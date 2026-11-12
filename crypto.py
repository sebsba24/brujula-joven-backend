"""
Cifrado simétrico de datos sensibles en reposo (Fernet / AES-128-CBC + HMAC).

Uso: el tipo de columna `EncryptedStr` cifra al guardar y descifra al leer,
de forma transparente para el resto de la aplicación.
"""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.types import TypeDecorator, Text

from config import get_settings

_settings = get_settings()


def _derive_fernet_key(raw: str) -> bytes:
    """Deriva una clave Fernet válida (32 bytes base64url) desde cualquier cadena.

    Así `ENCRYPTION_KEY` puede ser cualquier texto aleatorio y no es necesario
    generar un formato específico.
    """
    return base64.urlsafe_b64encode(hashlib.sha256(raw.encode("utf-8")).digest())


# Si ENCRYPTION_KEY no está definida, se deriva desde SECRET_KEY (válido en dev,
# pero en producción se debe configurar ENCRYPTION_KEY propio).
_key_source = _settings.encryption_key or _settings.secret_key
fernet = Fernet(_derive_fernet_key(_key_source))


def encrypt(value: str) -> str:
    return fernet.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode("utf-8")).decode("utf-8")


class EncryptedStr(TypeDecorator):
    """Columna de texto cifrada en reposo.

    - Al escribir: cifra el valor (texto plano → ciphertext).
    - Al leer: descifra. Si el valor aún está en texto plano (datos previos a la
      migración), lo devuelve tal cual para no romper la app durante la transición.
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return encrypt(str(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return decrypt(value)
        except (InvalidToken, ValueError):
            # Valor heredado sin cifrar: se devuelve sin cambios.
            return value

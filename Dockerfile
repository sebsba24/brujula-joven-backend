# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install uv for faster package management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --no-cache -r pyproject.toml

# Production stage
FROM python:3.12-slim as production

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# Railway inyecta el puerto en $PORT; 8000 es el valor por defecto en local
ENV PORT=8000
EXPOSE 8000

# Health check (urllib de la stdlib — la imagen slim no trae curl)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://localhost:'+os.environ.get('PORT','8000')+'/health')" || exit 1

# Run the application (forma shell para que ${PORT} se expanda)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}

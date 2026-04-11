#!/bin/bash

# ===========================================
# Azure Container Apps Deployment Script
# ===========================================

# Configuration - Update these variables
RESOURCE_GROUP="brujula-api-rg"
LOCATION="eastus"
CONTAINER_APP_ENV="brujula-api-env"
CONTAINER_APP_NAME="brujula-api"
ACR_NAME="brujulaapiacr"
IMAGE_NAME="brujula-api"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Azure Container Apps Deployment ===${NC}"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Login to Azure (interactive)
echo -e "${YELLOW}Logging in to Azure...${NC}"
az login

# Create Resource Group
echo -e "${YELLOW}Creating Resource Group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo -e "${YELLOW}Creating Azure Container Registry...${NC}"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)

# Build and push Docker image
echo -e "${YELLOW}Building and pushing Docker image...${NC}"
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:latest \
    --file Dockerfile \
    .

# Create Container Apps Environment
echo -e "${YELLOW}Creating Container Apps Environment...${NC}"
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Deploy Container App
echo -e "${YELLOW}Deploying Container App...${NC}"
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image $ACR_LOGIN_SERVER/$IMAGE_NAME:latest \
    --target-port 8000 \
    --ingress external \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --env-vars DATABASE_URL=secretref:database-url \
    --min-replicas 1 \
    --max-replicas 5 \
    --cpu 0.5 \
    --memory 1.0Gi

# Get the application URL
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" \
    --output tsv)

echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "${GREEN}Application URL: https://$APP_URL${NC}"
echo -e "${GREEN}API Documentation: https://$APP_URL/docs${NC}"
echo ""
echo -e "${YELLOW}Note: Remember to set the DATABASE_URL secret:${NC}"
echo -e "az containerapp secret set --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --secrets database-url='your-connection-string'"

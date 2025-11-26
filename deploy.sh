#!/bin/bash

# Azure deployment script for Streamlit Quiz App
# Make sure you're logged in: az login

set -e

# Configuration
RESOURCE_GROUP="quiz-app-rg"
LOCATION="francecentral"
APP_SERVICE_PLAN="quiz-app-plan"
WEB_APP_NAME="quiz-ai-agent-helper"
RUNTIME="PYTHON:3.10"
SKU="B1"  # Basic tier for student subscription

echo "🚀 Starting deployment of Quiz AI Agent to Azure..."

# Create resource group
echo "📦 Creating resource group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Register Microsoft.Web namespace if not already registered
echo "🔧 Registering Microsoft.Web namespace..."
az provider register --namespace Microsoft.Web

# Wait for registration
echo "⏳ Waiting for namespace registration..."
while [ "$(az provider show --namespace Microsoft.Web --query 'registrationState' -o tsv)" != "Registered" ]; do
  echo "   Still registering..."
  sleep 10
done
echo "✅ Microsoft.Web namespace registered"

# Create App Service Plan (B1 tier)
echo "📋 Creating App Service Plan (B1)..."
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku $SKU \
  --is-linux \
  --location $LOCATION

# Create Web App
echo "🌐 Creating Web App..."
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --name $WEB_APP_NAME \
  --runtime $RUNTIME

# Configure environment variables
echo "⚙️  Configuring environment variables..."
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings \
    MONGO_URI="mongodb+srv://<username>:<password>@<hostname>/<database>?retryWrites=true&w=majority" \
    GEMINI_API_KEY=<key> \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    WEBSITES_PORT="8501" \
    PORT="8501"

# Configure startup command
echo "🔧 Configuring startup command..."
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --startup-file "startup.sh"

# Deploy the app
echo "📤 Deploying application..."
az webapp up \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --runtime $RUNTIME \
  --sku $SKU \
  --location $LOCATION

echo "✅ Deployment complete!"
echo "🌍 Your app is available at: https://$WEB_APP_NAME.azurewebsites.net"
echo ""
echo "📋 Next steps:"
echo "1. Update GEMINI_API_KEY in Azure Portal or run:"
echo "   az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --settings GEMINI_API_KEY='your-key'"
echo ""
echo "2. View logs:"
echo "   az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
echo ""
echo "3. Check deployment status:"
echo "   az webapp deployment list --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --output table"

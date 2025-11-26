#!/bin/bash

# Quick update and redeploy script
# Use this after making changes to your app

set -e

RESOURCE_GROUP="quiz-app-rg"
WEB_APP_NAME="quiz-ai-agent-helper"

echo "🔄 Updating Quiz AI Agent..."

# Deploy using the new az webapp deploy command (zip deployment)
echo "📦 Creating deployment package..."
zip -r deploy.zip . -x "*.git*" "*__pycache__*" "*.pyc" "*.md" ".venv/*" "node_modules/*" "*.log"

echo "📤 Uploading to Azure..."
az webapp deploy \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --src-path deploy.zip \
  --type zip \
  --async true

# Clean up
rm deploy.zip

echo "✅ Update initiated!"
echo "🌍 App URL: https://$WEB_APP_NAME.azurewebsites.net"
echo ""
echo "📋 View logs:"
echo "   az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
echo ""
echo "🔍 Check deployment status:"
echo "   az webapp deployment list --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --output table"

#!/bin/bash

# Check deployment status and health

RESOURCE_GROUP="quiz-app-rg"
WEB_APP_NAME="quiz-ai-agent-helper"

echo "🔍 Checking Quiz AI Agent deployment status..."
echo ""

# Check if resource group exists
echo "📦 Resource Group Status:"
if az group exists --name $RESOURCE_GROUP | grep -q "true"; then
    echo "   ✅ Resource group exists"
else
    echo "   ❌ Resource group not found"
    exit 1
fi
echo ""

# Check app status
echo "🌐 Web App Status:"
APP_STATE=$(az webapp show --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --query state -o tsv 2>/dev/null)
if [ -n "$APP_STATE" ]; then
    echo "   State: $APP_STATE"
else
    echo "   ❌ Web app not found"
    exit 1
fi
echo ""

# Check app URL
echo "🔗 App URL:"
APP_URL=$(az webapp show --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --query defaultHostName -o tsv 2>/dev/null)
echo "   https://$APP_URL"
echo ""

# Check environment variables
echo "⚙️  Environment Variables:"
SETTINGS=$(az webapp config appsettings list --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME -o table 2>/dev/null)
echo "$SETTINGS" | grep -E "MONGO_URI|GEMINI_API_KEY|WEBSITES_PORT" || echo "   ⚠️  Some variables may be missing"
echo ""

# Check recent deployments
echo "📋 Recent Deployments:"
az webapp deployment list --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --output table 2>/dev/null || echo "   No deployments found"
echo ""

# Test app health
echo "🏥 Health Check:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://$APP_URL 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ App is responding (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "   ⏳ App may still be starting..."
else
    echo "   ⚠️  App returned HTTP $HTTP_CODE"
fi
echo ""

echo "📝 Quick Commands:"
echo "   View logs:    az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
echo "   Restart app:  az webapp restart --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
echo "   Update app:   ./update.sh"

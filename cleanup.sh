#!/bin/bash

# Delete Azure resources for Quiz AI Agent

set -e

RESOURCE_GROUP="quiz-app-rg"

echo "⚠️  WARNING: This will delete all resources in $RESOURCE_GROUP"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Deletion cancelled"
    exit 0
fi

echo "🗑️  Deleting resource group: $RESOURCE_GROUP..."
az group delete \
  --name $RESOURCE_GROUP \
  --yes \
  --no-wait

echo "✅ Deletion initiated (running in background)"
echo "📋 Check status:"
echo "   az group exists --name $RESOURCE_GROUP"

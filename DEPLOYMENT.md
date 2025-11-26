# Azure Deployment Guide

## 🚀 Deploying Quiz AI Agent to Azure App Service (B1)

### Prerequisites
- Azure CLI installed: `az --version`
- Logged in to Azure: `az login`
- Active Azure student subscription

### 📋 Quick Start

#### 1. First Time Deployment
```bash
# Make sure you're in the project directory
cd /home/uni2grow/workspace/csso/quiz-ai-agent

# Run the deployment script
./deploy.sh
```

**Important:** Update your GEMINI_API_KEY after deployment:
```bash
az webapp config appsettings set \
  --resource-group quiz-app-rg \
  --name quiz-ai-agent-tsognong \
  --settings GEMINI_API_KEY='your-actual-api-key-here'
```

#### 2. Update Existing Deployment
```bash
# After making code changes, quickly redeploy:
./update.sh
```

#### 3. View Logs
```bash
az webapp log tail \
  --resource-group quiz-app-rg \
  --name quiz-ai-agent-tsognong
```

#### 4. Delete Resources
```bash
./cleanup.sh
```

### 🔧 Manual Configuration

If you need to update settings manually:

**Update MongoDB URI:**
```bash
az webapp config appsettings set \
  --resource-group quiz-app-rg \
  --name quiz-ai-agent-tsognong \
  --settings MONGO_URI='your-mongodb-uri'
```

**Restart the app:**
```bash
az webapp restart \
  --resource-group quiz-app-rg \
  --name quiz-ai-agent-tsognong
```

### 📊 Monitoring

**Check app status:**
```bash
az webapp show \
  --resource-group quiz-app-rg \
  --name quiz-ai-agent-tsognong \
  --query state
```

**View deployment history:**
```bash
az webapp deployment list \
  --resource-group quiz-app-rg \
  --name quiz-ai-agent-tsognong \
  --output table
```

**Stream logs in real-time:**
```bash
az webapp log tail \
  --resource-group quiz-app-rg \
  --name quiz-ai-agent-tsognong
```

### 🌐 Access Your App

After deployment, your app will be available at:
**https://quiz-ai-agent-tsognong.azurewebsites.net**

### 💰 Cost Management (B1 Tier)

- **B1 (Basic)**: ~$13/month (~€12/month)
- Included in Azure for Students ($100 credit)
- 1 core, 1.75 GB RAM
- Custom domains and SSL

To check your costs:
```bash
az consumption usage list --output table
```

### 🔐 Environment Variables

The deployment automatically sets:
- `MONGO_URI`: MongoDB Atlas connection string
- `GEMINI_API_KEY`: Google Gemini API key (you need to set this)
- `WEBSITES_PORT`: 8501 (Streamlit default)
- `PORT`: 8501

### 🐛 Troubleshooting

**App not starting?**
1. Check logs: `az webapp log tail --resource-group quiz-app-rg --name quiz-ai-agent-tsognong`
2. Verify environment variables are set
3. Ensure startup.sh is executable

**Deployment failed?**
1. Check if namespace is registered: `az provider show --namespace Microsoft.Web`
2. Verify resource group exists: `az group exists --name quiz-app-rg`
3. Check quota limits: `az vm list-usage --location francecentral --output table`

**Port issues?**
- Streamlit uses port 8501 by default
- Azure expects the app to listen on the port specified in `WEBSITES_PORT`
- Make sure both are set to 8501

### 📝 Files Structure

```
quiz-ai-agent/
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
├── startup.sh            # Azure startup script
├── deploy.sh             # Initial deployment script
├── update.sh             # Quick update script
├── cleanup.sh            # Resource cleanup script
├── .deployment           # Deployment configuration
└── DEPLOYMENT.md         # This file
```

### 🔄 CI/CD (Optional)

For automated deployments, you can set up GitHub Actions:

```yaml
# .github/workflows/azure-deploy.yml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v2
        with:
          app-name: quiz-ai-agent-tsognong
          package: .
```

### 📞 Support

- Azure CLI docs: https://docs.microsoft.com/cli/azure/
- App Service docs: https://docs.microsoft.com/azure/app-service/
- Streamlit on Azure: https://docs.streamlit.io/knowledge-base/tutorials/deploy/azure

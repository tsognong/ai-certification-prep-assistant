# 🚀 Azure Deployment Quick Reference

## One-Time Setup (First Deployment)

```bash
# 1. Login to Azure
az login

# 2. Deploy the app
./deploy.sh

# 3. Set your Gemini API key (IMPORTANT!)
az webapp config appsettings set \
  --resource-group quiz-app-rg \
  --name quiz-ai-agent-tsognong \
  --settings GEMINI_API_KEY='YOUR_ACTUAL_KEY_HERE'
```

## Daily Operations

```bash
# Update app after code changes
./update.sh

# Check deployment status
./status.sh

# View live logs
az webapp log tail --resource-group quiz-app-rg --name quiz-ai-agent-tsognong

# Restart app
az webapp restart --resource-group quiz-app-rg --name quiz-ai-agent-tsognong
```

## Your App URL
**https://quiz-ai-agent-tsognong.azurewebsites.net**

## Cleanup (Delete Everything)
```bash
./cleanup.sh
```

## Costs
- **B1 Tier**: ~€12/month
- Covered by Azure for Students ($100 credit)

## Troubleshooting

**App not working?**
1. `./status.sh` - Check status
2. `az webapp log tail --resource-group quiz-app-rg --name quiz-ai-agent-tsognong` - View logs
3. Verify GEMINI_API_KEY is set

**Need to update environment variables?**
```bash
az webapp config appsettings set \
  --resource-group quiz-app-rg \
  --name quiz-ai-agent-tsognong \
  --settings KEY='value'
```

## Files
- `deploy.sh` - Initial deployment
- `update.sh` - Quick updates
- `status.sh` - Check status
- `cleanup.sh` - Delete resources
- `startup.sh` - App startup script
- `DEPLOYMENT.md` - Full documentation

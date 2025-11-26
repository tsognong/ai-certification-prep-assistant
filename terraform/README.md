# Terraform Infrastructure

Azure infrastructure for AI Certification Prep Assistant using App Service.

## Quick Start

1. **Install Terraform**
   ```bash
   # macOS
   brew install terraform
   
   # Ubuntu/Debian
   wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
   echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
   sudo apt update && sudo apt install terraform
   ```

2. **Configure Azure CLI**
   ```bash
   az login
   az account set --subscription "your-subscription-id"
   ```

3. **Set Variables**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

4. **Deploy**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

5. **Get Output**
   ```bash
   terraform output web_app_url
   ```

## Resources Created

- **Resource Group**: Container for all resources
- **App Service Plan**: B1 tier (Linux)
- **Web App**: Python 3.12 + Streamlit

## Cost Estimate

- **B1 tier**: ~€13/month (~$14/month)
- **F1 tier** (free): Change `sku_name = "F1"` in terraform.tfvars (limited features)

## Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `environment` | Environment name | `production` |
| `location` | Azure region | `francecentral` |
| `web_app_name` | App name (globally unique) | `quiz-ai-agent-helper` |
| `sku_name` | Pricing tier | `B1` |
| `python_version` | Python version | `3.12` |
| `mongo_uri` | MongoDB connection string | (required) |
| `gemini_api_key` | Google Gemini API key | (required) |
| `google_client_id` | OAuth client ID | (required) |
| `google_client_secret` | OAuth client secret | (required) |

## Outputs

- `web_app_url`: Application URL
- `resource_group_name`: Resource group name
- `deployment_summary`: Full deployment info

## Cleanup

```bash
terraform destroy
```

## Security Notes

- Never commit `terraform.tfvars` (already in `.gitignore`)
- Use Azure Key Vault for production secrets
- Terraform state contains sensitive data - use remote backend with encryption

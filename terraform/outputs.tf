# Outputs

# Resource Group
output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "resource_group_id" {
  description = "Resource group ID"
  value       = azurerm_resource_group.main.id
}

output "location" {
  description = "Deployment location"
  value       = azurerm_resource_group.main.location
}

# App Service
output "app_service_plan_id" {
  description = "App Service plan ID"
  value       = azurerm_service_plan.main.id
}

output "app_service_plan_sku" {
  description = "App Service plan pricing tier"
  value       = azurerm_service_plan.main.sku_name
}

# Web App
output "web_app_id" {
  description = "Web app ID"
  value       = azurerm_linux_web_app.main.id
}

output "web_app_name" {
  description = "Web app name"
  value       = azurerm_linux_web_app.main.name
}

output "web_app_url" {
  description = "Web app URL"
  value       = "https://${azurerm_linux_web_app.main.default_hostname}"
}

output "web_app_default_hostname" {
  description = "Web app default hostname"
  value       = azurerm_linux_web_app.main.default_hostname
}

# Deployment Info
output "deployment_summary" {
  description = "Deployment summary"
  value = {
    app_url       = "https://${azurerm_linux_web_app.main.default_hostname}"
    resource_group = azurerm_resource_group.main.name
    location      = azurerm_resource_group.main.location
    sku           = azurerm_service_plan.main.sku_name
    python_version = var.python_version
  }
}

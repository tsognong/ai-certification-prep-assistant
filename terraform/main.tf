# Azure Infrastructure for AI Certification Prep Assistant

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Common tags for all resources
locals {
  common_tags = {
    Environment = var.environment
    Project     = "AI Certification Prep Assistant"
    ManagedBy   = "Terraform"
  }
}

# Read current Azure subscription
data "azurerm_client_config" "current" {}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.common_tags
}

# App Service Plan
resource "azurerm_service_plan" "main" {
  name                = var.app_service_plan_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = var.sku_name
  tags                = local.common_tags
}

# Web App
resource "azurerm_linux_web_app" "main" {
  name                = var.web_app_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = true
  
  app_settings = {
    "MONGO_URI"                      = var.mongo_uri
    "GEMINI_API_KEY"                 = var.gemini_api_key
    "GOOGLE_CLIENT_ID"               = var.google_client_id
    "GOOGLE_CLIENT_SECRET"           = var.google_client_secret
    "GOOGLE_REDIRECT_URI"            = "https://${var.web_app_name}.azurewebsites.net"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "WEBSITES_PORT"                  = "8501"
    "PORT"                           = "8501"
    "ENVIRONMENT"                    = var.environment
  }
  
  site_config {
    application_stack {
      python_version = var.python_version
    }
    app_command_line = var.startup_command
    always_on        = var.always_on
  }
  
  tags = merge(
    local.common_tags,
    {
      AppType = "Streamlit"
      Runtime = "Python ${var.python_version}"
    }
  )
}

# Input Variables

# General
variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be: dev, staging, or production"
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "cert-prep-assistant"
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Name must contain only lowercase letters, numbers, and hyphens"
  }
}

variable "location" {
  description = "Azure region (e.g., francecentral, westeurope, eastus)"
  type        = string
  default     = "francecentral"
}

# Resources
variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
  default     = "cert-prep-rg"
}

variable "app_service_plan_name" {
  description = "App Service plan name"
  type        = string
  default     = "cert-prep-plan"
}

variable "web_app_name" {
  description = "Web app name (globally unique, becomes: https://<name>.azurewebsites.net)"
  type        = string
  default     = "cert-prep-assistant"
  
  validation {
    condition     = can(regex("^[a-z0-9-]{3,60}$", var.web_app_name))
    error_message = "Name must be 3-60 characters: lowercase, numbers, and hyphens only"
  }
}

# Configuration
variable "sku_name" {
  description = "App Service pricing tier (F1=Free, B1=Basic, S1=Standard, P1V2=Premium)"
  type        = string
  default     = "B1"
  
  validation {
    condition     = contains(["F1", "B1", "B2", "B3", "S1", "S2", "S3", "P1V2", "P2V2", "P3V2"], var.sku_name)
    error_message = "Invalid SKU. Valid options: F1, B1, B2, B3, S1, S2, S3, P1V2, P2V2, P3V2"
  }
}

variable "python_version" {
  description = "Python version"
  type        = string
  default     = "3.12"
  
  validation {
    condition     = contains(["3.10", "3.11", "3.12", "3.13"], var.python_version)
    error_message = "Supported Python versions: 3.10, 3.11, 3.12, 3.13"
  }
}

variable "startup_command" {
  description = "Application startup command"
  type        = string
  default     = "python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0"
}

variable "always_on" {
  description = "Keep app always running (prevents cold starts, not available on F1 tier)"
  type        = bool
  default     = true
}

# Sensitive Variables
variable "mongo_uri" {
  description = "MongoDB connection URI (format: mongodb+srv://user:password@cluster.mongodb.net/database)"
  type        = string
  sensitive   = true
  
  validation {
    condition     = can(regex("^mongodb(\\+srv)?://", var.mongo_uri))
    error_message = "URI must start with mongodb:// or mongodb+srv://"
  }
}

variable "gemini_api_key" {
  description = "Google Gemini API key (get from https://makersuite.google.com/app/apikey)"
  type        = string
  sensitive   = true
  
  validation {
    condition     = length(var.gemini_api_key) > 20
    error_message = "Invalid API key (too short)"
  }
}

variable "google_client_id" {
  description = "Google OAuth client ID"
  type        = string
  sensitive   = true
}

variable "google_client_secret" {
  description = "Google OAuth client secret"
  type        = string
  sensitive   = true
}

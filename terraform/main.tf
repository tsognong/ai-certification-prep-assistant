# ============================================
# FICHIER PRINCIPAL TERRAFORM
# Ce fichier définit TOUTES les ressources Azure
# ============================================

# 📚 CONCEPT : Configuration Terraform
# - required_version : Version minimale de Terraform
# - required_providers : Plugins nécessaires
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"  # Fournisseur Azure
      version = "~> 3.0"             # Version 3.x (compatible)
    }
  }
  
  # 📚 CONCEPT : Backend (Stockage de l'état)
  # Par défaut : backend "local" (fichier terraform.tfstate local)
  # Pour la production : utiliser un backend distant
  #
  # backend "azurerm" {
  #   resource_group_name  = "terraform-state-rg"
  #   storage_account_name = "tfstate12345"
  #   container_name       = "tfstate"
  #   key                  = "quiz-app.terraform.tfstate"
  # }
}

# ============================================
# PROVIDER AZURE
# ============================================

# 📚 CONCEPT : Provider
# Un provider est un plugin qui permet à Terraform de communiquer
# avec une API (ici Azure)
provider "azurerm" {
  # features {} est requis pour azurerm provider
  features {
    # Options pour gérer le comportement du provider
    resource_group {
      # Empêche la suppression de RG avec des ressources
      prevent_deletion_if_contains_resources = false
    }
  }
  
  # Optionnel : Configuration explicite
  # subscription_id = var.subscription_id
  # tenant_id       = var.tenant_id
}

# ============================================
# LOCALS (Variables calculées)
# ============================================

# 📚 CONCEPT : Locals
# Variables calculées localement (pas d'input utilisateur)
# Utiles pour : calculs, conditions, répétition de valeurs
locals {
  # Tags communs pour toutes les ressources
  common_tags = {
    Environnement = var.environment
    Projet        = "Quiz AI Agent"
    GerePar       = "Terraform"
    DateCreation  = timestamp()
  }
  
  # Nom complet de l'application (convention de nommage)
  full_app_name = "${var.project_name}-${var.environment}"
  
  # Calcul du SKU basé sur l'environnement
  # 📚 CONCEPT : Expression conditionnelle (ternaire)
  # syntaxe : condition ? valeur_si_vrai : valeur_si_faux
  computed_sku = var.environment == "production" ? "S1" : "B1"
}

# ============================================
# DATA SOURCES (Lecture de données existantes)
# ============================================

# 📚 CONCEPT : Data Source
# Permet de LIRE des informations (ne crée rien)
# Différence avec resource : data = lecture, resource = création/gestion

# Exemple : Lire la subscription Azure actuelle
data "azurerm_client_config" "current" {}

# Exemple : Lire un Key Vault existant (pour les secrets)
# data "azurerm_key_vault" "existing" {
#   name                = "mon-keyvault"
#   resource_group_name = "mon-rg-existant"
# }

# ============================================
# RESOURCE GROUP (Groupe de Ressources)
# ============================================

# 📚 CONCEPT : Resource
# syntaxe : resource "TYPE" "NOM_LOCAL" { arguments }
# - TYPE : Type de ressource du provider (azurerm_resource_group)
# - NOM_LOCAL : Nom pour référencer dans Terraform (quiz_app_rg)
# - Arguments : Configuration de la ressource (name, location, etc.)
resource "azurerm_resource_group" "quiz_app_rg" {
  name     = var.resource_group_name
  location = var.location
  
  # 📚 CONCEPT : Tags
  # Métadonnées pour organiser et gérer les ressources
  tags = local.common_tags
  
  # 📚 CONCEPT : Lifecycle
  # Contrôle le cycle de vie de la ressource
  lifecycle {
    # Empêche la suppression accidentelle
    # prevent_destroy = true
    
    # Crée la nouvelle avant de détruire l'ancienne (zéro downtime)
    # create_before_destroy = true
    
    # Ignore les changements faits en dehors de Terraform
    # ignore_changes = [tags["DateCreation"]]
  }
}

# ============================================
# APP SERVICE PLAN
# ============================================

# 📚 CONCEPT : Référencement de ressource
# azurerm_resource_group.quiz_app_rg.name référence le nom du RG créé ci-dessus
# Crée automatiquement une DÉPENDANCE IMPLICITE : RG sera créé avant le plan
resource "azurerm_service_plan" "quiz_app_plan" {
  name                = var.app_service_plan_name
  location            = azurerm_resource_group.quiz_app_rg.location
  resource_group_name = azurerm_resource_group.quiz_app_rg.name
  
  os_type  = "Linux"
  sku_name = var.sku_name
  
  tags = local.common_tags
}

# ============================================
# WEB APP (Application)
# ============================================

# 📚 CONCEPT : Dépendances multiples
# Cette ressource dépend de :
# 1. azurerm_resource_group.quiz_app_rg (via resource_group_name)
# 2. azurerm_service_plan.quiz_app_plan (via service_plan_id)
# Terraform calcule automatiquement l'ordre de création
resource "azurerm_linux_web_app" "quiz_app" {
  name                = var.web_app_name
  location            = azurerm_resource_group.quiz_app_rg.location
  resource_group_name = azurerm_resource_group.quiz_app_rg.name
  service_plan_id     = azurerm_service_plan.quiz_app_plan.id
  
  # 📚 CONCEPT : app_settings
  # Variables d'environnement de l'application
  # 📚 ATTENTION : Les secrets ici sont visibles dans le state !
  # Pour la production : utiliser Azure Key Vault + références
  app_settings = {
    "MONGO_URI"                      = var.mongo_uri
    "GEMINI_API_KEY"                 = var.gemini_api_key
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "WEBSITES_PORT"                  = "8501"
    "PORT"                           = "8501"
    
    # 📚 ASTUCE : Variables calculées
    "ENVIRONMENT" = var.environment
    "APP_VERSION" = var.app_version
  }
  
  # 📚 CONCEPT : Bloc imbriqué (nested block)
  site_config {
    # 📚 CONCEPT : Bloc dans un bloc
    application_stack {
      python_version = var.python_version
    }
    
    app_command_line = var.startup_command
    always_on        = var.always_on
    
    # 📚 EXEMPLE : CORS (si besoin)
    # cors {
    #   allowed_origins = ["https://example.com"]
    # }
  }
  
  https_only = true
  
  tags = merge(
    local.common_tags,
    {
      AppType = "Streamlit"
      Runtime = "Python ${var.python_version}"
    }
  )
  
  # 📚 CONCEPT : Dépendance explicite
  # Si nécessaire, forcer une dépendance non détectée automatiquement
  # depends_on = [
  #   azurerm_resource_group.quiz_app_rg
  # ]
}

# ============================================
# EXEMPLES AVANCÉS (Commentés)
# ============================================

# 📚 CONCEPT : Application Insights (Monitoring)
# resource "azurerm_application_insights" "quiz_app_insights" {
#   name                = "${var.project_name}-insights"
#   location            = azurerm_resource_group.quiz_app_rg.location
#   resource_group_name = azurerm_resource_group.quiz_app_rg.name
#   application_type    = "web"
#   
#   tags = local.common_tags
# }

# 📚 CONCEPT : Storage Account (pour fichiers statiques)
# resource "azurerm_storage_account" "quiz_storage" {
#   name                     = "${var.project_name}storage"
#   resource_group_name      = azurerm_resource_group.quiz_app_rg.name
#   location                 = azurerm_resource_group.quiz_app_rg.location
#   account_tier             = "Standard"
#   account_replication_type = "LRS"
#   
#   tags = local.common_tags
# }

# 📚 CONCEPT : Custom Domain (domaine personnalisé)
# resource "azurerm_app_service_custom_hostname_binding" "quiz_domain" {
#   hostname            = "quiz.example.com"
#   app_service_name    = azurerm_linux_web_app.quiz_app.name
#   resource_group_name = azurerm_resource_group.quiz_app_rg.name
# }

# 📚 CONCEPT : Count (créer N copies)
# Crée 3 storage accounts
# resource "azurerm_storage_account" "storage" {
#   count = 3
#   
#   name                = "${var.project_name}storage${count.index}"
#   resource_group_name = azurerm_resource_group.quiz_app_rg.name
#   location            = azurerm_resource_group.quiz_app_rg.location
#   # ...
# }

# 📚 CONCEPT : for_each (créer depuis un map/set)
# Préféré à count car plus stable
# variable "storage_accounts" {
#   type = map(object({
#     tier = string
#     replication = string
#   }))
#   default = {
#     "dev" = {
#       tier = "Standard"
#       replication = "LRS"
#     }
#     "prod" = {
#       tier = "Premium"
#       replication = "GRS"
#     }
#   }
# }
#
# resource "azurerm_storage_account" "storage" {
#   for_each = var.storage_accounts
#   
#   name                     = "${var.project_name}${each.key}"
#   account_tier             = each.value.tier
#   account_replication_type = each.value.replication
#   # ...
# }

# ============================================
# NOTES SUR LES BONNES PRATIQUES
# ============================================

# 1. 📌 NOMMAGE
#    - Ressources : snake_case (quiz_app_rg)
#    - Variables : snake_case (resource_group_name)
#    - Noms Azure : kebab-case (quiz-app-rg)

# 2. 📌 ORGANISATION
#    - Petits projets : 1 fichier main.tf
#    - Moyens projets : main.tf, variables.tf, outputs.tf
#    - Grands projets : Modules séparés

# 3. 📌 SÉCURITÉ
#    - Secrets : variables sensitive = true
#    - State : Backend distant + chiffrement
#    - .gitignore : terraform.tfvars, *.tfstate

# 4. 📌 VERSIONNEMENT
#    - Provider version : ~> 3.0 (compatible 3.x)
#    - Terraform version : >= 1.0

# 5. 📌 DOCUMENTATION
#    - Commentaires explicatifs
#    - README.md avec instructions
#    - Description dans variables et outputs

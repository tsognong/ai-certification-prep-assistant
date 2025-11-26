# ============================================
# VARIABLES D'ENTRÉE
# Valeurs configurables pour rendre le code réutilisable
# ============================================

# 📚 CONCEPT : Variable
# Une variable permet de paramétrer votre infrastructure
# Structure :
# variable "nom" {
#   description = "Description claire"
#   type        = type_de_donnée
#   default     = valeur_par_défaut (optionnel)
#   sensitive   = true/false
#   validation  = règle de validation
# }

# ============================================
# VARIABLES GÉNÉRALES
# ============================================

variable "environment" {
  description = "Nom de l'environnement (dev, staging, production)"
  type        = string
  default     = "production"
  
  # 📚 CONCEPT : Validation
  # Valide la valeur fournie par l'utilisateur
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "L'environnement doit être : dev, staging ou production"
  }
}

variable "project_name" {
  description = "Nom du projet (utilisé pour le nommage des ressources)"
  type        = string
  default     = "quiz-ai-agent"
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Le nom doit contenir uniquement des minuscules, chiffres et tirets"
  }
}

variable "location" {
  description = <<-EOT
    Région Azure où déployer les ressources.
    Régions populaires en Europe :
    - francecentral : France (Paris)
    - westeurope : Pays-Bas (Amsterdam)
    - northeurope : Irlande (Dublin)
  EOT
  type        = string
  default     = "francecentral"
}

# ============================================
# VARIABLES DE RESSOURCES
# ============================================

variable "resource_group_name" {
  description = "Nom du groupe de ressources Azure"
  type        = string
  default     = "quiz-app-rg"
}

variable "app_service_plan_name" {
  description = "Nom du plan App Service"
  type        = string
  default     = "quiz-app-plan"
}

variable "web_app_name" {
  description = <<-EOT
    Nom de l'application web (DOIT être unique globalement).
    Format : minuscules, chiffres et tirets uniquement.
    Exemple : quiz-ai-agent-helper
    ⚠️ Ce nom devient votre URL : https://<nom>.azurewebsites.net
  EOT
  type        = string
  default     = "quiz-ai-agent-helper"
  
  # 📚 CONCEPT : Validation avec regex
  validation {
    condition     = can(regex("^[a-z0-9-]{3,60}$", var.web_app_name))
    error_message = "Le nom doit : être entre 3-60 caractères, minuscules, chiffres et tirets uniquement"
  }
}

# ============================================
# VARIABLES DE CONFIGURATION
# ============================================

# 📚 CONCEPT : Types de variables
# string, number, bool, list, map, object, set, tuple, any

variable "sku_name" {
  description = <<-EOT
    Niveau tarifaire du plan App Service.
    Options courantes :
    - F1  : Gratuit (limité, pas de domaine custom, pas always-on)
    - B1  : Basique (~13€/mois, 1 core, 1.75GB RAM, bon pour dev)
    - B2  : Basique (~26€/mois, 2 cores, 3.5GB RAM)
    - S1  : Standard (~70€/mois, 1 core, 1.75GB RAM, slots de déploiement)
    - P1V2: Premium (~85€/mois, 1 core, 3.5GB RAM, meilleures perfs)
  EOT
  type        = string
  default     = "B1"
  
  validation {
    condition     = contains(["F1", "B1", "B2", "B3", "S1", "S2", "S3", "P1V2", "P2V2", "P3V2"], var.sku_name)
    error_message = "SKU invalide. Consultez la description pour les options valides"
  }
}

variable "python_version" {
  description = "Version de Python pour l'application"
  type        = string
  default     = "3.10"
  
  validation {
    condition     = contains(["3.8", "3.9", "3.10", "3.11"], var.python_version)
    error_message = "Versions Python supportées : 3.8, 3.9, 3.10, 3.11"
  }
}

variable "startup_command" {
  description = "Commande de démarrage de l'application"
  type        = string
  default     = "startup.sh"
}

variable "always_on" {
  description = <<-EOT
    Maintient l'application toujours active (pas de mise en veille).
    - true  : Recommandé pour production (évite les démarrages froids)
    - false : OK pour dev/test (économise des ressources)
    ⚠️ Non disponible sur le tier gratuit (F1)
  EOT
  type        = bool
  default     = true
}

variable "app_version" {
  description = "Version de l'application (pour tracking)"
  type        = string
  default     = "1.0.0"
}

# ============================================
# VARIABLES SENSIBLES (Secrets)
# ============================================

# 📚 CONCEPT : sensitive = true
# - Masque la valeur dans les logs et outputs
# - Ne la protège PAS dans le state (utilisez un backend chiffré)
# - Utilisez Azure Key Vault pour une vraie protection

variable "mongo_uri" {
  description = <<-EOT
    URI de connexion MongoDB Atlas.
    Format : mongodb+srv://user:password@cluster.mongodb.net/database
    
    Comment l'obtenir :
    1. Allez sur MongoDB Atlas
    2. Clusters → Connect → Connect your application
    3. Copiez la connection string
    4. Remplacez <password> par votre mot de passe
  EOT
  type        = string
  sensitive   = true
  
  # 📚 ASTUCE : Pas de valeur par défaut pour les secrets
  # Force l'utilisateur à la fournir explicitement
  
  # 📚 CONCEPT : Validation complexe
  validation {
    condition     = can(regex("^mongodb(\\+srv)?://", var.mongo_uri))
    error_message = "L'URI doit commencer par mongodb:// ou mongodb+srv://"
  }
}

variable "gemini_api_key" {
  description = <<-EOT
    Clé API Google Gemini pour les fonctionnalités IA.
    
    Comment l'obtenir :
    1. Allez sur https://makersuite.google.com/app/apikey
    2. Créez un projet
    3. Créez une clé API
    4. Copiez la clé
  EOT
  type        = string
  sensitive   = true
  
  validation {
    condition     = length(var.gemini_api_key) > 20
    error_message = "La clé API semble invalide (trop courte)"
  }
}

# ============================================
# VARIABLES OPTIONNELLES/AVANCÉES
# ============================================

variable "tags" {
  description = "Tags supplémentaires à ajouter à toutes les ressources"
  type        = map(string)
  default     = {}
  
  # 📚 EXEMPLE d'utilisation :
  # tags = {
  #   CostCenter = "IT"
  #   Owner      = "TeamA"
  # }
}

variable "enable_monitoring" {
  description = "Active Application Insights pour le monitoring"
  type        = bool
  default     = false
}

variable "custom_domain" {
  description = "Domaine personnalisé (optionnel). Exemple : quiz.example.com"
  type        = string
  default     = null  # null = pas de domaine custom
}

# ============================================
# VARIABLES COMPLEXES (Types avancés)
# ============================================

# 📚 CONCEPT : Type list
variable "allowed_ip_addresses" {
  description = "Liste d'adresses IP autorisées à accéder à l'app"
  type        = list(string)
  default     = []  # Vide = pas de restriction
  
  # 📚 EXEMPLE :
  # allowed_ip_addresses = ["203.0.113.5", "198.51.100.20"]
}

# 📚 CONCEPT : Type map
variable "app_settings_extra" {
  description = "Variables d'environnement supplémentaires"
  type        = map(string)
  default     = {}
  
  # 📚 EXEMPLE :
  # app_settings_extra = {
  #   "CUSTOM_VAR" = "value"
  #   "DEBUG"      = "false"
  # }
}

# 📚 CONCEPT : Type object (structure complexe)
variable "backup_config" {
  description = "Configuration de sauvegarde"
  type = object({
    enabled   = bool
    frequency = string
    retention = number
  })
  default = {
    enabled   = false
    frequency = "daily"
    retention = 7
  }
  
  # 📚 EXEMPLE :
  # backup_config = {
  #   enabled   = true
  #   frequency = "daily"
  #   retention = 30
  # }
}

# ============================================
# NOTES SUR L'UTILISATION DES VARIABLES
# ============================================

# 📌 MÉTHODE 1 : Fichier terraform.tfvars
# Créez un fichier terraform.tfvars :
# environment = "production"
# web_app_name = "mon-app-unique"
# mongo_uri = "mongodb+srv://..."

# 📌 MÉTHODE 2 : Ligne de commande
# terraform apply -var="environment=dev" -var="web_app_name=test-app"

# 📌 MÉTHODE 3 : Variables d'environnement
# export TF_VAR_environment="dev"
# export TF_VAR_mongo_uri="mongodb+srv://..."
# terraform apply

# 📌 MÉTHODE 4 : Fichier .auto.tfvars
# Terraform charge automatiquement les fichiers *.auto.tfvars
# Créez dev.auto.tfvars, prod.auto.tfvars, etc.

# 📌 ORDRE DE PRIORITÉ (du plus au moins important)
# 1. -var ou -var-file en ligne de commande
# 2. *.auto.tfvars (alphabétique)
# 3. terraform.tfvars
# 4. TF_VAR_* variables d'environnement
# 5. Valeurs par défaut dans variables.tf

# ============================================
# QUESTIONS D'ENTRETIEN SUR LES VARIABLES
# ============================================

# Q1 : Quelle est la différence entre variable et local ?
# R  : variable = input (fourni par l'utilisateur)
#      local    = calculé (valeur dérivée/calculée)

# Q2 : Comment protéger un secret dans une variable ?
# R  : - Marquer sensitive = true
#      - Ne pas mettre de default
#      - Utiliser TF_VAR_* en environnement
#      - State dans backend chiffré
#      - Idéalement : Azure Key Vault

# Q3 : Peut-on avoir une variable sans valeur par défaut ?
# R  : Oui ! Terraform demandera la valeur ou échouera

# Q4 : Comment valider qu'un nombre est entre 1 et 100 ?
# R  : validation {
#        condition = var.nombre >= 1 && var.nombre <= 100
#        error_message = "Doit être entre 1 et 100"
#      }

# Q5 : Différence entre list et set ?
# R  : list = ordre important, doublons OK
#      set  = pas d'ordre, pas de doublons

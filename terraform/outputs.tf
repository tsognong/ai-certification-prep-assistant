# ============================================
# OUTPUTS (Sorties)
# Valeurs affichées après terraform apply
# ============================================

# 📚 CONCEPT : Output
# Un output affiche des valeurs après l'exécution
# Utilisations :
# 1. Afficher des infos importantes (URL, IP, etc.)
# 2. Partager des données entre modules
# 3. Utiliser dans des scripts : terraform output nom_output
# 4. CI/CD : récupérer des valeurs pour d'autres étapes

# ============================================
# OUTPUTS BASIQUES
# ============================================

output "resource_group_name" {
  description = "Nom du groupe de ressources créé"
  value       = azurerm_resource_group.quiz_app_rg.name
  
  # 📚 CONCEPT : Référencement
  # azurerm_resource_group.quiz_app_rg.name
  # └─ type de ressource ─┘ └─ nom local ─┘ └─ attribut ─┘
}

output "resource_group_id" {
  description = "ID complet du groupe de ressources"
  value       = azurerm_resource_group.quiz_app_rg.id
  
  # 📚 NOTE : Format de l'ID Azure
  # /subscriptions/{sub-id}/resourceGroups/{nom}
}

output "location" {
  description = "Région Azure où les ressources sont déployées"
  value       = azurerm_resource_group.quiz_app_rg.location
}

# ============================================
# OUTPUTS APP SERVICE
# ============================================

output "app_service_plan_id" {
  description = "ID du plan App Service"
  value       = azurerm_service_plan.quiz_app_plan.id
}

output "app_service_plan_sku" {
  description = "SKU (niveau tarifaire) du plan App Service"
  value       = azurerm_service_plan.quiz_app_plan.sku_name
}

output "web_app_name" {
  description = "Nom de l'application web"
  value       = azurerm_linux_web_app.quiz_app.name
}

output "web_app_id" {
  description = "ID complet de l'application web"
  value       = azurerm_linux_web_app.quiz_app.id
}

# ============================================
# OUTPUTS IMPORTANTS (URLs et connexion)
# ============================================

output "application_url" {
  description = "URL publique de l'application (cliquez pour accéder)"
  value       = "https://${azurerm_linux_web_app.quiz_app.default_hostname}"
  
  # 📚 CONCEPT : Interpolation de chaîne
  # ${...} permet d'insérer des valeurs dans une chaîne
}

output "default_hostname" {
  description = "Nom d'hôte par défaut (sans https://)"
  value       = azurerm_linux_web_app.quiz_app.default_hostname
}

# 📚 CONCEPT : Output conditionnel
output "custom_domain_url" {
  description = "URL du domaine personnalisé (si configuré)"
  value       = var.custom_domain != null ? "https://${var.custom_domain}" : "Non configuré"
  
  # Syntaxe ternaire : condition ? valeur_si_vrai : valeur_si_faux
}

# ============================================
# OUTPUTS TECHNIQUES
# ============================================

output "outbound_ip_addresses" {
  description = <<-EOT
    Adresses IP sortantes de l'application.
    Utilisez-les pour configurer les firewalls (MongoDB whitelist, etc.)
  EOT
  value       = azurerm_linux_web_app.quiz_app.outbound_ip_addresses
}

output "possible_outbound_ip_addresses" {
  description = "Toutes les IPs sortantes possibles (inclut les futures si scaling)"
  value       = azurerm_linux_web_app.quiz_app.possible_outbound_ip_addresses
}

output "app_service_plan_kind" {
  description = "Type de plan (Linux dans notre cas)"
  value       = azurerm_service_plan.quiz_app_plan.kind
}

# ============================================
# OUTPUTS SENSIBLES
# ============================================

# 📚 CONCEPT : Output sensible
# Les outputs sensibles sont masqués dans la console
# Mais ils restent visibles dans le state !
output "app_settings_summary" {
  description = "Résumé des variables d'environnement (sans secrets)"
  value = {
    PORT           = "8501"
    ENVIRONMENT    = var.environment
    PYTHON_VERSION = var.python_version
    ALWAYS_ON      = var.always_on
  }
}

# ⚠️ NE JAMAIS faire un output de secrets en production
# C'est seulement pour la démo/dev
# output "mongo_uri_debug" {
#   description = "URI MongoDB (DEBUG UNIQUEMENT - NE PAS UTILISER EN PROD)"
#   value       = var.mongo_uri
#   sensitive   = true
# }

# ============================================
# OUTPUTS POUR CI/CD
# ============================================

output "deployment_commands" {
  description = "Commandes pour déployer l'application"
  value = {
    zip_deploy = "az webapp deployment source config-zip --resource-group ${azurerm_resource_group.quiz_app_rg.name} --name ${azurerm_linux_web_app.quiz_app.name} --src deploy.zip"
    
    view_logs = "az webapp log tail --resource-group ${azurerm_resource_group.quiz_app_rg.name} --name ${azurerm_linux_web_app.quiz_app.name}"
    
    restart_app = "az webapp restart --resource-group ${azurerm_resource_group.quiz_app_rg.name} --name ${azurerm_linux_web_app.quiz_app.name}"
  }
}

# ============================================
# OUTPUT FORMATÉ (Instructions complètes)
# ============================================

output "next_steps" {
  description = "Instructions détaillées pour les prochaines étapes"
  value = <<-EOT
  
  ╔════════════════════════════════════════════════════════════╗
  ║  ✅ INFRASTRUCTURE CRÉÉE AVEC SUCCÈS !                    ║
  ╚════════════════════════════════════════════════════════════╝
  
  📋 INFORMATIONS PRINCIPALES
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  🌍 URL Application      : https://${azurerm_linux_web_app.quiz_app.default_hostname}
  📦 Groupe de Ressources : ${azurerm_resource_group.quiz_app_rg.name}
  🖥️  Application Web      : ${azurerm_linux_web_app.quiz_app.name}
  📍 Région               : ${azurerm_resource_group.quiz_app_rg.location}
  💰 Niveau Tarifaire     : ${azurerm_service_plan.quiz_app_plan.sku_name}
  
  📋 PROCHAINES ÉTAPES
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  1️⃣  DÉPLOYER VOTRE CODE
  
      cd ${path.cwd}
      zip -r deploy.zip . -x "*.git*" -x "*terraform*" -x "*__pycache__*"
      
      az webapp deployment source config-zip \
        --resource-group ${azurerm_resource_group.quiz_app_rg.name} \
        --name ${azurerm_linux_web_app.quiz_app.name} \
        --src deploy.zip
  
  2️⃣  VÉRIFIER LES LOGS
  
      az webapp log tail \
        --resource-group ${azurerm_resource_group.quiz_app_rg.name} \
        --name ${azurerm_linux_web_app.quiz_app.name}
  
  3️⃣  CONFIGURER MONGODB WHITELIST
  
      Ajoutez ces IPs dans MongoDB Atlas :
      ${azurerm_linux_web_app.quiz_app.outbound_ip_addresses}
  
  4️⃣  TESTER L'APPLICATION
  
      curl https://${azurerm_linux_web_app.quiz_app.default_hostname}
      # ou ouvrez dans le navigateur
  
  📚 COMMANDES UTILES
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  # Redémarrer l'app
  az webapp restart --resource-group ${azurerm_resource_group.quiz_app_rg.name} \
                    --name ${azurerm_linux_web_app.quiz_app.name}
  
  # Mettre à jour une variable d'environnement
  az webapp config appsettings set \
    --resource-group ${azurerm_resource_group.quiz_app_rg.name} \
    --name ${azurerm_linux_web_app.quiz_app.name} \
    --settings CLE=VALEUR
  
  # Voir toutes les variables
  az webapp config appsettings list \
    --resource-group ${azurerm_resource_group.quiz_app_rg.name} \
    --name ${azurerm_linux_web_app.quiz_app.name}
  
  # Accéder au portail Azure
  https://portal.azure.com/#@/resource${azurerm_resource_group.quiz_app_rg.id}
  
  🔧 GESTION TERRAFORM
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  # Voir l'état actuel
  terraform show
  
  # Voir un output spécifique
  terraform output application_url
  
  # Mettre à jour l'infrastructure
  terraform plan
  terraform apply
  
  # Détruire tout (ATTENTION !)
  terraform destroy
  
  ═══════════════════════════════════════════════════════════
  
  EOT
}

# ============================================
# OUTPUTS POUR MODULES (si utilisation future)
# ============================================

# 📚 CONCEPT : Outputs pour modules
# Si vous transformez ce code en module, ces outputs
# permettent au module appelant d'accéder aux valeurs

output "resource_group" {
  description = "Objet complet du groupe de ressources (pour modules)"
  value       = azurerm_resource_group.quiz_app_rg
  
  # 📚 NOTE : Exposer l'objet entier permet d'accéder à tous ses attributs
  # Exemple d'utilisation dans un module parent :
  # module.quiz_app.resource_group.name
  # module.quiz_app.resource_group.location
  # etc.
}

output "web_app" {
  description = "Objet complet de l'application web (pour modules)"
  value       = azurerm_linux_web_app.quiz_app
  sensitive   = true  # Peut contenir des infos sensibles
}

# ============================================
# OUTPUT JSON (pour automatisation)
# ============================================

output "infrastructure_json" {
  description = "Configuration complète en JSON (pour scripts/automation)"
  value = jsonencode({
    resource_group = {
      name     = azurerm_resource_group.quiz_app_rg.name
      location = azurerm_resource_group.quiz_app_rg.location
      id       = azurerm_resource_group.quiz_app_rg.id
    }
    app_service = {
      name     = azurerm_linux_web_app.quiz_app.name
      url      = "https://${azurerm_linux_web_app.quiz_app.default_hostname}"
      sku      = azurerm_service_plan.quiz_app_plan.sku_name
      location = azurerm_linux_web_app.quiz_app.location
    }
    metadata = {
      environment    = var.environment
      deployed_at    = timestamp()
      terraform_path = path.cwd
    }
  })
}

# 📚 UTILISATION dans un script :
# terraform output -json infrastructure_json | jq '.app_service.url'

# ============================================
# NOTES SUR LES OUTPUTS
# ============================================

# 📌 ACCÉDER AUX OUTPUTS

# 1. Voir tous les outputs :
#    terraform output

# 2. Voir un output spécifique :
#    terraform output application_url

# 3. Format JSON (pour scripts) :
#    terraform output -json

# 4. Format brut (sans quotes) :
#    terraform output -raw application_url

# 5. Dans un script bash :
#    APP_URL=$(terraform output -raw application_url)
#    echo "App déployée sur : $APP_URL"

# 📌 QUESTIONS D'ENTRETIEN SUR LES OUTPUTS

# Q1 : Quelle est la différence entre output et variable ?
# R  : variable = INPUT (entrée de l'utilisateur)
#      output   = OUTPUT (résultat après création)

# Q2 : Peut-on utiliser un output dans la même config ?
# R  : Non directement. Utilisez des locals ou des références directes.

# Q3 : Comment passer un output à un autre module ?
# R  : module.nom_module.nom_output

# Q4 : Les outputs sensibles sont-ils sécurisés ?
# R  : Ils sont masqués dans la console mais VISIBLES dans le state.
#      Pour une vraie sécurité, utilisez Key Vault.

# Q5 : Comment utiliser un output dans un script CI/CD ?
# R  : terraform output -raw nom_output
#      ou terraform output -json pour un JSON complet

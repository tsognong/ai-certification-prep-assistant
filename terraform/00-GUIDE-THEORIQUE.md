# 📘 GUIDE COMPLET TERRAFORM - THÉORIE ET PRATIQUE

## 🎯 Objectif de ce Guide

Ce guide est conçu pour vous préparer à un **entretien technique** sur Terraform.
Il couvre les **concepts théoriques** ET la **pratique**, car les deux sont essentiels.

---

## 📚 PARTIE 1 : LES CONCEPTS FONDAMENTAUX

### 🔷 1.1 Qu'est-ce que l'Infrastructure as Code (IaC) ?

**Définition** : L'IaC est une approche qui consiste à **gérer et provisionner l'infrastructure via du code** plutôt que par des processus manuels.

**Avantages** :
- ✅ **Reproductibilité** : Le même code crée toujours la même infrastructure
- ✅ **Versionnement** : Infrastructure versionnée avec Git
- ✅ **Collaboration** : Plusieurs personnes peuvent travailler ensemble
- ✅ **Documentation** : Le code est la documentation
- ✅ **Automatisation** : CI/CD pour l'infrastructure
- ✅ **Réduction d'erreurs** : Moins d'erreurs humaines

**Types d'IaC** :
1. **Déclaratif** (Terraform, CloudFormation) : On décrit l'état final souhaité
2. **Impératif** (Scripts Bash, Python) : On décrit les étapes à suivre

**Question d'entretien** : "Quelle est la différence entre IaC déclarative et impérative ?"
- **Déclarative** : "Je veux 3 serveurs" → Terraform gère comment les créer
- **Impérative** : "Crée 3 serveurs avec ces commandes" → Vous gérez chaque étape

---

### 🔷 1.2 Qu'est-ce que Terraform ?

**Définition** : Terraform est un **outil IaC open-source** créé par HashiCorp qui permet de **définir, prévisualiser et déployer** l'infrastructure cloud de manière déclarative.

**Caractéristiques clés** :
- 🌐 **Multi-cloud** : Azure, AWS, GCP, etc.
- 📝 **Langage HCL** : HashiCorp Configuration Language (simple et lisible)
- 📊 **État (State)** : Suit les ressources créées
- 🔄 **Idempotent** : Exécuter plusieurs fois = même résultat
- 👀 **Plan avant Apply** : Prévisualisation des changements

**Architecture Terraform** :
```
┌─────────────┐
│  Terraform  │
│    Core     │
└──────┬──────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
  ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
  │ Azure   │   │   AWS   │   │   GCP   │   │  Autre  │
  │Provider │   │Provider │   │Provider │   │Provider │
  └─────────┘   └─────────┘   └─────────┘   └─────────┘
```

---

### 🔷 1.3 Les Concepts Clés de Terraform

#### 📌 **Provider (Fournisseur)**

**Définition** : Plugin qui permet à Terraform de communiquer avec une plateforme (Azure, AWS, etc.)

**Exemple** :
```hcl
provider "azurerm" {
  features {}
}
```

**Questions d'entretien** :
- Q : "Qu'est-ce qu'un provider ?"
- R : Un plugin qui permet à Terraform d'interagir avec une API cloud

- Q : "Peut-on utiliser plusieurs providers ?"
- R : Oui, on peut utiliser Azure + AWS dans le même projet

---

#### 📌 **Resource (Ressource)**

**Définition** : Un composant d'infrastructure (VM, réseau, base de données, etc.)

**Syntaxe** :
```hcl
resource "TYPE_RESSOURCE" "NOM_LOCAL" {
  argument = "valeur"
}
```

**Exemple** :
```hcl
resource "azurerm_resource_group" "mon_groupe" {
  name     = "mon-rg"
  location = "francecentral"
}
```

**Composants** :
- `azurerm_resource_group` : Type de ressource (du provider Azure)
- `mon_groupe` : Nom local (pour référencer dans Terraform)
- `name`, `location` : Arguments requis

**Questions d'entretien** :
- Q : "Quelle est la différence entre le nom de la ressource et l'identifiant local ?"
- R : Le nom local (`mon_groupe`) est pour Terraform, `name` est le vrai nom dans Azure

---

#### 📌 **Variable**

**Définition** : Paramètre configurable pour rendre le code réutilisable

**Types de variables** :
```hcl
# String
variable "nom_app" {
  type    = string
  default = "mon-app"
}

# Number
variable "nombre_serveurs" {
  type    = number
  default = 3
}

# Bool
variable "activer_https" {
  type    = bool
  default = true
}

# List
variable "zones" {
  type    = list(string)
  default = ["zone1", "zone2"]
}

# Map
variable "tags" {
  type = map(string)
  default = {
    Environment = "dev"
    Project     = "quiz"
  }
}

# Object
variable "config_vm" {
  type = object({
    size     = string
    disk_gb  = number
  })
}
```

**Validation** :
```hcl
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment doit être dev, staging ou prod"
  }
}
```

**Variables sensibles** :
```hcl
variable "mot_de_passe" {
  type      = string
  sensitive = true  # Masqué dans les logs
}
```

**Questions d'entretien** :
- Q : "Comment passer une valeur à une variable ?"
- R : 4 méthodes :
  1. Dans `terraform.tfvars`
  2. Avec `-var` : `terraform apply -var="nom=valeur"`
  3. Variable d'environnement : `export TF_VAR_nom=valeur`
  4. Prompt interactif si non définie

---

#### 📌 **Output (Sortie)**

**Définition** : Valeur affichée après l'exécution de Terraform

**Exemple** :
```hcl
output "url_app" {
  description = "URL de l'application"
  value       = azurerm_linux_web_app.mon_app.default_hostname
  sensitive   = false  # ou true pour masquer
}
```

**Utilisation** :
- Afficher des informations importantes (URL, IP, etc.)
- Partager des données entre modules
- Utiliser dans des scripts : `terraform output url_app`

---

#### 📌 **State (État)**

**Définition** : Fichier (`.tfstate`) qui stocke l'état actuel de l'infrastructure

**Pourquoi c'est crucial** :
- 📊 Terraform compare l'état actuel vs. désiré
- 🔄 Permet les mises à jour incrémentales
- 👥 Gère les dépendances entre ressources

**Contenu du state** :
- IDs des ressources créées
- Métadonnées
- Dépendances
- **⚠️ Peut contenir des secrets !**

**Types de backend** :

1. **Local** (par défaut) :
```hcl
# terraform.tfstate dans le dossier local
# ❌ Problème : Pas de collaboration
```

2. **Remote (distant)** :
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstatexxxx"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}
```

**Questions d'entretien** :
- Q : "Pourquoi le state est-il important ?"
- R : Il permet à Terraform de savoir ce qui existe déjà et calculer les changements nécessaires

- Q : "Doit-on commiter le state sur Git ?"
- R : ❌ NON ! Il contient des secrets. Utiliser un backend distant.

- Q : "Que faire si le state est corrompu ?"
- R : Restaurer depuis une backup ou utiliser `terraform import` pour reconstruire

---

#### 📌 **Data Source**

**Définition** : Permet de **lire** des informations existantes (ne crée rien)

**Exemple** :
```hcl
# Lire un groupe de ressources existant
data "azurerm_resource_group" "existing" {
  name = "mon-rg-existant"
}

# Utiliser ses propriétés
resource "azurerm_virtual_network" "vnet" {
  resource_group_name = data.azurerm_resource_group.existing.name
  location           = data.azurerm_resource_group.existing.location
  # ...
}
```

**Différence Resource vs Data** :
- `resource` → CRÉE ou GÈRE
- `data` → LIT seulement (read-only)

---

### 🔷 1.4 Le Workflow Terraform

```
┌──────────────────┐
│  terraform init  │ ← Initialisation (télécharge providers)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ terraform plan   │ ← Prévisualisation (dry-run)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ terraform apply  │ ← Application (crée/modifie)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│terraform destroy │ ← Destruction (supprime tout)
└──────────────────┘
```

**Détails de chaque commande** :

1. **`terraform init`**
   - Télécharge les providers
   - Initialise le backend
   - Installe les modules
   - Crée `.terraform/` et `.terraform.lock.hcl`

2. **`terraform plan`**
   - Compare state actuel vs. configuration
   - Génère un plan d'exécution
   - Affiche : `+` (create), `~` (modify), `-` (destroy)
   - **Ne modifie RIEN**

3. **`terraform apply`**
   - Exécute le plan
   - Crée/modifie les ressources
   - Met à jour le state
   - Demande confirmation (sauf `-auto-approve`)

4. **`terraform destroy`**
   - Supprime toutes les ressources du state
   - Demande confirmation

**Autres commandes importantes** :
- `terraform fmt` : Formate le code
- `terraform validate` : Vérifie la syntaxe
- `terraform show` : Affiche le state
- `terraform state list` : Liste les ressources
- `terraform output` : Affiche les outputs
- `terraform import` : Import de ressources existantes
- `terraform taint` : Marque pour recréation
- `terraform refresh` : Met à jour le state

---

### 🔷 1.5 Dépendances et Graphe

**Dépendances implicites** (automatiques) :
```hcl
resource "azurerm_resource_group" "rg" {
  name     = "mon-rg"
  location = "francecentral"
}

resource "azurerm_virtual_network" "vnet" {
  resource_group_name = azurerm_resource_group.rg.name  # ← Dépendance !
  # Terraform créera automatiquement rg avant vnet
}
```

**Dépendances explicites** :
```hcl
resource "azurerm_network_security_group" "nsg" {
  # ...
  depends_on = [azurerm_resource_group.rg]  # Force l'ordre
}
```

**Graphe de dépendances** :
```bash
terraform graph | dot -Tpng > graph.png
```

---

### 🔷 1.6 Modules

**Définition** : Un module est un **conteneur réutilisable** de code Terraform

**Structure** :
```
modules/
  ├── app-service/
  │   ├── main.tf
  │   ├── variables.tf
  │   └── outputs.tf
  └── database/
      ├── main.tf
      ├── variables.tf
      └── outputs.tf
```

**Utilisation** :
```hcl
module "mon_app" {
  source = "./modules/app-service"
  
  app_name = "quiz-app"
  location = "francecentral"
}

# Accéder aux outputs du module
output "app_url" {
  value = module.mon_app.url
}
```

**Avantages** :
- 🔄 Réutilisation du code
- 📦 Encapsulation
- 🧪 Testabilité
- 📚 Registry public : registry.terraform.io

---

### 🔷 1.7 Workspaces (Espaces de travail)

**Définition** : Permet d'avoir **plusieurs états** pour le même code

**Utilisation** :
```bash
# État par défaut : "default"
terraform workspace list

# Créer un workspace
terraform workspace new dev
terraform workspace new prod

# Changer de workspace
terraform workspace select prod

# Variable conditionnelle
locals {
  environment = terraform.workspace
}
```

**Cas d'usage** :
- Environnements multiples (dev, staging, prod)
- Tests parallèles
- Isolation des états

---

## 🎯 PARTIE 2 : CONCEPTS AVANCÉS (Entretien Senior)

### 🔶 2.1 Provisioners

**Définition** : Exécutent des scripts lors de la création/destruction

```hcl
resource "azurerm_virtual_machine" "vm" {
  # ...
  
  provisioner "local-exec" {
    command = "echo ${self.public_ip} > ip.txt"
  }
  
  provisioner "remote-exec" {
    connection {
      type     = "ssh"
      user     = "admin"
      host     = self.public_ip
    }
    
    inline = [
      "sudo apt update",
      "sudo apt install -y nginx"
    ]
  }
  
  provisioner "file" {
    source      = "script.sh"
    destination = "/tmp/script.sh"
  }
}
```

**⚠️ À éviter** : Préférer les outils dédiés (Ansible, cloud-init)

---

### 🔶 2.2 Lifecycle

**Contrôle le cycle de vie des ressources** :

```hcl
resource "azurerm_app_service" "app" {
  # ...
  
  lifecycle {
    # Empêche la destruction accidentelle
    prevent_destroy = true
    
    # Crée avant de détruire (zéro downtime)
    create_before_destroy = true
    
    # Ignore les changements externes
    ignore_changes = [
      tags,
      app_settings["SOME_KEY"]
    ]
  }
}
```

---

### 🔶 2.3 Dynamic Blocks

**Génère des blocs répétitifs** :

```hcl
variable "ports" {
  default = [80, 443, 8080]
}

resource "azurerm_network_security_group" "nsg" {
  # ...
  
  dynamic "security_rule" {
    for_each = var.ports
    content {
      name                       = "allow-${security_rule.value}"
      priority                   = 100 + security_rule.key
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = security_rule.value
      source_address_prefix      = "*"
      destination_address_prefix = "*"
    }
  }
}
```

---

### 🔶 2.4 Functions

**Terraform inclut des fonctions intégrées** :

```hcl
# Strings
upper("hello")              # → "HELLO"
lower("WORLD")              # → "world"
format("%s-%s", "app", "01") # → "app-01"

# Collections
length([1, 2, 3])           # → 3
concat([1, 2], [3, 4])      # → [1, 2, 3, 4]
lookup(map, "key", "default")

# Numeric
max(5, 12, 9)               # → 12
min(5, 12, 9)               # → 5

# Encoding
base64encode("hello")
jsonencode({a = "b"})

# Filesystem
file("path/to/file")
fileexists("path")

# Date/Time
timestamp()                 # → "2025-11-18T..."

# IP
cidrsubnet("10.0.0.0/16", 8, 2) # → "10.0.2.0/24"
```

---

### 🔶 2.5 Locals

**Variables calculées localement** :

```hcl
locals {
  # Calculs
  total_vms = var.web_vms + var.db_vms
  
  # Conditions
  environment = terraform.workspace == "prod" ? "production" : "development"
  
  # Maps
  common_tags = {
    Environment = local.environment
    ManagedBy   = "Terraform"
    Project     = var.project_name
  }
  
  # String interpolation
  full_name = "${var.project}-${local.environment}-app"
}

resource "azurerm_resource_group" "rg" {
  name     = local.full_name
  location = var.location
  tags     = local.common_tags
}
```

---

## 🎯 PARTIE 3 : QUESTIONS D'ENTRETIEN FRÉQUENTES

### ❓ Questions Théoriques

**Q1 : Qu'est-ce que Terraform et pourquoi l'utiliser ?**
> Terraform est un outil IaC qui permet de gérer l'infrastructure de manière déclarative.
> Avantages : reproductibilité, versionnement, collaboration, preview des changements.

**Q2 : Différence entre Terraform et Ansible ?**
> - **Terraform** : Provisionne l'infrastructure (création de VMs, réseaux)
> - **Ansible** : Configure les serveurs (installe logiciels, config)
> - Souvent utilisés ensemble : Terraform crée, Ansible configure

**Q3 : Qu'est-ce que l'idempotence ?**
> Exécuter la même commande plusieurs fois produit le même résultat.
> `terraform apply` deux fois → pas de changement si rien n'a changé

**Q4 : Différence entre `terraform plan` et `terraform apply` ?**
> - `plan` : Prévisualise (lecture seule, aucun changement)
> - `apply` : Exécute réellement les changements

**Q5 : Pourquoi utiliser un backend distant ?**
> - Collaboration en équipe (state partagé)
> - Verrouillage (locking) pour éviter les conflits
> - Backup automatique
> - Sécurité (pas de state local avec secrets)

**Q6 : Comment gérer les secrets dans Terraform ?**
> 1. Variables `sensitive = true`
> 2. Variables d'environnement `TF_VAR_*`
> 3. HashiCorp Vault
> 4. Azure Key Vault + data source
> 5. Ne JAMAIS commiter `.tfvars` avec secrets

**Q7 : Que faire si deux personnes appliquent en même temps ?**
> Le backend distant avec locking empêche cela.
> Le second obtient une erreur "state is locked"

**Q8 : Comment importer une ressource existante ?**
> ```bash
> terraform import azurerm_resource_group.rg /subscriptions/.../resourceGroups/mon-rg
> ```

**Q9 : Différence entre count et for_each ?**
> - `count` : Crée N copies (accès par index)
> - `for_each` : Crée depuis un map/set (accès par clé)
> `for_each` est préféré (plus stable)

**Q10 : Qu'est-ce qu'un taint ?**
> Marque une ressource pour être détruite et recréée au prochain apply
> ```bash
> terraform taint azurerm_virtual_machine.vm
> ```

---

### 🔧 Questions Pratiques

**Q1 : Créez un groupe de ressources Azure**
```hcl
resource "azurerm_resource_group" "rg" {
  name     = "mon-rg"
  location = "francecentral"
}
```

**Q2 : Ajoutez une variable pour le nom**
```hcl
variable "rg_name" {
  type = string
}

resource "azurerm_resource_group" "rg" {
  name     = var.rg_name
  location = "francecentral"
}
```

**Q3 : Créez 3 groupes de ressources**
```hcl
variable "rg_names" {
  type = list(string)
  default = ["rg-1", "rg-2", "rg-3"]
}

resource "azurerm_resource_group" "rgs" {
  for_each = toset(var.rg_names)
  
  name     = each.value
  location = "francecentral"
}
```

**Q4 : Ajoutez des tags conditionnels**
```hcl
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  
  prod_tags = var.environment == "prod" ? {
    CriticalLevel = "High"
    Backup        = "Daily"
  } : {}
  
  all_tags = merge(local.common_tags, local.prod_tags)
}

resource "azurerm_resource_group" "rg" {
  name     = var.rg_name
  location = "francecentral"
  tags     = local.all_tags
}
```

---

## 🎯 PARTIE 4 : PRATIQUE - VOTRE PROJET

Maintenant passons à la pratique avec votre infrastructure Quiz AI Agent !

Les fichiers Terraform détaillés seront créés dans les prochains fichiers.

---

## 📚 RESSOURCES POUR APPROFONDIR

### Documentation Officielle
- [Terraform Docs](https://www.terraform.io/docs)
- [Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [HashiCorp Learn](https://learn.hashicorp.com/terraform)

### Certifications
- **Terraform Associate (003)** : Certification officielle HashiCorp
- Durée : 1h, 57 questions
- Coût : ~70 USD

### Livres Recommandés
- "Terraform: Up & Running" par Yevgeniy Brikman
- "Infrastructure as Code" par Kief Morris

---

## ✅ CHECKLIST DE PRÉPARATION ENTRETIEN

### Concepts à Maîtriser
- [ ] Comprendre IaC et ses avantages
- [ ] Expliquer le workflow Terraform
- [ ] Différencier Provider, Resource, Variable, Output
- [ ] Comprendre le State et son importance
- [ ] Expliquer l'idempotence
- [ ] Connaître les dépendances (implicites/explicites)
- [ ] Comprendre les modules
- [ ] Connaître les backends distants
- [ ] Comprendre count vs for_each
- [ ] Savoir utiliser les data sources

### Compétences Pratiques
- [ ] Écrire un fichier `.tf` basique
- [ ] Utiliser des variables
- [ ] Créer des outputs
- [ ] Utiliser terraform init/plan/apply/destroy
- [ ] Gérer le state
- [ ] Importer des ressources existantes
- [ ] Utiliser des fonctions (lookup, merge, etc.)
- [ ] Créer des modules
- [ ] Gérer plusieurs environnements
- [ ] Déboguer des erreurs Terraform

### Questions à Poser
- Quelle version de Terraform utilisez-vous ?
- Utilisez-vous des modules ?
- Quel backend utilisez-vous pour le state ?
- Comment gérez-vous les secrets ?
- Utilisez-vous Terraform Cloud/Enterprise ?
- Comment organisez-vous votre code Terraform ?
- Quelle est votre stratégie de CI/CD avec Terraform ?

---

**📖 Suite dans les fichiers suivants : main.tf, variables.tf, outputs.tf**

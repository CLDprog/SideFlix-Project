# Sideflix : variables reprises du TD 4.2 (sans bi_warehouse_size, inutile ici).
# Les valeurs réelles vont dans terraform.tfvars, exclu de Git (.gitignore).
variable "organization_name" {
  description = "Première partie de l'identifiant de compte (avant le tiret), ex. ABCDEFG"
  type        = string
}

variable "account_name" {
  description = "Seconde partie de l'identifiant de compte (après le tiret), ex. XY12345"
  type        = string
}

variable "user" {
  description = "Utilisateur Snowflake associé à la clé publique RSA (authentification par paire de clés, TD 2)"
  type        = string
}

variable "private_key_path" {
  description = "Chemin local de rsa_key.p8, en dehors du dépôt. Ne jamais versionner la clé."
  type        = string
}

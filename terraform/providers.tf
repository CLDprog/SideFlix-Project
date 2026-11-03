# Sideflix : adaptation de providers.tf (TD 4.2).
# Un seul provider, rôle SYSADMIN : c'est le rôle qui crée les warehouses.
# Le second provider du TD (alias "security", rôle SECURITYADMIN) n'est pas repris :
# l'action 4.2 ne crée ni rôle ni droit (les GRANT du rôle analyste sont prévus à l'étape 10).
provider "snowflake" {
  organization_name = var.organization_name
  account_name      = var.account_name
  user              = var.user
  authenticator     = "SNOWFLAKE_JWT"
  private_key       = file(var.private_key_path)
  role              = "SYSADMIN"
}

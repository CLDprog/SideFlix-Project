# Adapted from TD 4.2. SYSADMIN creates and manages the warehouse.
# No SECURITYADMIN provider is needed: access grants are handled by governance SQL scripts.
provider "snowflake" {
  organization_name = var.organization_name
  account_name      = var.account_name
  user              = var.user
  authenticator     = "SNOWFLAKE_JWT"
  private_key       = file(var.private_key_path)
  role              = "SYSADMIN"
}

# Sideflix warehouse managed as code (action 4.2), using the TD 4.2 module.
# Built-in cost settings: 60-second auto-suspend, auto-resume, initially suspended.
# One warehouse serves ingestion, dbt and Gold queries.
# Database and schemas are created by SQL; they are not declared a second time here.
module "sideflix_warehouse" {
  source  = "./modules/warehouse"
  name    = "SIDEFLIX_WH"
  size    = "XSMALL"
  comment = "Sideflix: ingestion, dbt and Gold queries - managed by Terraform, do not edit manually"
}

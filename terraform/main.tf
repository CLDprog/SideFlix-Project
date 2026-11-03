# Sideflix : ressource déclarée en IaC (action 4.2).
# Adaptation de main.tf (TD 4.2) : on réutilise tel quel le module warehouse du TD,
# qui impose les règles de coût (auto-suspend 60 s, auto-resume, créé suspendu).
# Un seul warehouse suffit au prototype : ingestion, dbt et requêtes Gold.
# La base SIDEFLIX et ses schémas ont été créés en SQL à l'action 4.1 :
# ils ne sont pas gérés ici, pour ne pas les déclarer deux fois.
module "sideflix_warehouse" {
  source  = "./modules/warehouse"
  name    = "SIDEFLIX_WH"
  size    = "XSMALL"
  comment = "Sideflix : ingestion, dbt et requetes Gold - gere par Terraform, ne pas modifier a la main"
}

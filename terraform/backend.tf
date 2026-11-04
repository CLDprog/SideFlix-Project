# State Terraform distant et partagé (action 4.2, roadmap v2).
# Backend "gcs" de l'exemple backend.tf.example du TD 4.2 et du guide 09-iac du resource pack :
# bucket privé (accès public bloqué, accès uniforme), versionné, verrouillage intégré au backend GCS.
# Le bucket a été créé une fois à la main (étape manuelle listée dans terraform/README.md).
# Aucun identifiant ici : l'authentification Google se fait au lancement
# (gcloud auth application-default login).
# Seul le stockage du state est sur Google Cloud ; Snowflake (données et calculs) reste sur AWS.
terraform {
  backend "gcs" {
    bucket = "sideflix-tfstate-ml45551"
    prefix = "sideflix"
  }
}

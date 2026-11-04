# Remote shared Terraform state (action 4.2).
# GCS backend follows TD 4.2 and resource pack 09: private bucket, versioning and native locking.
# The bucket was created manually once; see terraform/README.md.
# Authenticate at run time with gcloud auth application-default login; no credentials are stored here.
# Google Cloud stores state only; Snowflake data and compute remain on AWS.
terraform {
  backend "gcs" {
    bucket = "sideflix-tfstate-ml45551"
    prefix = "sideflix"
  }
}

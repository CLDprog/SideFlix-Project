# Terraform — existing warehouse, shared state on GCS

The `SIDEFLIX_WH` warehouse was created by the TD 4.2 module (X-Small, auto-suspend 60 s, auto-resume). Never recreate it, and never run `apply` from an empty state.

## State: remote, versioned, locked, private (action 4.2, 4 November 2026)

- Active backend: `backend.tf`, type `gcs`, bucket `sideflix-tfstate-ml45551`, prefix `sideflix` (dedicated Google Cloud project `sideflix-tfstate-ml45551`, region europe-west9).
- Private bucket (public access blocked, uniform access), versioning enabled; native GCS backend locking (`sideflix/default.tflock`).
- Migrated from Jérémy's actual state, same lineage; `terraform plan -detailed-exitcode` = 0 after migration. Evidence: `evidence/03_cloud_and_iac/terraform_report.md`.
- Snowflake stays on AWS; Google Cloud only holds this state file.
- The active backend is GCS only; an unused S3 draft has been removed from the final delivery.

## Running Terraform

Prerequisites on the workstation: Google Cloud SDK, `gcloud auth application-default login` with an account authorized on the bucket; a local `terraform.tfvars` (see `terraform.tfvars.example`) and a Snowflake key associated with the specified user.

```sh
terraform init
terraform fmt -check
terraform validate
terraform plan -detailed-exitcode   # 0 = no changes, 1 = error, 2 = changes to review
```

Do not apply any unexpected creation, replacement or destruction. To grant a member access: `roles/storage.objectAdmin` on this bucket only, for their Google account.

## Manual steps (pack 09)

Snowflake trial account and first admin; Google Cloud project and state bucket; Google login at run time; RSA public key on the Snowflake user; the group's users. Never commit state, backups, `terraform.tfvars` or keys.

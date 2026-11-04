# Step 4.2 V2 — shared Terraform state on Google Cloud Storage

4 November 2026. Jérémy Caillaud's session, assisted by AI, on the workstation holding the existing state. Sources: course 4.2 p.34 (remote state), lab 4.2 T4 and `backend.tf.example` (GCS/S3 variants), resource pack `09-iac/README.md`, grading criterion C5.

## Requirements and guidance

| Source | Requirement or guidance | Application |
| --- | --- | --- |
| C5 | At least one relevant resource declared in IaC, with protected state where applicable | Graded requirement |
| Pack 09-iac | Protected state; for teams, remote, versioned, locked and access-controlled state (GCS, S3 or HCP Terraform); list the state bucket as a manual setup step | Team recommendation adopted in the V2 roadmap |
| Lab 4.2 | Remote state is demonstrated by the teacher and is not required in the lab | Method taught, not practiced in that lab |

## Choice and rationale

- **GCS backend:** first variant in the lab example and included in the resource pack, with integrated locking. AWS CLI/credentials were unavailable on that workstation; Jérémy already had a Google Cloud account from lab 1.2.
- **One cloud for data:** Snowflake storage and compute remain on AWS in `AWS_EU_WEST_3`. Google Cloud stores only Terraform state. No Snowflake resource was recreated or changed during the migration.
- **Dedicated project:** `sideflix-tfstate-ml45551`, separate from the lab 1.2 project, isolates state permissions.

## Work performed

1. Installed official Google Cloud SDK 592.0.0; Jérémy completed `gcloud auth login` and application-default login.
2. Manual setup: dedicated project linked to the trial billing account; private bucket `gs://sideflix-tfstate-ml45551` in `europe-west9` (Paris), uniform access, public access blocked, **versioning enabled**, seven-day soft delete.
3. Original state backed up outside Git and OneDrive at `C:\Users\jerem\sideflix_state_backup\`, with matching checksum.
4. Added `terraform/backend.tf` (`gcs`, prefix `sideflix`, no credentials) and ran `terraform init -migrate-state`.

## Executed checks

| Check | Expected | Observed |
| --- | --- | --- |
| Migration | State in bucket, same lineage | `sideflix/default.tfstate`, 4,667 bytes, identical lineage, one resource |
| `terraform fmt -check` | Exit 0 | Exit 0 |
| `terraform validate` | Valid configuration | Valid, exit 0 |
| `terraform plan -detailed-exitcode` | No changes, exit 0 | No changes, **exit 0** |
| Locking | Second operator blocked | Existing lock → `Error acquiring the state lock` (412), exit 1; after release → exit 0 |
| Versioning | Versions retained | Two state versions and history of locks acquired/released by each plan |
| Access | No anonymous access | State read HTTP 403, listing HTTP 401; Jérémy is the sole owner |
| Secrets | None in Git | No credentials in `backend.tf`; state, backup and `terraform.tfvars` excluded from Git |

Raw evidence: `rendu/terraform_4_2_v2_migration_gcs.txt`; local-state checks before migration: `rendu/terraform_4_2_v2_controle_state_local.txt`.

## Manual setup to disclose during the oral defense

Snowflake trial account and initial administrator; Google Cloud account/project and state bucket; Google authentication using `gcloud auth application-default login`; RSA public key registration on the Snowflake user; group users.

## Limitations

- Two providers are used: AWS for Snowflake/data, and Google Cloud for state only. Disclose this against the course's “1 cloud” checklist.
- Another Terraform operator needs `roles/storage.objectAdmin` on this bucket for their Google account and an RSA key registered on their Snowflake user. This was not configured at verification time: Jérémy remained the sole operator.
- Google Cloud is a trial account. Keep the local state backup until grading is complete.

# Terraform — warehouse existant, state partagé sur GCS

Le warehouse `SIDEFLIX_WH` a été créé par le module du TD 4.2 (X-Small, auto-suspend 60 s, auto-resume). Ne jamais le recréer ni lancer `apply` depuis un state vide.

## State : distant, versionné, verrouillé, privé (action 4.2, 4 novembre 2026)

- Backend actif : `backend.tf`, type `gcs`, bucket `sideflix-tfstate-ml45551`, préfixe `sideflix` (projet Google Cloud dédié `sideflix-tfstate-ml45551`, région europe-west9).
- Bucket privé (accès public bloqué, accès uniforme), versioning activé ; verrouillage natif du backend GCS (`sideflix/default.tflock`).
- Migration faite depuis le vrai state de Jérémy, même lignée ; `terraform plan -detailed-exitcode` = 0 après migration. Preuves : `rendu/Etape_4_2_V2_Verifications.md`.
- Snowflake reste sur AWS ; Google Cloud ne conserve que ce fichier de state.
- `backend.tf.example` garde la variante S3 préparée auparavant (non retenue : pas d'accès AWS).

## Lancer Terraform

Prérequis sur le poste : Google Cloud SDK, `gcloud auth application-default login` avec un compte autorisé sur le bucket ; `terraform.tfvars` local (voir `terraform.tfvars.example`) et une clé Snowflake associée à l'utilisateur indiqué.

```sh
terraform init
terraform fmt -check
terraform validate
terraform plan -detailed-exitcode   # 0 = aucun changement, 1 = erreur, 2 = changements à analyser
```

Ne pas appliquer une création, un remplacement ou une destruction inattendue. Pour donner l'accès à un membre : `roles/storage.objectAdmin` sur ce seul bucket pour son compte Google.

## Étapes manuelles (pack 09)

Compte Snowflake d'essai et premier admin ; projet Google Cloud et bucket du state ; connexion Google au lancement ; clé publique RSA sur l'utilisateur Snowflake ; utilisateurs du groupe. Ne jamais versionner state, sauvegardes, `terraform.tfvars` ni clés.

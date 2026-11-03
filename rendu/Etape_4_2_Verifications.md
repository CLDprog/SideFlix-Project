# Action 4.2 : warehouse SIDEFLIX_WH créé avec Terraform (3 novembre 2026)

Session de Jérémy Caillaud, avec assistance de l'IA. Sources : plan scolaire (étape 4), TD 4.2 partie T (`starter/terraform`, module `warehouse`).

## Réalisé

- Configuration `terraform/` adaptée du TD 4.2 :
  - `modules/warehouse/main.tf` : copié **sans modification** (vérifié par `diff`) ; il impose auto-suspend 60 s, auto-resume et création à l'arrêt.
  - `main.tf` : un seul appel du module, `SIDEFLIX_WH` en `XSMALL`. La base SIDEFLIX (action 4.1, SQL) n'est pas déclarée ici pour ne pas la gérer deux fois.
  - `providers.tf` : un seul provider, rôle SYSADMIN, authentification par paire de clés (`SNOWFLAKE_JWT`). Le provider SECURITYADMIN du TD n'est pas repris : aucun rôle ni droit n'est créé ici (étape 10).
  - `versions.tf`, `.gitignore` : repris du TD. `variables.tf`, `outputs.tf`, `terraform.tfvars.example` : adaptés (variable `bi_warehouse_size` supprimée, sortie `warehouse`).
- Terraform v1.16.6 installé sur le poste de Jérémy (`winget install Hashicorp.Terraform`, paquet officiel HashiCorp) ; le TD demande 1.9 ou plus.
- `terraform.tfvars` local (non versionné) : identifiant du compte Snowflake de Jérémy, utilisateur `REDGRAVE_AIRFLOW`, chemin de la clé privée hors du dépôt.

## Contrôles effectivement exécutés

| Contrôle | Attendu | Obtenu | Preuve |
| --- | --- | --- | --- |
| `terraform init` | provider installé | `snowflakedb/snowflake` v2.22.1, signé ; lock file créé | `rendu/terraform_4_2_init_fmt_validate.txt` |
| `terraform fmt` | code formaté | aucun fichier modifié | idem |
| `terraform validate` | configuration valide | `Success! The configuration is valid.` | idem |
| Clé utilisée = clé enregistrée sur l'utilisateur | même empreinte | `SHA256:zshY631pJ+CvefRH3j3Bm2U+A71lYZHwjlWh7eyDtSg=` des deux côtés (calcul local sur la clé publique) | ci-dessous |
| `terraform plan` relu avant apply | 1 création, rien d'autre | `Plan: 1 to add, 0 to change, 0 to destroy.` | `rendu/terraform_4_2_plan.txt` |
| `terraform apply` | warehouse créé | `Apply complete! Resources: 1 added, 0 changed, 0 destroyed.` | `rendu/terraform_4_2_apply.txt` |
| `terraform plan` après apply | aucun changement | `No changes. Your infrastructure matches the configuration.` (code retour 0 avec `-detailed-exitcode`) | `rendu/terraform_4_2_plan_after_apply.txt` |
| État lu dans Snowflake au rafraîchissement | X-Small, 60 s, auto-resume, SYSADMIN | `XSMALL`, `60`, `true`, owner `SYSADMIN`, état `SUSPENDED` | `terraform.tfstate` (local) |
| Secrets | aucune clé dans le state ni dans le dépôt | aucune occurrence de clé dans le state ; `terraform.tfvars`, `*.tfstate`, `*.p8` exclus par `.gitignore` | contrôle `grep` |

Le plan a été relu par Jérémy avant l'apply (une seule ressource créée, aucune modification ni suppression).

## Utilisateur et clé : choix et limite

- La seule paire de clés du poste (`C:\Users\jerem\redgave\keys\`, créée au TD 4.2) est associée à l'utilisateur `REDGRAVE_AIRFLOW` (type SERVICE, sans mot de passe, `HAS_KEYPAIR = true`, clé déposée le 31 octobre 2026). `DESC USER` et le calcul local donnent la même empreinte.
- Option retenue par Jérémy : réutiliser cet utilisateur sans rien créer ni modifier. Terraform ne demande que le rôle SYSADMIN, hérité de ACCOUNTADMIN.
- **Limite à présenter à l'oral (C7)** : cet utilisateur possède ACCOUNTADMIN, plus que nécessaire, et son nom vient du TD. Correction possible à l'étape 10 : utilisateur SERVICE dédié `SIDEFLIX_SVC` avec seulement les droits utiles.

## State Terraform

- State local `terraform/terraform.tfstate`, exclu de Git. Il ne contient pas la clé, seulement les attributs du warehouse.
- Le dossier du projet est synchronisé par OneDrive : le state reste privé (compte personnel) mais n'est pas un backend partagé et verrouillé. Un backend distant (exemple `backend.tf.example` du TD) serait l'étape suivante en équipe ; non mis en place pour le prototype.
- Ne pas exécuter `terraform destroy` avant la fin de la correction.

## Coût

Warehouse créé à l'arrêt (`SUSPENDED`) : aucun crédit consommé tant qu'aucune requête ne l'utilise. En X-Small : 1 crédit par heure d'activité, arrêt automatique après 60 s d'inactivité.

## Reproduction

PowerShell, dans `Projet\Sideflix\terraform` : copier `terraform.tfvars.example` en `terraform.tfvars` et le remplir, puis `terraform init`, `terraform fmt`, `terraform validate`, `terraform plan` (relire), `terraform apply`, `terraform plan` (attendu : No changes).

## Prochaine action

4.3 : adapter le SQL de setup du TD 2 pour créer, dans `SIDEFLIX.BRONZE`, le format JSON, le stage interne et les tables Bronze (catalogue et sessions brutes VARIANT avec `_source_file` et `_loaded_at`), en utilisant `SIDEFLIX_WH`.

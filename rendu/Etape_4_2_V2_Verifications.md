# Action 4.2 v2 : state Terraform partagé sur Google Cloud Storage (4 novembre 2026)

Session de Jérémy Caillaud, avec assistance de l'IA, sur le poste détenteur du state. Sources : cours 4.2 p.34 (« Remote state »), TD 4.2 partie T4 et `backend.tf.example` (variantes GCS et S3), resource pack `09-iac/README.md`, barème C5.

## Ce que demandent les supports

| Support | Formulation | Statut pour nous |
| --- | --- | --- |
| Barème C5 | « at least one relevant resource declared in IaC, with protected state where applicable » | Exigence notée |
| Pack 09-iac | « the state protected » ; « In a team keep it remote, versioned, locked and access-controlled » (GCS, S3 ou HCP Terraform) ; lister le bucket du state parmi les étapes manuelles | Recommandation d'équipe, retenue par la roadmap v2 |
| TD 4.2 | « Remote state demonstrated by the teacher, not required in the lab » | Méthode vue, non pratiquée en TD |

## Choix et justification

- **Backend GCS** : première variante de l'exemple du TD 4.2 et citée par le pack ; verrouillage intégré au backend. Le compte AWS n'était pas disponible sur le poste (ni CLI, ni identifiants) ; le compte Google Cloud de Jérémy existait déjà (TD 1.2).
- **Un seul cloud pour les données** : Snowflake (stockage et calculs) reste sur AWS, région `AWS_EU_WEST_3`. Google Cloud ne conserve que le fichier de state Terraform. Rien n'a été recréé ni modifié dans Snowflake.
- **Projet dédié** `sideflix-tfstate-ml45551`, séparé du projet du TD 1.2, pour isoler les droits du state.

## Réalisé

1. Google Cloud SDK 592.0.0 installé (paquet officiel) ; connexions `gcloud auth login` et `application-default login` faites par Jérémy.
2. Étape manuelle : projet dédié, lié au compte de facturation d'essai ; bucket `gs://sideflix-tfstate-ml45551` (europe-west9, Paris) privé, accès uniforme, accès public bloqué, **versioning activé**, corbeille de 7 jours.
3. Sauvegarde du state d'origine hors dépôt et hors OneDrive (`C:\Users\jerem\sideflix_state_backup\`), empreinte identique.
4. `terraform/backend.tf` (backend `gcs`, préfixe `sideflix`, aucun identifiant) puis `terraform init -migrate-state`.

## Contrôles effectivement exécutés

| Contrôle | Attendu | Obtenu |
| --- | --- | --- |
| Migration | state dans le bucket, même lignée | `sideflix/default.tfstate` (4667 octets), lineage identique, 1 ressource |
| `terraform fmt -check` | code 0 | 0 |
| `terraform validate` | configuration valide | valide, code 0 |
| `terraform plan -detailed-exitcode` | No changes, code 0 | No changes, **code 0** |
| Verrouillage | un second opérateur est bloqué | verrou présent → `Error acquiring the state lock` (412), code 1 ; verrou retiré → code 0 |
| Versioning | versions conservées | 2 versions du state ; historique des verrous pris/libérés par chaque plan |
| Accès | aucun accès anonyme | lecture du state HTTP 403, liste HTTP 401 ; seul propriétaire : Jérémy |
| Secrets | rien dans Git | `backend.tf` sans identifiant ; state, sauvegarde et `terraform.tfvars` hors Git |

Sorties brutes : `rendu/terraform_4_2_v2_migration_gcs.txt` ; contrôle du state local avant migration : `rendu/terraform_4_2_v2_controle_state_local.txt`.

## Étapes manuelles à citer à l'oral (pack 09)

Compte Snowflake d'essai et premier administrateur ; compte et projet Google Cloud, bucket du state ; connexion Google au lancement (`gcloud auth application-default login`) ; clé publique RSA enregistrée sur l'utilisateur Snowflake ; utilisateurs du groupe.

## Limites

- Deux fournisseurs : AWS (Snowflake, données) et Google Cloud (state uniquement). À dire explicitement face à la checklist « 1 cloud ».
- Pour qu'un autre membre lance Terraform : droit `roles/storage.objectAdmin` sur ce bucket pour son compte Google, et clé Snowflake enregistrée sur son utilisateur. Non configuré à ce jour : Jérémy reste le seul opérateur.
- Compte Google Cloud en essai ; la sauvegarde locale du state est à conserver jusqu'à la fin de la correction.

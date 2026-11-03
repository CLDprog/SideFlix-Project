# Action 4.1 : objets Sideflix dans Snowflake (3 novembre 2026)

Session de Jérémy Caillaud, avec assistance de l'IA. Sources : plan scolaire (étape 4), `02_snowflake_setup.sql` du TD 2 (onprem-to-snowflake), Terraform du TD 4.2 pour le choix des rôles.

## Réalisé

- Script `ingestion/00_create_sideflix_objects.sql`, adapté du setup du TD 2 : rôle SYSADMIN, `IF NOT EXISTS` (relance sans effet), base `SIDEFLIX` et schémas `BRONZE`, `SILVER`, `GOLD`, `LAB`, chacun avec un commentaire décrivant son rôle.
- Exécution dans le compte Snowflake de cours de Jérémy (Snowsight, Workspaces), rôle SYSADMIN, le 3 novembre 2026 vers 15 h 40 (heure de Paris).
- Aucun objet REDGRAVE n'est lu ni modifié ; aucun warehouse n'a été utilisé.

## Contrôles effectivement exécutés

| Contrôle | Attendu | Obtenu | Preuve |
| --- | --- | --- | --- |
| Base SIDEFLIX existe | oui | oui (6 schémas listés dans SIDEFLIX) | `rendu/snowflake_4_1_show_schemas.csv` |
| Schémas du plan | BRONZE, SILVER, GOLD, LAB | les quatre présents | idem |
| Propriétaire des schémas | SYSADMIN (rôle utilisé par dbt et Terraform dans les TD) | SYSADMIN pour les quatre, et pour PUBLIC | idem |
| Rôle actif pendant l'exécution | SYSADMIN | SYSADMIN | `rendu/snowflake_4_1_region.csv`, `rendu/snowflake_4_1_execution.png` |
| Fournisseur cloud et région | à relever | AWS, région `AWS_EU_WEST_3` (Paris) | idem |

`INFORMATION_SCHEMA` et `PUBLIC` sont créés automatiquement par Snowflake avec toute base. Les horodatages du CSV sont affichés par Snowsight en heure du Pacifique (-0800) : 06:40 correspond à 15:40 à Paris.

Le schéma `PUBLIC`, créé automatiquement par le rôle propriétaire de la base, appartient à SYSADMIN : la base a donc bien été créée par SYSADMIN (le `SHOW DATABASES` n'a pas été conservé séparément).

## Incident rencontré et correction

Premier essai : seule la dernière requête (région) a été exécutée, sous le rôle ACCOUNTADMIN sélectionné par défaut dans la feuille. Un `SHOW SCHEMAS IN DATABASE SIDEFLIX` a ensuite répondu « Object does not exist » : rien n'avait été créé, donc rien à corriger ni à supprimer. Deuxième essai : rôle SYSADMIN choisi dans le sélecteur de la feuille, puis exécution de tout le script sélectionné. Résultat conforme ci-dessus.

À retenir pour la suite : dans Snowsight Workspaces, sélectionner le rôle SYSADMIN dans la feuille et exécuter tout le script (Ctrl+A puis Run), sans compter seulement sur `USE ROLE`.

## Écart avec le TD et points à connaître

- Région : le TD 2 conseillait AWS US West (Oregon) ; le compte utilisé est en AWS Europe (Paris). Aucun impact sur le projet ; un seul fournisseur cloud reste utilisé (checklist Session 4.2, p. 39).
- Compte : les objets sont dans le compte d’essai de Jérémy (fin d'essai vers le 21 novembre 2026, 399 $ de crédits sur 400 au 3 novembre). Les étapes suivantes (ingestion, dbt, Airflow, Terraform) doivent viser ce même compte.
- Hors périmètre de 4.1, volontairement : warehouse `SIDEFLIX_WH` (action 4.2, Terraform) ; format JSON, stage et tables Bronze (action 4.3).

## Reproduction

Snowsight → Projects → Workspaces → nouvelle feuille SQL ; choisir le rôle SYSADMIN ; coller `ingestion/00_create_sideflix_objects.sql` ; tout sélectionner et exécuter. Une relance ne modifie rien (`IF NOT EXISTS`). Pour vérifier : `SHOW SCHEMAS IN DATABASE SIDEFLIX;` puis comparer à `rendu/snowflake_4_1_show_schemas.csv`.

## Prochaine action

4.2 : créer `SIDEFLIX_WH` avec Terraform (X-Small, auto-suspend 60 s, auto-resume) en adaptant le module warehouse du TD 4.2, puis `terraform plan` sans changement après `apply`.

# Étape 10 — état et action administrative restante

Précondition vérifiée : étapes1–9 terminées. Les fichiers10 sont préparés ; les rôles et le moniteur ne sont pas encore créés.

## Intervention exacte de Jérémy

1. Dans Snowsight, rôle ACCOUNTADMIN : lire puis exécuter `governance/10_admin_setup.sql`. Ce script crée SIDEFLIX_ANALYST/SIDEFLIX_RUNNER, accorde seulement les objets Sideflix utiles, transfère au runner la propriété des modèles Silver/Gold pour que dbt puisse les remplacer (grants actuels conservés), désactive les rôles secondaires par défaut pour Matis et rattache le moniteur mensuel. SYSADMIN conserve le contrôle par la hiérarchie des rôles. Aucun objet REDGRAVE ni warehouse Terraform n'est recréé.
2. Conserver les sorties SHOW GRANTS, SHOW RESOURCE MONITORS/WAREHOUSES et des deux relevés de crédits/stockage en fin de script dans rendu. Dans Snowsight, vérifier/configurer les notifications du moniteur pour le compte administrateur avec e-mail vérifié. Les seuils sont visibles à50/80/100%, mais aucune réception d'alerte budgétaire n'est annoncée sans preuve ; ne pas consommer artificiellement des crédits pour déclencher un seuil.
3. Matis pourra exécuter `10_verify_access.sql` : rôle analyste seul, Gold SELECT autorisé, Bronze SELECT et Gold INSERT refusés. L'INSERT de contrôle écrit zéro ligne même en cas de mauvais grant. Préserver chaque résultat, y compris les refus.
4. Dans le fichier privé `airflow/.env`, ajouter `SNOWFLAKE_ROLE=SIDEFLIX_RUNNER`. Reconstruire les deux images et recréer Airflow pour transmettre la variable, puis run normal daté du1er novembre et vérifier CURRENT_ROLE/SECONDARY_ROLES, build33/33 et publication13sessions/177,4min. Sans ces preuves,10.1 reste ouverte. Le helper Python, le profil Core et le DAG acceptent désormais la variable ; le défaut SYSADMIN est conservé pour ne pas casser les runs avant les grants. LAB est déjà créée à l'étape4 ; le hook dbt n'essaie plus de créer un schéma.
5. Jeremy vérifie ensuite le plan Terraform depuis son véritable backend GCS avant tout futur apply : le rattachement manuel du resource monitor ne doit pas être retiré par inadvertance. Ne pas lancer Terraform depuis Matis ni appliquer un changement non revu.

Le rôle analyste n'hérite pas du runner ou de SYSADMIN : ils sont ses parents dans la hiérarchie, pas ses enfants. Pour un autre utilisateur de démonstration, l'administrateur devra également accorder le rôle choisi et neutraliser les rôles secondaires ; ne pas partager la clé de Matis.

## Mesures et coûts

Voir `rendu/Etape_10_Mesures.json` et `rendu/Etape_10_V2_Verifications.md`. Les vues ACCOUNT_USAGE sont refusées à SYSADMIN ; le résultat vide du table function metering ne prouve pas un coût nul. Les chiffres réellement facturés et stockage seront complétés avec les exports administratifs. Le budget10crédits/mois est un choix de contrôle de prototype, pas une facture observée.

## Arrêt et remise en route (10.3)

Snapshots dans source/real, code sur GitHub privé, preuves dans rendu, résultats dans Snowflake ; reçus de run et base Airflow dans airflow/work et airflow/state locaux. Les clés et .env restent hors Git.

Après fin des tâches, sur le terminal du poste :

```sh
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags pause sideflix_daily
docker compose -f airflow/docker-compose.yml down
```

Puis avec SYSADMIN dans Snowsight :

```sql
ALTER WAREHOUSE SIDEFLIX_WH SUSPEND;
SHOW WAREHOUSES LIKE 'SIDEFLIX_WH';
```

Ne pas utiliser `down -v` pour l'arrêt normal : conserver la base source. Après suspension, éviter une nouvelle requête qui réveillerait le warehouse avec auto-resume. Un warehouse déjà suspendu ne nécessite pas une seconde suspension. L'assistant n'a pas l'accès au daemon du Mac ; ces actions ne sont pas prétendues exécutées ici.

Pour reprendre : ouvrir Docker Desktop, vérifier les variables privées et le rôle autorisé, puis :

```sh
docker compose -f airflow/docker-compose.yml up -d --build
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags list-import-errors
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags unpause sideflix_daily
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags trigger sideflix_daily --run-id oral_normal_20261101 --conf '{"date":"2026-11-01"}'
```

Choisir un run_id neuf pour toute nouvelle exécution. Auto-resume réveille le warehouse à la première requête autorisée. Contrôle : quatre tâches success, build33/33, une ligne de publication pour le1er novembre,13sessions/177,4min. La journée réelle sans sessions simulées peut produire un échec planifié attendu ; aucune donnée n'est inventée.

Nettoyage seulement après correction et sauvegarde : objets SIDEFLIX ciblés, jamais REDGRAVE ; ressources Terraform depuis le vrai state GCS après revue du plan destroy. Ne rien détruire avant l'oral. Bucket/versioning du state gérés séparément après suppression des ressources et conservation des preuves nécessaires ; clé/compte d'essai sous le contrôle de Jérémy.

# Accès des membres du groupe au compte Snowflake (3 novembre 2026)

Session de Jérémy Caillaud, avec assistance de l'IA. Objectif : permettre à Matis et Rayan de reprendre les étapes 6 et 7 (dbt) dans le compte Snowflake où se trouvent les objets Sideflix, sans partager la clé ni le mot de passe de Jérémy.

## Réalisé

- `ingestion/03_create_team_users.sql`, exécuté dans Snowsight avec ACCOUNTADMIN : utilisateurs `MATIS_DOUAY` et `RAYAN_FAHER_BONNE` (type PERSON, mot de passe temporaire à changer à la première connexion, rôle par défaut SYSADMIN, warehouse `SIDEFLIX_WH`, contexte `SIDEFLIX.BRONZE`), puis `GRANT ROLE SYSADMIN` à chacun.
- Les mots de passe temporaires ont été saisis uniquement dans la feuille Snowsight au moment de l'exécution ; ils ne figurent dans aucun fichier du projet et ont été transmis par un canal privé.

## Contrôle effectivement exécuté

| Contrôle | Attendu | Obtenu | Preuve |
| --- | --- | --- | --- |
| Rôle de MATIS_DOUAY | USAGE sur SYSADMIN, accordé par ACCOUNTADMIN | identique | `rendu/snowflake_acces_groupe_show_grants.csv` |
| Rôle de RAYAN_FAHER_BONNE | USAGE sur SYSADMIN, accordé par ACCOUNTADMIN | identique | idem |

## À faire par chaque membre

1. Se connecter à Snowsight (lien sur la page centrale Notion, section « Accès Snowflake »), changer le mot de passe, activer la MFA si Snowflake la demande.
2. Pour dbt (étape 6) : générer sa propre paire de clés avec `gen_key.py` (TD 2) et envoyer **uniquement la clé publique** à Jérémy, qui l'ajoute avec `ALTER USER ... SET RSA_PUBLIC_KEY = '...'`.

## Limites

- SYSADMIN donne plus de droits que nécessaire (critère C7) ; un rôle limité à SIDEFLIX pourra être créé à l'étape 10.
- Les utilisateurs dépendent du compte d'essai de Jérémy (fin vers le 21 novembre 2026).
- Les feuilles Snowsight sont enregistrées automatiquement : les mots de passe saisis doivent en être effacés après l'exécution.

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
2. Pour les scripts Python (étape 5) et dbt (étape 6) : générer sa propre paire de clés avec `gen_key.py` (TD 2) et envoyer **uniquement la clé publique** à Jérémy, qui l'ajoute avec `ALTER USER ... SET RSA_PUBLIC_KEY = '...'`.

## Limites

- SYSADMIN donne plus de droits que nécessaire (critère C7) ; un rôle limité à SIDEFLIX pourra être créé à l'étape 10.
- Les utilisateurs dépendent du compte d'essai de Jérémy (fin vers le 21 novembre 2026).
- Les feuilles Snowsight sont enregistrées automatiquement : les mots de passe saisis doivent en être effacés après l'exécution.

## Mise à jour du 4 novembre 2026 : clé de Matis pour les scripts de l'étape 5

Contexte : l'étape 5 est reprise par Matis. Les scripts Python d'ingestion se connectent par paire de clés RSA (méthode du TD 2, partie B, `connect_snowflake()` de `incremental_orders.py`). Option retenue par le groupe : chaque membre utilise sa propre clé, aucune clé privée ne circule.

Déroulé :

1. Matis a généré sa paire avec le script original `gen_key.py` du TD 2 (Cours 2, `onprem-to-snowflake`), dans un dossier local hors des dépôts. Il a publié sur la fiche Notion de l'étape 5 uniquement la commande `ALTER USER` contenant la clé **publique** et l'empreinte attendue.
2. Contrôle avant exécution : l'empreinte recalculée à partir de la clé publique (SHA-256 de la clé DER, encodée en base64) est identique à celle annoncée par Matis ; clé RSA 2048 bits valide. `DESC USER MATIS_DOUAY` : les deux emplacements `RSA_PUBLIC_KEY_FP` et `RSA_PUBLIC_KEY_2_FP` étaient vides, donc rien n'est écrasé.
3. Enregistrement le 4 novembre 2026 à 14:49 UTC, sur demande de Jérémy, depuis son poste avec le rôle ACCOUNTADMIN (connexion par clé de l'utilisateur de service, sans mot de passe) : `ALTER USER MATIS_DOUAY SET RSA_PUBLIC_KEY = '<clé publique de Matis>'`, puis `DESC USER MATIS_DOUAY`.

| Contrôle | Attendu | Obtenu | Preuve |
| --- | --- | --- | --- |
| Emplacements de clé avant | vides | `null` / `null` | `rendu/snowflake_cle_matis_verification.txt` |
| `ALTER USER` | exécuté | `Statement executed successfully.` | idem |
| `RSA_PUBLIC_KEY_FP` après | `SHA256:CsUD4fP1ZdhtvytG5im9rjZNic8oH/J0e7ix3s4aFk8=` | identique | idem |
| `RSA_PUBLIC_KEY_2_FP` après | inchangé | `null` | idem |

Reste à faire par Matis : définir `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER=MATIS_DOUAY` et `SNOWFLAKE_PRIVATE_KEY_FILE` sur son poste, puis lancer `python ingestion/check_connection.py` (attendu : MATIS_DOUAY, SYSADMIN, SIDEFLIX_WH, SIDEFLIX.BRONZE). Tant que ce test n'est pas fait, la connexion de Matis n'est pas déclarée réussie.

Rotation ou retrait : `ALTER USER MATIS_DOUAY UNSET RSA_PUBLIC_KEY;` (ACCOUNTADMIN), par exemple si la clé privée est perdue ou exposée.

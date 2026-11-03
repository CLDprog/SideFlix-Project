-- Sideflix · Accès des membres du groupe au compte Snowflake de Jérémy.
-- Crée un utilisateur pour Matis et un pour Rayan, puis leur accorde le rôle SYSADMIN
-- (propriétaire de tous les objets Sideflix : base, schémas, warehouse, tables Bronze).
-- À lancer dans Snowsight avec le rôle ACCOUNTADMIN, une seule fois.
--
-- AUCUN mot de passe n'est écrit dans ce fichier : remplacer les deux __MOT_DE_PASSE_TEMPORAIRE__
-- directement dans la feuille Snowsight au moment de l'exécution (14 caractères ou plus, majuscule,
-- minuscule, chiffre), puis les transmettre à chacun par un canal privé. Ils devront le changer à la
-- première connexion (MUST_CHANGE_PASSWORD) ; Snowflake peut aussi leur demander d'activer la MFA.
--
-- Limite (C7) : SYSADMIN est plus large que nécessaire ; suffisant pour le prototype, à présenter
-- à l'oral. Un rôle dédié limité à SIDEFLIX pourra être créé à l'étape 10.

USE ROLE ACCOUNTADMIN;

CREATE USER IF NOT EXISTS MATIS_DOUAY
    TYPE = PERSON
    LOGIN_NAME = 'MATIS_DOUAY'
    DISPLAY_NAME = 'Matis Douay'
    PASSWORD = '__MOT_DE_PASSE_TEMPORAIRE_MATIS__'
    MUST_CHANGE_PASSWORD = TRUE
    DEFAULT_ROLE = SYSADMIN
    DEFAULT_WAREHOUSE = SIDEFLIX_WH
    DEFAULT_NAMESPACE = SIDEFLIX.BRONZE
    COMMENT = 'Projet Sideflix - membre du groupe 6';

CREATE USER IF NOT EXISTS RAYAN_FAHER_BONNE
    TYPE = PERSON
    LOGIN_NAME = 'RAYAN_FAHER_BONNE'
    DISPLAY_NAME = 'Rayan Faher Bonne'
    PASSWORD = '__MOT_DE_PASSE_TEMPORAIRE_RAYAN__'
    MUST_CHANGE_PASSWORD = TRUE
    DEFAULT_ROLE = SYSADMIN
    DEFAULT_WAREHOUSE = SIDEFLIX_WH
    DEFAULT_NAMESPACE = SIDEFLIX.BRONZE
    COMMENT = 'Projet Sideflix - membre du groupe 6';

-- Le grant : donne aux deux utilisateurs le rôle propriétaire des objets Sideflix.
GRANT ROLE SYSADMIN TO USER MATIS_DOUAY;
GRANT ROLE SYSADMIN TO USER RAYAN_FAHER_BONNE;

-- Vérification : attendu, pour chacun, une ligne USAGE sur le rôle SYSADMIN.
SHOW GRANTS TO USER MATIS_DOUAY;
SHOW GRANTS TO USER RAYAN_FAHER_BONNE;

-- Pour dbt (étape 6), connexion par clé comme dans les TD, sans mot de passe :
-- chaque membre génère sa paire avec gen_key.py (TD 2) et envoie UNIQUEMENT la clé publique, puis :
-- ALTER USER MATIS_DOUAY SET RSA_PUBLIC_KEY = 'MIIBIjANBgkq...';
-- ALTER USER RAYAN_FAHER_BONNE SET RSA_PUBLIC_KEY = 'MIIBIjANBgkq...';

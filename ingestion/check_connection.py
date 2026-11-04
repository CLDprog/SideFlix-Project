"""Sideflix · Action 4.3 : vérifier la connexion d'un script à Snowflake, sans mot de passe.

Même méthode que connect_snowflake() dans incremental_orders.py (TD 2, partie B) :
paire de clés RSA + variables d'environnement, rôle SYSADMIN. Seuls la base, le schéma
et le warehouse changent (SIDEFLIX, BRONZE, SIDEFLIX_WH). Ce script ne modifie rien :
il lit le contexte de session et compte les lignes des tables Bronze.

Variables d'environnement (voir .env.example ; ne jamais versionner la clé) :
  SNOWFLAKE_ACCOUNT           identifiant de compte, ex. ABCDEFG-XY12345
  SNOWFLAKE_USER              utilisateur associé à la clé publique
  SNOWFLAKE_PRIVATE_KEY_FILE  chemin de rsa_key.p8, en dehors du dépôt

Lancement : python ingestion/check_connection.py
"""
import os
from pathlib import Path

# RSA only: do not discover ambient EC2 instance credentials.
os.environ['AWS_EC2_METADATA_DISABLED'] = 'true'
os.environ['SNOWFLAKE_DISABLE_PLATFORM_DETECTION'] = 'true'
import snowflake.connector
from cryptography.hazmat.primitives import serialization


def connect_snowflake():
    key_file = Path(os.environ["SNOWFLAKE_PRIVATE_KEY_FILE"])
    private_key = serialization.load_pem_private_key(key_file.read_bytes(), password=None)
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key=private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        role=os.environ.get("SNOWFLAKE_ROLE", "SYSADMIN"),
        warehouse="SIDEFLIX_WH",
        database="SIDEFLIX",
        schema="BRONZE",
        authenticator="SNOWFLAKE_JWT",
        login_timeout=30,
        network_timeout=60,
        session_parameters={"TIMEZONE": "UTC"},
    )


def main():
    with connect_snowflake() as sf, sf.cursor() as cur:
        cur.execute(
            "SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), "
            "CURRENT_DATABASE(), CURRENT_SCHEMA()"
        )
        user, role, warehouse, database, schema = cur.fetchone()
        print(f"Utilisateur : {user}")
        print(f"Rôle        : {role}")
        print(f"Warehouse   : {warehouse}")
        print(f"Contexte    : {database}.{schema}")
        for table in ("CATALOG", "SESSIONS_RAW", "LOAD_RUNS"):
            cur.execute(f"SELECT COUNT(*) FROM SIDEFLIX.BRONZE.{table}")
            print(f"{table:<13}: {cur.fetchone()[0]} ligne(s)")
        print("Connexion par paire de clés réussie, sans mot de passe.")


if __name__ == "__main__":
    main()

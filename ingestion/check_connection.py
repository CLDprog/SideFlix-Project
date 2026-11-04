"""Verify Snowflake RSA authentication and count Bronze rows without modifying data.

Adapted from TD 2B's connect_snowflake(): RSA key plus environment variables.
The default runtime role is SIDEFLIX_RUNNER; administrator setup is separate.
Required variables: SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER and
SNOWFLAKE_PRIVATE_KEY_FILE (private key kept outside Git).
Run: python ingestion/check_connection.py
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
        role=os.environ.get("SNOWFLAKE_ROLE", "SIDEFLIX_RUNNER"),
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
        print(f"User        : {user}")
        print(f"Role        : {role}")
        print(f"Warehouse   : {warehouse}")
        print(f"Context     : {database}.{schema}")
        for table in ("CATALOG", "SESSIONS_RAW", "LOAD_RUNS"):
            cur.execute(f"SELECT COUNT(*) FROM SIDEFLIX.BRONZE.{table}")
            print(f"{table:<13}: {cur.fetchone()[0]} row(s)")
        print("Key-pair connection succeeded without a password.")


if __name__ == "__main__":
    main()

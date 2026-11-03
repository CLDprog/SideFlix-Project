"""Sideflix · Action 5.1 : ingestion incrémentale du catalogue PostgreSQL vers Snowflake Bronze.

Adaptation de incremental_orders.py (TD 2, partie B). Même logique en trois temps :
  1. watermark : MAX(updated_at) déjà présent dans SIDEFLIX.BRONZE.CATALOG ;
  2. extraction : WHERE updated_at > watermark dans PostgreSQL (seules les lignes nouvelles ou modifiées) ;
  3. chargement : table temporaire CATALOG_BATCH puis MERGE sur content_id (insertion ou mise à jour,
     jamais de doublon ; une relance sans changement n'extrait rien).
Chaque exécution est journalisée dans SIDEFLIX.BRONZE.LOAD_RUNS.

Adaptations à Sideflix : table public.catalog (base sideflix) au lieu de merch.orders ; clé content_id ;
pas de calcul de montant ; tables CATALOG et LOAD_RUNS créées à l'avance par 01_bronze_setup.sql
(action 4.3) au lieu d'être créées par le script ; warehouse SIDEFLIX_WH.

Limite reprise du TD 2 : une suppression dans PostgreSQL n'est pas vue (aucune ligne à extraire)
et un changement qui ne touche pas updated_at n'est pas repris. Ce n'est pas un CDC complet.

Variables d'environnement :
  SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PRIVATE_KEY_FILE   (voir .env.example)
  PGUSER / PGPASSWORD (+ PGHOST, PGPORT, PGDATABASE ; par défaut 127.0.0.1 et sideflix)

Lancement (depuis le dossier Sideflix) : python ingestion/incremental_catalog.py
"""
import os
from pathlib import Path

import psycopg2
import snowflake.connector
from cryptography.hazmat.primitives import serialization

TARGET = "SIDEFLIX.BRONZE.CATALOG"
RUN_LOG = "SIDEFLIX.BRONZE.LOAD_RUNS"

EXTRACT_SQL = """
SELECT c.content_id,
       c.title,
       c.content_type,
       c.duration_seconds,
       to_char(c.updated_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"')
FROM public.catalog c
WHERE c.updated_at > %s::timestamptz
ORDER BY c.updated_at
"""

MERGE_SQL = f"""
MERGE INTO {TARGET} t
USING (
    SELECT content_id, title, content_type, duration_seconds,
           TO_TIMESTAMP_TZ(updated_at) AS updated_at
    FROM CATALOG_BATCH
) s
ON t.content_id = s.content_id
WHEN MATCHED THEN UPDATE SET
    title = s.title, content_type = s.content_type, duration_seconds = s.duration_seconds,
    updated_at = s.updated_at, _loaded_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT
    (content_id, title, content_type, duration_seconds, updated_at, _loaded_at)
VALUES
    (s.content_id, s.title, s.content_type, s.duration_seconds, s.updated_at, CURRENT_TIMESTAMP())
"""


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
        role="SYSADMIN",
        warehouse="SIDEFLIX_WH",
        database="SIDEFLIX",
        schema="BRONZE",
    )


def main():
    os.environ.setdefault("PGDATABASE", "sideflix")
    os.environ.setdefault("PGHOST", "127.0.0.1")
    sf = connect_snowflake()
    cur = sf.cursor()
    try:
        # 1. Watermark = dernière modification déjà présente dans Snowflake.
        cur.execute(f"SELECT TO_VARCHAR(MAX(updated_at), 'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM') FROM {TARGET}")
        watermark = cur.fetchone()[0] or "1900-01-01T00:00:00+00:00"
        print(f"Watermark (dernier updated_at dans Snowflake) : {watermark}")

        # 2. Extraction des seules lignes modifiées après le watermark.
        with psycopg2.connect() as pg, pg.cursor() as pg_cur:
            pg_cur.execute(EXTRACT_SQL, (watermark,))
            rows = pg_cur.fetchall()
            # Photo de la source, journalisée pour rendre visibles les écarts avec Snowflake.
            pg_cur.execute("SELECT count(*) FROM public.catalog")
            source_contents = pg_cur.fetchone()[0]
        print(f"Lignes extraites de PostgreSQL : {len(rows)}")

        # 3. Table temporaire puis MERGE dans Bronze.
        inserted = updated = 0
        if rows:
            cur.execute("""
                CREATE OR REPLACE TEMPORARY TABLE CATALOG_BATCH (
                    content_id VARCHAR, title VARCHAR, content_type VARCHAR,
                    duration_seconds NUMBER, updated_at VARCHAR)
            """)
            cur.executemany("INSERT INTO CATALOG_BATCH VALUES (%s, %s, %s, %s, %s)", rows)
            cur.execute(MERGE_SQL)
            inserted, updated = cur.fetchone()
            print(f"Résultat du MERGE : {inserted} insérée(s), {updated} mise(s) à jour")
        else:
            print("Rien de nouveau : aucun MERGE nécessaire.")

        cur.execute(f"SELECT COUNT(*), COUNT(DISTINCT content_id) FROM {TARGET}")
        total, distinct_ids = cur.fetchone()
        print(f"{TARGET} contient {total} contenu(s), {distinct_ids} content_id distinct(s).")

        # 4. Journal de l'exécution.
        cur.execute(
            f"INSERT INTO {RUN_LOG} SELECT CURRENT_TIMESTAMP(), %s, %s, %s, %s, %s, %s",
            (watermark, len(rows), inserted, updated, source_contents, total),
        )
        print(f"Exécution journalisée dans {RUN_LOG} (source : {source_contents} contenus).")
    finally:
        cur.close()
        sf.close()


if __name__ == "__main__":
    main()

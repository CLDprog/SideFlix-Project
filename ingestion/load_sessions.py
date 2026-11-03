"""Sideflix · Actions 5.3 et 5.4 : charger les sessions JSON en Bronze (batch par stage + COPY INTO).

Adaptation de la partie A du TD 2 (onprem-to-snowflake) : fichiers -> stage interne -> COPY INTO.
Au TD 2, les fichiers étaient déposés à la main (bouton « + Files ») ; le TD précise qu'en entreprise
un job planifié les pousse avec PUT. C'est ce que fait ce script, pour pouvoir être relancé tel quel
(et plus tard par Airflow, étape 8). Mêmes garanties que le TD :
  * PUT ... OVERWRITE = FALSE : un fichier déjà présent sur le stage n'est pas renvoyé ;
  * COPY INTO garde 64 jours de métadonnées de chargement : un fichier déjà chargé est ignoré,
    donc une relance n'ajoute aucune ligne (0 fichier traité).
Chaque ligne JSON est stockée telle quelle dans raw (VARIANT), avec _source_file (METADATA$FILENAME)
et _loaded_at. Le doublon S4 et la durée négative S31 restent en Bronze : ils seront traités en Silver.

Variables d'environnement : SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PRIVATE_KEY_FILE (voir .env.example).
Lancement (depuis le dossier Sideflix) : python ingestion/load_sessions.py
"""
import os
from pathlib import Path

import snowflake.connector
from cryptography.hazmat.primitives import serialization

SESSIONS_DIR = Path(__file__).resolve().parent.parent / "source" / "sessions"
STAGE = "@SIDEFLIX.BRONZE.SESSIONS_STAGE"
TARGET = "SIDEFLIX.BRONZE.SESSIONS_RAW"

COPY_SQL = f"""
COPY INTO {TARGET} (raw, _source_file, _loaded_at)
FROM (SELECT $1, METADATA$FILENAME, CURRENT_TIMESTAMP() FROM {STAGE})
FILE_FORMAT = (FORMAT_NAME = 'SIDEFLIX.BRONZE.JSON_LINES')
PATTERN = '.*sessions_[0-9-]+[.]json[.]gz'
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
    files = sorted(SESSIONS_DIR.glob("sessions_*.json"))
    print(f"Fichiers locaux trouvés : {len(files)} ({', '.join(f.name for f in files)})")
    with connect_snowflake() as sf, sf.cursor() as cur:
        # 1. Dépôt sur le stage (compression gzip automatique ; un fichier déjà présent est ignoré).
        for f in files:
            cur.execute(f"PUT 'file://{f.as_posix()}' {STAGE} AUTO_COMPRESS = TRUE OVERWRITE = FALSE")
            src, target, *_rest = cur.fetchone()
            status = _rest[-2] if len(_rest) >= 2 else _rest
            print(f"PUT  {src:<26} -> {target:<29} statut : {status}")

        # 2. Chargement des fichiers du stage dans la table brute.
        cur.execute(COPY_SQL)
        desc = [d[0].lower() for d in cur.description]
        results = [dict(zip(desc, r)) for r in cur.fetchall()]
        if results and "file" in desc:
            for r in results:
                print(f"COPY {r['file']:<40} statut : {r['status']:<7} lues : {r['rows_parsed']:>2}  chargées : {r['rows_loaded']:>2}")
        else:
            print("COPY : " + "; ".join(str(list(r.values())[0]) for r in results))

        # 3. Volumes par fichier dans Bronze.
        cur.execute(f"""
            SELECT _source_file, COUNT(*) FROM {TARGET}
            GROUP BY _source_file ORDER BY _source_file
        """)
        rows = cur.fetchall()
        for name, n in rows:
            print(f"Bronze {name:<29} : {n} ligne(s)")
        print(f"{TARGET} contient {sum(n for _, n in rows)} ligne(s) brute(s) au total.")


if __name__ == "__main__":
    main()

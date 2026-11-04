# Sources publiques et simulation

Exécuter `python source/collect_public_data.py` depuis la racine du dépôt, avec `source/requirements.txt` installé. Le collecteur n’écrit dans aucune base et ne modifie pas les événements fictifs historiques. Il télécharge MovieLens/Netflix si absents, identifie les six œuvres Wikidata par leur IMDb P345, récupère sept jours de pageviews utilisateur, puis filtre six enregistrements du flux IMDb gzip. Les réponses déjà présentes sont réutilisées.

Les données brutes `source/real/` sont conservées localement et exclues du Git par défaut. Le manifeste décrit fichiers, URLs, SHA256 et moment du contrôle ; la date de téléchargement initiale des fichiers MovieLens fournis par Matis est inconnue. Un contrôle n’est pas une nouvelle extraction. La période des consultations est du 26 octobre au 1er novembre 2026 ; les notes MovieLens et classements Netflix sont historiques. Détails dans le rapport de collecte.

Conditions, attributions, grains/périodes et curation documentés dans `docs/sources_and_catalogue.md` et le manifeste. Les données brutes restent locales ; aucune utilisation commerciale ou droit de diffusion des films n’est revendiqué.

`source/v2/sessions/` contient des événements explicitement simulés ; `source/v2/expected_daily_usage.csv` leurs résultats attendus calculés localement. Le chargement Bronze v2 et le rejeu ont réussi (voir `rendu/Etape_5_V2_Verifications.md`). La transformation dbt v2 reste à adapter. L’original est conservé dans `source/fixtures/reference/`.

## Charger le catalogue réel (TD 2)

Base PostgreSQL locale `sideflix` existante, variables PG* standard (hôte 127.0.0.1 par défaut). Depuis la racine : `python source/03_load_real_catalog.py`. Le script conserve le catalogue précédent une seule fois dans `lab.catalog_reference`, ajoute identifiant IMDb/provenance, puis applique un UPSERT. Un rejeu identique ne modifie pas `updated_at`. Les anciens scripts numérotés 01/02 restent ceux du fixture historique. Preuve : `rendu/Etape_3_2_V2_Verifications.md`. Ce chargement local n’est pas une ingestion Snowflake.

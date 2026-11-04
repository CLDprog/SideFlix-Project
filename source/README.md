# Sources publiques et simulation

Exécuter `python source/collect_public_data.py` depuis la racine du dépôt, avec `source/requirements.txt` installé. Le collecteur n’écrit dans aucune base et ne modifie pas les événements fictifs historiques. Il télécharge MovieLens/Netflix si absents, identifie les six œuvres Wikidata par leur IMDb P345, récupère sept jours de pageviews utilisateur, puis filtre six enregistrements du flux IMDb gzip. Les réponses déjà présentes sont réutilisées.

Les 19 fichiers du manifeste et les 12 réponses de `source/real/api_runs/` sont désormais partagés dans le dépôt GitHub privé du groupe, pour un usage interne uniquement. Les archives téléchargées, dumps IMDb complets et fichiers de landing générés restent exclus de Git. Un `git -c core.autocrlf=false pull --ff-only` récupère les snapshots exacts sans nouvelle collecte ni conversion des fins de ligne (notamment sur Windows). Les fins de ligne originales des sources sont conservées pour respecter les SHA-256. Le manifeste décrit fichiers, URLs, SHA256 et moment du contrôle ; la date de téléchargement initiale des fichiers MovieLens fournis par Matis est inconnue. Un contrôle n’est pas une nouvelle extraction. La période des consultations est du 26 octobre au 1er novembre 2026 ; les notes MovieLens et classements Netflix sont historiques. Détails dans le rapport de collecte.

Conditions, attributions, grains/périodes et curation documentés dans `docs/sources_and_catalogue.md` et le manifeste. Le partage est interne aux trois membres, dans le dépôt privé ; aucune utilisation commerciale ni droit de diffusion des films n’est revendiqué. La copie finale remise à la professeure doit exclure les exports IMDb (`real/imdb/`) et Netflix (`real/netflix/`), sans historique Git contenant ces fichiers. Wikidata (CC0), les statistiques Wikimedia et MovieLens peuvent rester, avec leurs attributions et la licence MovieLens `real/movielens/ml-latest-small/README.txt` intacte.

`source/v2/sessions/` contient des événements explicitement simulés ; `source/v2/expected_daily_usage.csv` leurs résultats attendus calculés localement. Le chargement Bronze v2 et le rejeu ont réussi (voir `rendu/Etape_5_V2_Verifications.md`). La transformation dbt v2 reste à adapter. L’original est conservé dans `source/fixtures/reference/`.

## Charger le catalogue réel (TD 2)

Base PostgreSQL locale `sideflix` existante, variables PG* standard (hôte 127.0.0.1 par défaut). Depuis la racine : `python source/03_load_real_catalog.py`. Le script conserve le catalogue précédent une seule fois dans `lab.catalog_reference`, ajoute identifiant IMDb/provenance, puis applique un UPSERT. Un rejeu identique ne modifie pas `updated_at`. Les anciens scripts numérotés 01/02 restent ceux du fixture historique. Preuve : `rendu/Etape_3_2_V2_Verifications.md`. Ce chargement local n’est pas une ingestion Snowflake.

## Rejeu exact sur un autre poste

Les réponses API originales du manifeste restent dans `real/wikidata/` et `real/wikimedia/`. Les réponses réellement ingérées sont conservées séparément dans `real/api_runs/`, par batch_id ; elles peuvent différer du snapshot initial. Pour rejouer le lot vérifié, utiliser le reçu déjà versionné :

```sh
python ingestion/load_sessions.py --public --replay-receipt rendu/ingestion_v2_initial.json --receipt rendu/ingestion_v2_replay.json
```

Cette commande utilise les réponses sauvegardées sans rappeler les APIs. Les variables et clés privées restent propres à chaque poste et hors Git. Les SHA-256 du manifeste décrivent les octets des sources ; seul `usage_attribution` a été actualisé pour ce partage interne. L’étape 8 est reprise par Jérémy sur son PC ; ses adaptations PostgreSQL/Compose sont distinctes de ce partage de données.

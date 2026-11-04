# Sources publiques et simulation

Exécuter `python source/collect_public_data.py` depuis la racine du dépôt, avec `source/requirements.txt` installé. Le collecteur n’écrit dans aucune base et ne modifie pas les événements fictifs historiques. Il télécharge MovieLens/Netflix si absents, identifie les six œuvres Wikidata par leur IMDb P345, récupère sept jours de pageviews utilisateur, puis filtre six enregistrements du flux IMDb gzip. Les réponses déjà présentes sont réutilisées.

Les données brutes `source/real/` sont conservées localement et exclues du Git par défaut. Le manifeste décrit fichiers, URLs, SHA256 et moment du contrôle ; la date de téléchargement initiale des fichiers MovieLens fournis par Matis est inconnue. Un contrôle n’est pas une nouvelle extraction. La période des consultations est du 26 octobre au 1er novembre 2026 ; les notes MovieLens et classements Netflix sont historiques. Détails dans le rapport de collecte.

Conditions, attributions, grains/périodes et curation documentés dans `docs/sources_and_catalogue.md` et le manifeste. Les données brutes restent locales ; aucune utilisation commerciale ou droit de diffusion des films n’est revendiqué.

`source/v2/sessions/` contient des événements explicitement simulés ; `source/v2/expected_daily_usage.csv` leurs résultats attendus calculés localement. Le chargement et les tests dans le pipeline partagé restent à réaliser. L’original est conservé dans `source/fixtures/reference/`.

# Sources et catalogue — validation de conception, 4 novembre 2026

Cinq jeux authentiques collectés et distincts, documentés dans source/sources_manifest.csv (URL, fichier, empreinte, grain, période, conditions/attribution, destination analytique). Les fichiers CSV MovieLens d’une même archive comptent comme un seul jeu ; les événements Sideflix sont simulés et ne comptent pas dans les cinq.

| Jeu | Usage et règle |
| --- | --- |
| IMDb | Référence du titre/type/année/durée ; durée du contenu, jamais du visionnage. Dump officiel non commercial : seul un extrait brut de six lignes est versionné, dans le dépôt privé et pour le rejeu, sans publication. Attribution : Information courtesy of IMDb (https://www.imdb.com). Used with permission. Usage soumis aux conditions IMDb, aucune permission commerciale revendiquée. |
| MovieLens | 74 notes pour les six films ; moyenne et nombre de notes comme contexte historique. Attribution : F. Maxwell Harper and Joseph A. Konstan, 2015, The MovieLens Datasets: History and Context, ACM TiiS 5(4), article 19, https://doi.org/10.1145/2827872. Recherche/non-commercial, pas d’approbation GroupLens implicite ; README original conservé. |
| Netflix | Benchmark hebdomadaire historique ; source officielle Tudum et statistiques attribuées à Netflix. Aucun droit de redistribution générale n’est affirmé ; l’export brut est versionné dans le dépôt privé pour le rejeu, sans publication. Correspondance certaine : Sicario (2015), fiche https://www.netflix.com/be-fr/title/80046311. Les non-appariements restent NULL/statut explicite. |
| Wikidata | Métadonnées et correspondances par P345, six QID et liens d’articles ; données structurées sous CC0, source et révision conservées dans le JSON. |
| Wikimedia | 42 statistiques quotidiennes publiques (six articles, sept jours), filtre user ; pas de texte d’article. Documentation : https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/ ; règles API : https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_API_Usage_Guidelines. Timeout, user-agent, cache et respect des erreurs 429. |

Les conditions sont documentées pour ce démonstrateur pédagogique non commercial. Elles ne constituent pas des droits de streaming, ni une autorisation commerciale pour Sideflix. Le dépôt remis reste privé, avec un accès en lecture pour la professeure. Il contient le code, les résultats attribués et les extraits nécessaires au rejeu, et n’est pas rendu public tant qu’il contient les exports IMDb et Netflix, historique compris. L’export Netflix est versionné en entier ; seul le dump IMDb complet ne l’est pas (extrait de six lignes).

## Sélection de six films

Critère pédagogique : productions de structures de cinéma indépendant / financement de producteurs identifiés, avec identification fiable dans les jeux retenus. La distribution par un grand groupe ne prouve pas à elle seule un financement studio. Aucun contrat de droits n’est supposé. Ce choix de curation est explicite, pas une classification automatique tirée d’un genre IMDb.

| Film | Repère de production et référence primaire |
| --- | --- |
| Whiplash (2014) | Bold Films, Blumhouse, Right of Way ; financement/production précisés par le distributeur : https://www.sonyclassics.com/downloads/Whiplash-Release.pdf |
| Moonlight (2016) | Film du catalogue A24, identité et sortie confirmées : https://a24films.com/films/moonlight ; production Plan B/Pastel documentée dans la fiche Wikidata liée. |
| Frances Ha (2012) | RT Features et Scott Rudin Productions, crédits du festival : https://www.festival-entrevues.com/fr/films/2025/frances-ha |
| Room (2015) | Element Pictures et No Trace Camping, soutien Film4/Irish Film Board : https://filmsandfestivals.britishcouncil.org/projects/room |
| Sicario (2015) | Black Label Media / Thunder Road ; dossier de sélection du festival : https://www.festival-cannes.com/en/f/sicario/ ; producteur : https://blacklabel-media.com/film/sicario-2/ |
| Get Out (2017) | Production Blumhouse identifiée par le distributeur : https://www.universalpictures.com/movies/get-out |

Les durées viennent exclusivement du snapshot IMDb retenu pour éviter de mélanger des éditions ou des durées de sites différents. Les six tconst sont vérifiés dans MovieLens et Wikidata ; jointures par identifiants, pas seulement par texte. Les notes historiques, rangs Netflix, consultations Wikipédia et événements simulés ont des périodes/natures distinctes.

## Vérification de l’architecture

Voir architecture_v2.md : cinq sources réelles, catalogue PostgreSQL + watermark/MERGE, fichiers + stage/COPY, APIs + requests/VARIANT, Snowflake Bronze/Silver/Gold, dbt, Docker, Airflow unique et warehouse Terraform existant. Chaque brique correspond aux TD 2, 3.2/3.3, 4.2 ou aux exemples du resource pack. Les contrôles clés/métier/fraîcheur-complétude précèdent publication. Le modèle de sortie est une ligne contenu/jour, avec contexte préagrégé pour conserver les totaux. Périmètre local/cloud et simulation identifiés. Aucun outil supplémentaire requis. Étape 2 : conception/sources validées ; le fonctionnement v2 sera vérifié aux étapes d’implémentation.

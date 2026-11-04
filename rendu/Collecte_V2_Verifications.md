# Collecte v2 — vérifications réelles

Collecte locale du 4 novembre 2026. Aucune publication ni modification PostgreSQL/Snowflake.

- Cinq jeux distincts : IMDb, MovieLens, Netflix Top 10, Wikidata, Wikimedia.
- Catalogue technique : Whiplash (2014), Moonlight (2016), Frances Ha (2012), Room (2015), Sicario (2015), Get Out (2017).
- IMDb : six enregistrements authentiques conservés sans fabrication, type movie et durée positive. Le script filtre le flux gzip officiel ; aucun gros dump n’est conservé.
- MovieLens : 9 742 films/liens, 100 836 notes ; clés uniques, aucune référence de film orpheline ; notes autorisées 0,5–5 par pas de 0,5 ; unicité utilisateur/film. 74 notes pour les six films retenus.
- Wikidata : six fiches, correspondance IMDb P345 vérifiée, QID et article anglais conservés.
- Wikimedia : six articles × sept jours = 42 observations, timestamps uniques et vues non négatives. Période 26 octobre–1er novembre 2026, all-access/user. Réponses brutes JSON conservées. Une erreur HTTP 429 a été reprise avec délai et sans refetch des snapshots déjà présents.
- Netflix : 8 884 lignes. Sicario est présent semaine du 9 mars 2025, rang 5 ; identité du film 2015 corroborée par la fiche Netflix officielle 80046311. Get Out est une piste non encore marquée vérifiée dans le mapping. Les périodes Netflix sont historiques, distinctes des événements simulés.
- Empreintes de tous les fichiers du manifeste recontrôlées avec succès.
- Simulation finale isolée : source/v2/sessions, 32 brutes = 30 sessions valides + un rejet + un doublon ; résultats par jour dans expected_daily_usage.csv. Source de visionnage explicitement sideflix_simulated. Référence du 30 octobre : A=45 min/2 sessions, B=10 min/1 session.
- Prototype original copié sans modification dans source/fixtures/reference ; les fichiers existants sont aussi conservés à leur emplacement initial.

## Reproduction

Depuis Sideflix, avec requests installé selon l’environnement du cours :

```sh
python source/collect_public_data.py
```

Le script réutilise les réponses API et le sous-ensemble IMDb conservés. Le collecteur télécharge MovieLens et Netflix si absents aux chemins indiqués. Conserver les snapshots exacts ; une extraction ultérieure peut changer.

## Restant avant validation complète (état du contrôle initial, conservé comme historique)

Documenter dans le manifeste les conditions d’usage/attribution et la période/granularité de chaque jeu ; compléter les références de curation du catalogue indépendant. Les six films sont une sélection technique, pas une preuve de droits de diffusion. L’échantillon IMDb ne doit pas être redistribué sans vérification de ses conditions.

Accès GitHub rétabli après ce contrôle initial : dépôt du groupe cloné et ajouts intégrés en préservant ingestion/Terraform. Les données brutes, d’abord conservées localement, sont versionnées dans ce dépôt privé depuis le commit 0577f62 pour le rejeu exact, sans publication ; code, mapping, manifeste et simulation sont aussi partagés. Le commit publié est consigné dans Notion. Ne pas considérer ces vérifications locales comme une exécution cloud de la v2.

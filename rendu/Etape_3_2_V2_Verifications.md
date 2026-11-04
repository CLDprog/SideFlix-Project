# Étape 3.2 v2 — vérifiée en PostgreSQL local

Chargement réel exécuté avec source/03_load_real_catalog.py, base sideflix sur 127.0.0.1. Six films réels, six identifiants IMDb distincts, durées positives et provenance imdb. Ancien catalogue (six contenus fictifs) conservé dans lab.catalog_reference ; anciens fichiers intacts.

Premier passage : six mises à jour. Rejeu : zéro modification et updated_at identiques. Clé primaire et durée positive vérifiées par tentatives rejetées puis annulées. Trigger updated_at vérifié sur une modification annulée par ROLLBACK. Aucun contenu de test persistant.

Les données ne sont pas encore chargées dans Snowflake. Chaque membre reproduit le chargement sur sa base locale selon le TD.

Catalogue vérifié :

- A : Whiplash, 6360 secondes, tt2582802
- B : Moonlight, 6660 secondes, tt4975722
- C : Frances Ha, 5160 secondes, tt2347569
- D : Room, 7080 secondes, tt3170832
- E : Sicario, 7260 secondes, tt3397884
- F : Get Out, 6240 secondes, tt5052448

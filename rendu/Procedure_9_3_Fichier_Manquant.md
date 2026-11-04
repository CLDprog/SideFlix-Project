# 9.3 — reprise d'un fichier manquant (procédure, non simulée)

1. Identifier dans les logs Airflow le fichier/source en défaut et le lot/date demandés ; consulter `source/sources_manifest.csv` pour le chemin et le SHA-256 attendus. Ne pas remplacer une absence par zéro.
2. Le collecteur réutilise les fichiers existants et peut retélécharger certains fichiers absents. Si la récupération échoue ou si un fichier requis n'existe toujours pas, `ingest_sources` échoue ; si le lot reçu est incomplet, `check_sources` échoue. Dans les deux cas les dépendances bloquent build/publication et le callback notifie après les retries.
3. Restaurer uniquement le snapshot concerné depuis le dépôt privé, en préservant d'éventuels travaux sans rapport. Exemple, après avoir confirmé l'absence du fichier :

```sh
git restore --source=HEAD -- source/real/netflix/all-weeks-global.tsv
```

4. Vérifier son empreinte avec `shasum -a 256 source/real/netflix/all-weeks-global.tsv` et la comparer à la ligne du manifeste. Ne pas accepter silencieusement un nouveau snapshot de période ou d'empreinte différente. Les réponses de rejeu exact se restaurent de même depuis leur chemin `source/real/api_runs/` versionné.
5. Relancer le même jour avec un nouveau run_id, sans option d'incident. Pour la démonstration du 1er novembre :

```sh
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags trigger sideflix_daily --run-id reprise_fichier_20261101 --conf '{"date":"2026-11-01"}'
```

6. Vérifier les quatre tâches au vert, les lots/volumes attendus et la publication unique (13 sessions/177,4 minutes pour cette date). Conserver logs et résultat du contrôle dans rendu, puis tracer la reprise dans Notion.

Précision par rapport à la formulation de la roadmap : un fichier physique absent est d'abord traité par le collecteur, donc l'échec peut survenir dès l'ingestion ; ce n'est pas systématiquement `check_sources` qui échoue. Le blocage de publication reste le même. Cette procédure n'est pas un troisième incident réellement testé et ne remplace pas les preuves de9.1/9.2.

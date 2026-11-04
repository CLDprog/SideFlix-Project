# Sources and catalogue: design validation, 4 November 2026

Five distinct authentic datasets were collected and documented in [source/sources_manifest.csv](../source/sources_manifest.csv): URL, file, checksum, grain, period, terms/attribution and analytical destination. MovieLens CSVs from one archive count as one dataset. Simulated Sideflix events do not count among the five.

| Dataset | Use and conditions |
| --- | --- |
| IMDb | Reference title, type, year and runtime; runtime is never viewing duration. A six-row extract of the official non-commercial dump is versioned privately for replay; the full dump is excluded. Attribution: Information courtesy of IMDb (https://www.imdb.com). Used with permission. Use remains subject to IMDb terms; no commercial permission is claimed. |
| MovieLens | 74 ratings for the six films; average and count provide historical context. Attribution: F. Maxwell Harper and Joseph A. Konstan, 2015, The MovieLens Datasets: History and Context, ACM TiiS 5(4), article 19, https://doi.org/10.1145/2827872. Research/non-commercial use; no implied GroupLens endorsement. The original README is retained. |
| Netflix | Historical weekly benchmark from the official Tudum source; statistics attributed to Netflix. No general redistribution rights are claimed. The raw export is versioned privately for replay. Confirmed match: Sicario (2015), https://www.netflix.com/be-fr/title/80046311. Unmatched records retain NULL and an explicit status. |
| Wikidata | Metadata and matching through P345, six QIDs and article links. Structured data is CC0; source and revision are retained in JSON. |
| Wikimedia | 42 public daily statistics (six articles, seven days), user filter; no article text. Documentation: https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/ ; API guidelines: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_API_Usage_Guidelines. Requests use a timeout, user agent and cache and respect 429 responses. |

These conditions are documented for this non-commercial educational demonstrator. They do not provide streaming rights or commercial permission for Sideflix. The delivered repository stays private; the owner must give the professor read access. It contains attributed results and replay inputs. It must not be made public while IMDb and Netflix exports remain in it, including its history. The complete Netflix export is versioned; the full IMDb dump is not.

## Selection of six films

The educational selection uses productions associated with independent film companies or identified producers, with reliable matches in the selected datasets. Distribution by a major company alone does not establish studio financing. No rights contract is assumed. This is an explicit curation choice, not an automatic classification from an IMDb genre.

| Film | Production context and primary reference |
| --- | --- |
| Whiplash (2014) | Bold Films, Blumhouse, Right of Way; distributor's production/financing notes: https://www.sonyclassics.com/downloads/Whiplash-Release.pdf |
| Moonlight (2016) | A24 catalogue identity and release: https://a24films.com/films/moonlight ; Plan B/Pastel production documented in the linked Wikidata record. |
| Frances Ha (2012) | RT Features and Scott Rudin Productions; festival credits: https://www.festival-entrevues.com/fr/films/2025/frances-ha |
| Room (2015) | Element Pictures and No Trace Camping, with Film4/Irish Film Board support: https://filmsandfestivals.britishcouncil.org/projects/room |
| Sicario (2015) | Black Label Media / Thunder Road; festival entry: https://www.festival-cannes.com/en/f/sicario/ ; producer: https://blacklabel-media.com/film/sicario-2/ |
| Get Out (2017) | Blumhouse production identified by the distributor: https://www.universalpictures.com/movies/get-out |

Runtimes come exclusively from the retained IMDb snapshot to avoid mixing editions or website figures. All six IMDb tconst identifiers are checked in MovieLens and Wikidata; joins use identifiers rather than title text alone. Historical ratings, Netflix ranks, Wikipedia page views and simulated events have different periods and meanings.

## Architecture check

See [architecture_v2.md](architecture_v2.md): five real sources; PostgreSQL catalogue with watermark/MERGE; files with stage/COPY; APIs with requests/VARIANT; Snowflake Bronze/Silver/Gold; dbt, Docker, one Airflow scheduler and the existing Terraform warehouse. Each component maps to TDs 2, 3.2/3.3, 4.2 or the resource pack. Key, business, freshness and completeness checks precede publication. The output grain is one content item/day; context is aggregated before joins to preserve totals. Local/cloud boundaries and simulation are explicit. Implementation evidence is indexed in [rendu/INDEX_PREUVES.md](../rendu/INDEX_PREUVES.md).

# Final delivery audit — 4 November 2026

## What was checked

Original Framework (six pages), grading matrix C1–C8, Session 1.2 p.6, Session 4.2 p.39, relevant resource-pack examples, latest Notion handover, submitted code, slides and saved execution evidence. The requested repository is `CLDprog/SideFlix-Project`; the earlier separate-repository plan is superseded.

## Findings and corrections

| Area | Result / correction |
| --- | --- |
| Two real incident/recovery scenarios | Verified actual controlled failures, not just written scenarios: invalid-device test blocks downstream publication and later recovers; crash after MERGE retries with one publication row. Original JSON/logs retained. |
| Live run with governance, lineage and documentation | Explicit sequence added to the English slide deck and oral runbook. This remains a future action at the oral; neither a video nor historical evidence certifies it has happened. |
| Snowflake/dbt bootstrap | Removed the unconditional dependency on Gold before its first dbt build; pre-created publication/audit tables before grants; historical-reference checks are optional on a clean account. |
| Least privilege | Runtime defaults now use SIDEFLIX_RUNNER in Airflow, Core profile and RSA helper. Administrative setup remains separate. Existing allow/deny checks and restricted service-user run are retained. |
| Presentation | 21 slides and speaker notes translated to English; stale repository links corrected, English architecture embedded, live policy/lineage/docs checks included; contributions corrected. PPTX ZIP integrity checked. Native slide rendering could not run in this session. |
| dbt documentation | Packaged actual generated index/manifest/catalog under docs/dbt with English current model descriptions/source displays. Saved catalog/lineage remain dated evidence; no new database execution is claimed. |
| Readability and language | Main README now begins with a deliverables table; retained authored reports, architecture/source/operating documents and SQL labels are English. Original data, query receipts, UI screenshots and logs are preserved in their captured language. |
| Repository structure | Slides/video grouped under deliverables; obsolete prototype reports, duplicate fixtures, placeholders, old broad-admin team setup and inactive S3 draft removed. Final code, source snapshots/licences, tests and evidence retained for reproduction. Git history is not rewritten. |
| Video | Original 80.75-second Airflow recording preserved. Its last frame precedes completion; actual logs of the same run now prove 33 successes and unique publication of 13 sessions / 177.4 minutes. |
| Sources/results | Five authentic datasets plus explicitly simulated Sideflix sessions; checksums and independently computed expected totals checked. No source snapshots or recorded results rewritten. |
| Course methods | TD2A COPY, TD2B watermark/MERGE, pack05 requests/VARIANT, TD3.2/3.3 dbt, TD4.2 DockerOperator/Terraform, packs06–09 alerting/state are used. Kafka, CDC, Iceberg and a new app are not required alternatives to deploy. |

## Validation and its limits

The local validation receipt is `rendu/FINAL_DELIVERY_CHECKS.json`. It covers Python syntax, YAML/JSON parsing, Markdown links, source file hashes, the independent simulated-session aggregation, required deliverables, PPTX integrity/language scan, and targeted secret-pattern checks. Whitespace checks were run with `git diff --check`.

This audit inspected recorded Snowflake/Snowsight/Airflow/Terraform evidence and code. A fresh live verification could not be performed: the execution environment cannot resolve external service hosts, Docker socket access is denied, and the GitHub connector returns 404 for the private repository. Existing real execution evidence is not described as a fresh rerun. Small bootstrap and default-role corrections have static validation; an end-to-end rerun of the corrected final checkout remains necessary before the oral.

## Requirements that cannot be silently declared fully satisfied

1. **Fictional versus real company:** grading C1 requests a credible fictional company, whereas Framework p.1 asks for a real-world enterprise. Sideflix is explicitly fictional, grounded in Netflix as the real industry reference; no real acquisition agreement is asserted.
2. **Cloud wording:** the checklist says “1 cloud”. Snowflake/AWS is the data/compute platform; GCS holds Terraform state only. The second provider is disclosed rather than hidden. No unnecessary migration was attempted just before delivery.
3. **Every member owns part of the pipeline:** Rayan is assigned the Gold consumption layer. Matis actually executed the saved Snowsight captures. Rayan must personally own/explain his part; this cannot be manufactured by changing attribution.
4. **Live presentation:** the presenters must actually trigger the explicit-date run and verify policies, lineage and documentation. The runbook prepares this obligation; it does not mark it complete.

## Remaining actions requiring the presenters or account owner

- **Repository owner:** grant the teacher access to this private repository and confirm the invitation. Keep it private while it contains restricted source exports/history. The assistant cannot alter that owner's GitHub App installation or verify the teacher's login.
- **Presenters:** run the final checkout on the presentation machine, keep one scheduler active, use `{"date":"2026-11-01"}`, and rehearse the exact oral checklist. Explain both executed incidents with their before/after evidence, demonstrate the live normal run, allowed/denied access, lineage and documentation.
- **Monitor owner:** confirm email notifications/delivery for the resource monitor if not already confirmed. SQL creation and configured thresholds do not prove email delivery.
- **Student submitting:** enter the final repository link and any separately requested files on the course platform, verify download/access and retain the submission confirmation. No platform submission receipt has been observed.

The technical correction commit and remote push must be checked separately. A local file or commit is not proof that GitHub has received it.

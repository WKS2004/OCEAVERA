# OBIS source record — all Area 230 occurrence records

> **Historical acquisition record:** The API JSON pages and derived CSV below
> were created during the earlier API/CSV workflow and removed from local
> storage on 7 October 2026 after the user requested cleanup and a switch to
> AWS Open Data GeoParquet. The query count, file sizes and hashes describe
> that completed historical retrieval only; none of those payloads is
> currently retained. The then-selected D-035 AWS method and its feasibility
> assessment are preserved as history. The current API/CSV acquisition is
> recorded in [D-036](2026-10-08-decision-obis-area-230-api-csv.md) and the
> [8 October source record](2026-10-08-source-obis-area-230-api-csv.md).

- **Resource ID / record date / status:** OBIS-SL-AREA230-2026-10-07; 7 October 2026; complete all-record acquisition for the accepted collection query
- **Publisher and resource title:** Ocean Biodiversity Information System (OBIS), Occurrence API v3
- **Stable publisher URL, DOI or accession:** [OBIS occurrence API](https://api.obis.org/v3/occurrence)
- **Exact version, release, taxon or layer identifier:** Live API v3; OBIS area ID 230, “Sri Lanka”; all taxa
- **Retrieval date and method:** 7 October 2026, 08:47:55–08:52:32 Asia/Colombo (03:17:55–03:22:32 UTC); paginated HTTPS GET requests from the standard-library collector
- **Exact query and filters:** `areaid=230`, `absence=include`, `dropped=include`, `qcfields=true`; page size 1,000 with cursor pagination. Area 230 is the sole geographic/taxon selection scope. No taxon, date, depth, geometry, quality-flag exclusion or overall record-count filter was applied. The page size is only a batch size; the collector continued until the API-reported total was reached.
- **API count and coverage at retrieval:** 23,934 records reported and downloaded; 24 pages (23 × 1,000 and 1 × 934); all taxa and all returned occurrence records for the query, including absence and dropped records. The API count is time-specific and may change. Area 230 is an OBIS-defined geographic area; it is not asserted to equal the Sri Lankan EEZ polygon or a final modelling population.
- **Original payload format and repository-relative location:** Unmodified JSON response bodies under `data/raw/obis/area-230-sri-lanka/20261007T031755Z/`; page retrieval times, exact request parameters, record counts and SHA-256 hashes are in the ignored local `receipt.json` and summarized below.
- **CSV export and format:** `data/interim/obis/area-230-sri-lanka/occurrences-20261007T031755Z.csv`; 23,934 data rows and 220 columns, formed from the union of fields returned across all pages. UTF-8 CSV; null values are empty cells; array/object values are compact JSON strings. This is an export of the API JSON and does not replace the preserved original responses.
- **CSV size and checksum:** 28,273,983 bytes; SHA-256 `af1a795d0da23d1657bf3e12f858dee7578a2a18c5c10c3454f93ed9ea7e6802`.
- **Licence / terms reference and sharing conditions:** No full review of the contributing datasets’ licences or redistribution conditions has been completed. Inspect OBIS source/dataset terms and ecological sensitivity before sharing records or coordinates.
- **Required attribution / citation:** Cite OBIS and the contributing datasets according to their actual terms. The acquisition retains source fields returned by OBIS; this record does not claim that every contributing dataset has the same licence.
- **Processing and limitations:** No occurrence was cleaned, filtered by quality, deduplicated, or excluded. The only conversion was serialisation of the API response fields into CSV cells; original JSON pages remain unchanged. This collection decision does not select a focal species, define the modelling population, or turn absence of a returned record into a confirmed absence.
- **Generating artefact:** [Python standard-library collector](../../src/data_collection/obis_occurrences.py); [collection decision D-034](2026-10-07-decision-obis-area-230.md).

## Original page fingerprints

Each fingerprint is SHA-256 of the exact response body saved for that page.

| Page | Records | SHA-256 |
| --- | ---: | --- |
| 1 | 1,000 | `e07994f93cd97a4dea0cdb13fbe9bc2032b1d69c5e7e46c24c671e36b22c396c` |
| 2 | 1,000 | `36a72de7d7a89f664222519a9869c45e10b787880e939ea84796d2090848c698` |
| 3 | 1,000 | `6e077aab33e490d70aab8bc193ef34d1ff7ef723d13e14b39f8e55b4833a9b43` |
| 4 | 1,000 | `1ddc9b393bbe0270983bd2440a5f9e4cdfe2f1f9e2e7cdd89853597afdad6465` |
| 5 | 1,000 | `4d6858ca6dcbbc8803d970b1d3672cbd7ad1617dc7a925c38c40568e2f0ea67e` |
| 6 | 1,000 | `639651ac6e56acc814cd27eff3deddd4fe73e7eccac1bd96db1bc4216d15cad4` |
| 7 | 1,000 | `43a7196ca4865efbcb0b03e587560d4c8bc7a3982cc49c05a4c36621d7c37e57` |
| 8 | 1,000 | `ba4a7005667f32c0d2ce362fd0010d34a7b40629129eb514bca81c4dfc5976f8` |
| 9 | 1,000 | `6d5fc389af3e22bece01c5460454bbcf8ead00f20eb6ad59eb1c797ef612a456` |
| 10 | 1,000 | `348f6d7fa9b88364226f5329fc095ac5280ce37d410b59cca9ca4d13e197032a` |
| 11 | 1,000 | `1bab3a85870f8efef28849621476072e0b6c5483923fe8450510ef08318bcb22` |
| 12 | 1,000 | `3c2f83574653f7516a0cbf30bed0fbe0eb7be92c64395e42011ee12f7ccef2e0` |
| 13 | 1,000 | `94a4324c4c1fa1b0a7f4aa2e1f0ff7bbcd08442c26cc8c54e3e9eba8daf1e476` |
| 14 | 1,000 | `05dcc2f9176872aae2c35aae0438d71f239e2f58c86b0bff78ebdea2ca998999` |
| 15 | 1,000 | `99e82f079e87c914c5b6304c1fd603724176940e429e20ecc2a2e4e5ac1217e1` |
| 16 | 1,000 | `9eb4e33315350a7c8941d2bd0c5955e0f7249950d5fa607ac90314efead22c84` |
| 17 | 1,000 | `9d88aa283c2489e196d5979b6eb4bd7e501375918a821541bcb8c15fb75c6af3` |
| 18 | 1,000 | `2d91dd63084f3e2db289b75f3e176341196d90b2a39624dce5cc974784ddd9d1` |
| 19 | 1,000 | `473be5c8ff37a9678ac89b37de5177350f4e86798ad647cc361446da72fa0417` |
| 20 | 1,000 | `17aae2765e9ddf4a715f2dc8f31d81209fdf0696e469213200743354d0103600` |
| 21 | 1,000 | `80ffcdb1a644c68da475748f1aa5553d30ac287e2a2dea39d4f717a0ce5f24ab` |
| 22 | 1,000 | `902d64203f4e8925e6eed7f5b1ecf5a4d74504aacfd558bfda3ffe9f63b3078b` |
| 23 | 1,000 | `a6e12d829d6ba3acf5dd49236cd46c97b279b32bc3e937edd727fdb652110801` |
| 24 | 934 | `7a7229514b713771b24d1049e3750b567268b86818158a26c59fc824da6e3f54` |

## Publisher references

- [OBIS data access and CSV/full-export guidance](https://manual.obis.org/access)
- [OBIS data quality and dropped-record guidance](https://manual.obis.org/data_qc.html)
- [OBIS occurrence API](https://api.obis.org/#/Occurrence/get_occurrence)

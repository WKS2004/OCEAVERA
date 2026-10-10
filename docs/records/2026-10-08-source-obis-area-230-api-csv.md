# OBIS source record — Area 230 API JSON and CSV

- **Resource ID / record date / status:** OBIS-SL-AREA230-API-CSV-2026-10-08; 8 October 2026; completed API retrieval and verified CSV conversion
- **Publisher and resource title:** Ocean Biodiversity Information System (OBIS), Occurrence API v3
- **Stable publisher URL, DOI or accession:** [OBIS occurrence API](https://api.obis.org/v3/occurrence)
- **Exact version, release, taxon or layer identifier:** Live OBIS API v3; area ID 230 (“Sri Lanka”); all taxa
- **Retrieval date and method:** 8 October 2026, 05:52:17–05:58:22 UTC (11:22:17–11:28:22 Asia/Colombo); sequential HTTPS GET pages from the standard-library downloader
- **Exact query and filters:** `areaid=230`, `absence=include`, `dropped=include`; page size `1000`; first cursor `after=-1`, then the last occurrence ID from each preceding page; `total=false` after the first page. The `fields` parameter was omitted. No taxon, date, depth, quality or total-record filter was applied. The page size controls batching only.
- **API count and coverage at retrieval:** The first response reported 23,934 records. The downloader saved 23,934 records across 24 pages (23 × 1,000 and 1 × 934), with 23,934 unique OBIS IDs and zero duplicate IDs. All returned absence and dropped records were included.
- **Count reconciliation with the OBIS Area page:** The open [Area 230 page](https://obis.org/area/230) displays 23,327 occurrence records. Of the 23,934 API records, exactly 23,327 have both `absence=false` and `dropped=false`. The other 607 are 563 records with `dropped=true` and 50 with `absence=true`, with six records in both groups (563 + 50 − 6 = 607). Thus the displayed count matches the API records without either flag; D-036 deliberately retains all 607 flagged records. No row was lost to make the counts match.
- **Original payload format and repository-relative location:** Exact API response bodies are retained as `page-00001.json` through `page-00024.json` under `data/raw/obis/json/area-230-20261008T055217394846Z/`. The ignored local `manifest.json` records the request attempts, per-page row counts, cursors, response-body sizes and SHA-256 hashes.
- **Measured response-body bytes:** 43,261,460 bytes across the 24 successful HTTP 200 response bodies; their saved page files total the same number of bytes. Three earlier sandbox DNS failures received zero response-body bytes. This measurement excludes HTTP headers, TLS and other network-protocol overhead.
- **CSV export and format:** `data/raw/obis/csv/area-230-20261008T055217394846Z.csv`; 23,934 data rows and 230 columns. The columns include every top-level key returned in the JSON records and all 68 names listed on the [OBIS Data Access page](https://obis.org/data/access/). OBIS's `aphiaID` API key is retained and also mirrored as the documented `AphiaID` column. Eleven other documented field names were not present as API keys and therefore have blank CSV cells. No records were filtered or deduplicated. Nested arrays and objects are compact JSON strings; nulls are blank cells. The exact JSON responses remain the lossless source for JSON types and values.
- **Measured coordinate extent:** A read-only scan of the retained CSV found `decimalLatitude` values from 2.93300008774 to 11.31666667° N and `decimalLongitude` values from 77.133 to 85.06° E across all 23,934 records. Both coordinate columns contained finite numeric values in every row. These are observation-coordinate extrema for this Area 230 snapshot; they are not the Bio-ORACLE collection bounds or proof that every record lies inside the irregular EEZ polygon.
- **CSV size and checksum:** 26,892,051 bytes; SHA-256 `16ec5ff96e57dc1e58baa33912d16fe7e9098c78759e750608611bf9a2dc0c43`.
- **Manifest fingerprint:** The completed JSON run manifest is 12,882 bytes; SHA-256 `fea62d18435cf724c5741f713bc95e2022e19c112472900bab812280f239acf4`. The adjacent ignored CSV receipt includes this source-manifest hash, the CSV hash and the conversion checks.
- **Licence / terms reference and sharing conditions:** Contributing-dataset terms and redistribution conditions have not been reviewed. Check OBIS source and contributing-dataset terms and ecological sensitivity before sharing records or coordinates.
- **Required attribution / citation:** Cite OBIS and contributing datasets according to their applicable terms. Retaining API fields does not establish uniform licence terms across contributors.
- **Processing and limitations:** The downloader saved each successful response body unchanged. The converter checked page hashes, cursor chain, total counts, unique IDs, the complete field union, the 68 documented access-page columns and each CSV row against the JSON. The API offers no snapshot token; records could change during pagination. The API's reported total is the completeness target for this retrieval. The exact numerical match between the page display and records with both flags false reconciles the count difference, though the page's internal display rule is not independently documented here.
- **Generating artefacts:** [Python JSON downloader](../../src/data_collection/obis_occurrences.py); [JSON-to-CSV converter](../../src/data_collection/obis_json_to_csv.py); [D-036 acquisition decision](2026-10-08-decision-obis-area-230-api-csv.md). The later raw-to-interim path convention is in [D-038](2026-10-08-decision-phase-specific-derived-data-paths.md); [`stage_obis_csv.py`](../../src/data_preparation/stage_obis_csv.py) has not been run on this raw CSV, and this source record describes the unchanged raw acquisition.

## Original page fingerprints

SHA-256 values are for the exact unchanged API response body saved for each page.

| Page file | Records | Response-body bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `page-00001.json` | 1,000 | 1,818,063 | `aa7f6e46dd31595cc471d9f472890e8449b2b929841f83bf81cc2a85a2ba836f` |
| `page-00002.json` | 1,000 | 1,809,582 | `a184237fe5fa964ae184c1ab8625ca97a85fb7a0bed5cba29e63b9c6f6401263` |
| `page-00003.json` | 1,000 | 1,794,357 | `62fc680e0f0e63c20eca55b94f26e6a3af428c4bd6f0ed8553a82e4fe8080820` |
| `page-00004.json` | 1,000 | 1,817,806 | `ebcaede5c16c950f8d5b72c4f1a4bff5efbade9587a92fe251bd02e74dd6cadd` |
| `page-00005.json` | 1,000 | 1,802,247 | `6be0187a4e1510f72bcbc0edde7cd2658dd18b036f61070ab0a61340d68bdc5d` |
| `page-00006.json` | 1,000 | 1,820,854 | `7dec7da3a335eb7ca8c3c9c4339fcbc1474d2888ae3c1dfc3fefe625bc60fb0a` |
| `page-00007.json` | 1,000 | 1,820,015 | `1b1b32aeea5e4498f3d838b023eea4a6a41f9e08188e5e049337043fec8e6c15` |
| `page-00008.json` | 1,000 | 1,832,666 | `ddb68f22a217d87d5269efb18dbc6860bcc42f8bbd58c8d276688cc64a85006b` |
| `page-00009.json` | 1,000 | 1,818,548 | `9600dcd498ceb2eb5f4d671e536bdb3fca2245e9817dca329ec0a0f274429015` |
| `page-00010.json` | 1,000 | 1,811,885 | `f3f5957e7a9c3f1c1134e27b042e20da9dec2d0f3998084517d2fda3552fc1e2` |
| `page-00011.json` | 1,000 | 1,786,834 | `daa55c390d9309d5e0e3a2921c1bed0bfed4dd3d2c63f88c92b44cf41eca54d5` |
| `page-00012.json` | 1,000 | 1,776,005 | `20f97d2ccefe14e13395dd19b78908e40d64c58ed8b85f34fc7ce5718327d79f` |
| `page-00013.json` | 1,000 | 1,814,952 | `a71f66834d37b6bdc6bd7a3eca470ad6edc2de3b224ac3c407e483a10856bcf1` |
| `page-00014.json` | 1,000 | 1,806,748 | `98cdd8beceb5b9b443aca9787196463f9e456eab7d2d041b7f4b269426d7ae7e` |
| `page-00015.json` | 1,000 | 1,811,087 | `c2037333d8db29f699f0788d1e8acab901e29a410909e8f7971c6d8bd6fda915` |
| `page-00016.json` | 1,000 | 1,809,732 | `02aa84d895553ab04593fa4898db8cd2d0ae800bc4291347c59d95a077da680d` |
| `page-00017.json` | 1,000 | 1,801,679 | `5478886725ca8978c816dd856963ca159fbd2ba590b2b5c6b9dc69c3361516eb` |
| `page-00018.json` | 1,000 | 1,787,448 | `5971c3798f2913272944db83a5b1dd820fc4fcd59d6d6fbd13d17846c98fc796` |
| `page-00019.json` | 1,000 | 1,785,150 | `89c9a048c3988564bdb4f469a40ce0b22f3238c6dd508cc3458c4722ae37e3eb` |
| `page-00020.json` | 1,000 | 1,850,589 | `93497d78230a0d32069d380070a2e21f76250925ff9443a4e76744001782adf3` |
| `page-00021.json` | 1,000 | 1,789,945 | `65cfab40bdb149f3c8933b7567253ce43159701cd52ed3083217f64946af9afb` |
| `page-00022.json` | 1,000 | 1,760,506 | `a507f87f59c5edc8e1491529a2da3b35ae500d2db8aca051ac8773a25a5120ab` |
| `page-00023.json` | 1,000 | 1,844,345 | `412248bfade8050722ea0bbc2d9464e1fd9b40c8984665f858bfd80ea1ae99af` |
| `page-00024.json` | 934 | 1,690,417 | `129d1202bb30109b40e1e98da7b0704cb4ad282de4112b9fec9b9e0abcc1b658` |

## Publisher references

- [OBIS data access](https://obis.org/data/access/)
- [OBIS occurrence API](https://api.obis.org/)
- [Official OBIS API client pagination](https://github.com/iobis/robis/blob/master/R/occurrence.R)

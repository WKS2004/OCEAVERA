# OBIS Area 230 column and row cleaning

- **Date:** 11 October 2026
- **Status:** The corrected generic OBIS cleaning stage is implemented and verified. The output is not a selected modelling population.
- **Purpose:** Replace the exploratory 90% column screen with a conservative protected-column rule, then remove only clearly unusable records or confirmed exact source duplicates.

> **Correction notice — 11 October 2026:** The initial implementation details below are retained as history. Their 113-column result and four-indicator row-missingness rule were superseded by the final correction and verification at the end of this record.

## Initial implementation record (superseded)

- **Input at that time:** The now-removed `data/interim/obis/source_validation/occurrences.csv` was a byte-preserving copy of the 23,934-row, 230-column raw source. Its SHA-256 matched the raw source: `16ec5ff96e57dc1e58baa33912d16fe7e9098c78759e750608611bf9a2dc0c43`.
- **Code:** [`clean_obis_occurrences_csv.py`](../../src/data_preparation/clean_obis_occurrences_csv.py).
- **Primary output at that time:** `data/interim/obis/cleaning/occurrences_cleaned.csv` (23,371 rows × 113 columns; SHA-256 `83b5a404816a3f21844b58b29371736c34c81cf110a7482214a4cf1bd5f53e0e`); it was later replaced by the corrected output and is not retained as a separate version.
- **Column diagnostics at that time:** `data/interim/obis/cleaning/column_completeness.csv` (230 original columns; SHA-256 `a2351eb73820eb367eb6b30de377049767f0d9aff803cb437c61e505ad6440d3`). It recorded populated/missing counts and percentages, protection status, retention status and reason for each column; the CSV report is no longer retained.
- **Runtime:** Python 3.12.14 bundled with Codex, standard library only. The WSL launch from this tool session returned `Wsl/ERROR_ACCESS_DENIED`, and no Conda command or WSL terminal was attached. No environment or package was changed. The implementation uses only standard-library functionality.

### Column cleaning (initial implementation; superseded)

An original CSV value is populated when it is not null and is not empty after trimming whitespace. The column report uses all 23,934 input rows. The configurable `MIN_COLUMN_COMPLETENESS` is 0.10; an ordinary column is retained at or above 10%, and an explicitly protected field is retained regardless of completeness. Exactly 10% qualifies. No values are imputed or normalized.

The result is 113 retained columns and 117 removed columns. All 37 requested protected fields are present and retained. Four are below 10% and remain specifically because of protection: `eventID` (4.11%), `habitat` (1.32%), `samplingEffort` (4.04%) and `samplingProtocol` (3.99%). The full removed-column list and completeness percentages are in the generated column diagnostic.

The former 90% experiment retained only 22 columns and removed useful fields; it remains in the [10 October screening record](2026-10-10-obis-area-230-column-screening.md). This implementation writes to a new filename and leaves that experimental output unchanged.

### Row cleaning (initial implementation; superseded)

The row-missingness denominator is four indicators: any usable taxonomic name or identifier; latitude; longitude; and any available `eventDate`, `date_year`, `date_start`, `date_end` or `date_mid`. Taxonomic identity accepts any available name/identifier or higher-rank name/ID; it does not require both `species` and `speciesid`, and `taxonRank` is not required. Missing uncertainty and missing date alone do not exclude a row. The configurable `MAX_ESSENTIAL_MISSINGNESS` is 0.60; exclusion requires more than 60% missing indicators.

Rules run in this order, so the exclusion counts are mutually exclusive:

| First applicable exclusion | Rows removed |
| --- | ---: |
| Explicit `dropped=true` | 563 |
| Missing, non-numeric, non-finite or out-of-range coordinates | 0 |
| No usable taxonomic identification | 0 |
| More than 60% missing across the four indicators | 0 |
| Confirmed exact duplicate across all original source columns | 0 |
| **Total removed** | **563** |
| **Rows retained** | **23,371** |

Before column reduction, exact duplicate checks compared all 230 source values. No exact duplicate groups or extra duplicate rows were found. No records became identical after column reduction. Repeated `occurrenceID` values remain: 58 groups with 58 extra records in both source and output. Repeated `species`/coordinate/`eventDate` combinations remain: 501 groups with 1,645 extra records in the source, and 496 groups with 1,640 extra records in the output. Those are diagnostics only; different source records were not merged or removed.

The `absence` and `marine` columns were not filters. The output retains 44 `absence=true` rows, 115 `marine=false` rows and 52 rows with blank `marine`. Existing QC flags were also retained; output counts are `ON_LAND` 8,000, `NO_DEPTH` 16,891, `NO_ACCEPTED_NAME` 490, `DEPTH_EXCEEDS_BATH` 584 and `NO_MATCH` 0. There are 3,188 distinct non-empty `species` names, with no species-specific filter.

### Verification and limits (initial implementation; superseded)

The cleaner completed successfully and a repeated run produced identical hashes for both generated outputs. A separate verification confirmed that the output header matches the retained columns, every output row is an unchanged source record in original order, all protected columns are retained, and the only exclusions in this snapshot are `dropped=true` rows. At the time, the raw CSV SHA-256 matched its source-validation copy. D-049 later removed the interim copy and the earlier 90% output; their fingerprints remain historical evidence only.

This is generic biological data cleaning only. It does not resolve taxonomic conflicts, interpret absence as presence, use `marine` as a spatial filter, adjudicate coastal flags, select species, validate coordinates against rasters, integrate environmental data, or construct modelling targets.

Run from the repository root with the OCEAVERA environment activated:

```text
python src/data_preparation/clean_obis_occurrences_csv.py
```

## Final correction and verified run — 11 October 2026

The cleaner was corrected after the read-only audit. The current output is 23,371 rows × 112 columns; this section supersedes the initial 23,371 × 113 result above.

### Source verification

Before cleaning, the script reads the generated source-validation manifest (`data/interim/obis/cleaning/source_validation_manifest.json`) and verifies it. The tracked [`stage_obis_csv.py`](../../src/data_preparation/stage_obis_csv.py) script creates this manifest without copying the raw CSV.

- The source path resolves inside `data/raw/obis/`.
- The raw CSV's SHA-256 and byte count match the manifest.
- The raw CSV's row and column dimensions match the manifest.
- The source fingerprint still matches after the cleaner reads the CSV.

The verified source remains 23,934 rows × 230 columns, with SHA-256 `16ec5ff96e57dc1e58baa33912d16fe7e9098c78759e750608611bf9a2dc0c43`. The raw data was not modified or copied into interim.

### Column cleaning

The 10% threshold and the 37 protected columns are unchanged. Completeness now excludes exact, field-specific missing sentinels found in this snapshot:

| Field | Sentinel treated as missing | Sentinel records |
| --- | --- | ---: |
| day | null | 2 |
| islandGroup | null | 2 |
| lifeStage | NA | 2,806 |
| modified | null | 10 |
| month | null | 2 |
| originalScientificName | NA | 47 |
| specificEpithet | NA | 3,291 |
| verbatimElevation | null | 2 |
| year | null | 2 |

Matching trims surrounding whitespace and ignores case. Other strings such as unknown are not treated as missing because they may be explicit category or text values.

The result is **112 retained columns** and **118 removed columns**. All 37 protected columns are present and retained; the same four protected columns remain below the threshold: eventID, habitat, samplingEffort and samplingProtocol. lifeStage is no longer retained: after excluding its 2,806 NA values, it has 1,547 usable values out of 23,934 (**6.46%**). specificEpithet remains above the threshold at 3,245 usable values (**13.56%**). Exact counts and decisions for all 230 source columns are in the generated JSON column-completeness report (`data/interim/obis/cleaning/column_completeness.json`).

### Row eligibility and optional missingness

The ineffective 60% row-missingness rule has been removed. Row eligibility now requires:

1. The OBIS dropped field is not true.
2. Latitude and longitude are finite numeric coordinates within their legal ranges.
3. At least one usable retained taxonomic name or identifier is present at any rank. This includes taxonID; it does not require species, speciesid or taxonRank.
4. The full original source row is not an exact duplicate of an earlier eligible row.

This keeps the essential requirements tied to spatially usable, taxonomically identifiable occurrence records. Dates, species-level fields, coordinate uncertainty and descriptive metadata are optional; missing values in them are reported but do not exclude an otherwise eligible observation. marine, absence and quality flags remain non-filtering fields.

| First applicable exclusion | Rows |
| --- | ---: |
| OBIS dropped=true | 563 |
| Invalid coordinates | 0 |
| No usable taxonomic identification | 0 |
| Confirmed exact full-source duplicate | 0 |
| **Total excluded** | **563** |
| **Rows retained** | **23,371** |

Optional missingness in the final output includes 5,043 rows with all five date fields missing (21.58%), 5,952 with both species and speciesid missing (25.47%), 12,407 without coordinate uncertainty (53.09%), and 13,033 without taxonRank (55.77%). These observations remain in the cleaned output.

The output retains 3,188 distinct non-empty species values, 115 marine=false records, 52 blank marine records and 44 absence=true records. Quality flags remain for later interpretation; no spatial or taxonomic adjudication was performed.

### Safe outputs and reproducibility

The script writes each output to a temporary file in the target directory, flushes it, then atomically replaces the destination. It replaces the JSON run summary last so its recorded hashes identify the completed CSV and JSON report. These interim outputs are local generated artefacts; the tracked [cleaner script](../../src/data_preparation/clean_obis_occurrences_csv.py) recreates them.

- Cleaned CSV: `data/interim/obis/cleaning/occurrences_cleaned.csv`, 23,371 × 112, SHA-256 `1e51a18bb6cf096e111dd0f2c810c97e93619501f74574c3b2c6be130b1aec21`.
- Column report: `data/interim/obis/cleaning/column_completeness.json`, 230 source-column entries, SHA-256 `63774d6050980f089e0a979cc3dcf904ccf168a5202251f75e6549baeff6cae5`.
- Run summary: `data/interim/obis/cleaning/cleaning_summary.json`; it records source metadata, criteria, sentinel rules, column decisions, row exclusions, optional missingness, duplicate diagnostics and hashes for the CSV and JSON report.

The cleaner completed twice with identical primary-output and column-report hashes. Independent checks confirmed the output rows and retained values match eligible source records in source order, every protected field is present, and the only exclusions in this snapshot are the 563 OBIS-dropped records. The bundled Python 3.12.14 runtime was used because WSL returned Wsl/ERROR_ACCESS_DENIED; no environment or package was changed. Reproduction from the repository root:

    python src/data_preparation/clean_obis_occurrences_csv.py

This remains generic OBIS cleaning only. Taxonomic reconciliation, marine-raster validation, Bio-ORACLE integration, species selection, feature or target construction and model training were not performed.

## Interim retention policy — 11 October 2026

Under [D-049](2026-10-11-decision-interim-one-current-dataset.md), `data/interim/obis/` contains only the `cleaning/` subdirectory. That directory holds the single cleaned occurrence CSV, its JSON reports and the source-validation manifest; source validation does not create a sibling directory or copy the raw CSV. Earlier OBIS interim datasets are not retained; the raw source and scripts allow the required state to be regenerated. Bio-ORACLE now also has only its `cleaning/` subdirectory; the [cleaning record](2026-10-11-bio-oracle-cleaning.md) documents its one review item and the rechecked source-validation bundle that preceded it. A single integrated dataset is planned but does not yet exist.

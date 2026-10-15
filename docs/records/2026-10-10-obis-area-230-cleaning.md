# OBIS Area 230 cleaning for later spatial merge

- **Date:** 10 October 2026
- **Status:** Historical first row-filter pass. Its interim output was superseded by later OBIS cleaning and is not retained under [D-049](2026-10-11-decision-interim-one-current-dataset.md).
- **Purpose:** Preserve evidence for the earlier trial of source-state and coordinate row exclusions. The intermediate 90% column screen is documented in the [column-screening record](2026-10-10-obis-area-230-column-screening.md); the current result is in the [11 October cleaning record](2026-10-11-obis-area-230-cleaning.md).

**Historical-output note — 11 October:** The row-filter and subsequent 90% column-screen CSVs described below are no longer present in interim. Only the current cleaned OBIS CSV is retained; earlier states can be regenerated from the raw source and scripts under D-049.

## Historical source and output

- **Source resource:** Complete OBIS Area 230 API/CSV snapshot selected under [D-036](2026-10-08-decision-obis-area-230-api-csv.md), retrieved 8 October 2026. The source query includes all taxa, absence and dropped records, with no date, depth or record-quality filter.
- **Raw CSV:** `data/raw/obis/csv/area-230-20261008T055217394846Z.csv`; 23,934 rows, 230 columns; SHA-256 `16ec5ff96e57dc1e58baa33912d16fe7e9098c78759e750608611bf9a2dc0c43`.
- **Input at that time:** `data/interim/obis/source_validation/occurrences.csv`; a verified byte-for-byte copy of the raw CSV, later removed under D-049.
- **Generating code:** [`04_clean_obis_occurrences_csv.py`](../../src/data_preparation/04_clean_obis_occurrences_csv.py), using the Python standard library.
- **Earlier row-filter output (superseded):** `data/interim/obis/cleaning/occurrences.csv`; 23,217 rows, 230 columns, 25,945,951 bytes; SHA-256 `9d3eb7482e447897b178c65fe11ceef3b072dca4c3db12d95973596794bf88ab`.
- **Implementation update:** This row-filter output was superseded first by the user's request to screen columns, then by the current 10% protected-column and conservative row-cleaning implementation; see the [current cleaning record](2026-10-11-obis-area-230-cleaning.md).
- **Runtime:** Configured bundled Python 3.12.14; no environment or package operation was performed.

## Earlier row-filter rules and counts

The earlier row-filter pass read the fixed source-validation CSV and wrote a stable timestamp-free cleaning path. It retained the original 230 columns in the same order and retained the exact parsed source values and row order for every kept record. It did not append review or other fields.

| Ordered exclusion rule | Rows excluded by first matching rule | Reason |
| --- | ---: | --- |
| `dropped=true` | 563 | OBIS identifies the record as dropped by its quality-control pipeline. |
| `absence=true`, unless already dropped | 44 | An explicit absence is not an occurrence in this occurrence-only handoff; six such rows were already counted as dropped. |
| `marine=false`, unless already excluded | 110 | The record is explicitly marked non-marine; another 109 of the 219 false-status rows overlap with an earlier exclusion. |
| Invalid, missing or out-of-range latitude/longitude, unless already excluded | 0 | No source row in this snapshot fails the finite-number and legal-range check. |
| **Total removed** | **717** | The reasons above are mutually exclusive under the listed priority. |
| **Retained** | **23,217** | One row per retained OBIS record; source schema unchanged. |

The counts for criteria can overlap: `dropped=true` occurs on 563 rows, `absence=true` on 50, and `marine=false` on 219. The output has 23,165 `marine=true` rows and retains 52 blank marine-status rows for later species-level review. Every retained row has `absence=false`, `dropped=false`, and valid coordinates.

For the run recorded above, the then-current script also checked the staged-source fingerprint, compared the cleaned rows to the source, and wrote a local manifest. That implementation and its row exclusions are no longer applied by the current script. The historical pass made no imputations, coordinate normalization, deduplication, joins, targets or features.

## Issues observed in the earlier row-filter output

- The earlier output retained repeated `occurrenceID` values without deduplication; 57 repeated-ID groups remained. Source pairs match on coordinates, date and scientific name but differ in `dataset_id`, OBIS `id` and `taxonRank`; source/taxonomic reconciliation is needed before deciding whether observations are duplicates.
- Blank marine status was retained rather than converted to false. Blank dates, depth, coordinate uncertainty, taxon rank/ID and licence were also retained. Their relevance depends on focal species and selected Bio-ORACLE layers.
- OBIS `flags` were unchanged. The earlier output still contained `ON_LAND` on 7,923 rows and `NO_DEPTH` on 16,755 rows. The land flag will be checked against actual marine-grid/domain matching when integration is implemented; it was not treated as a certain location error in that row-filter pass.
- The focal species, final modelling polygon, temporal/depth requirements, target and candidate duplicate policy remain unselected. This output is not an analysis-ready or integrated modelling table.
- CSV is used as an interim handoff because the configured runtime has no compatible GeoParquet writer. The project still prefers GeoParquet for a compatible derived spatial table; this output is not a completed spatial dataset.
- Review OBIS and contributing-dataset terms before redistribution. The retained row-level `license` field is blank on 12,009 rows.

The EDA findings supporting these rules are in the [dated EDA record](2026-10-10-obis-area-230-eda.md). OBIS documents dropped records and quality control in its [data-QC guidance](https://manual.obis.org/data_qc.html), and identifies `absence`, `dropped` and `marine` among the access fields in the [field reference](https://portal.obis.org/data/access/). No Bio-ORACLE files or integration outputs were changed.

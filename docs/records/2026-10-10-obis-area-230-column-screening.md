# OBIS Area 230 column-completeness screen

- **Date:** 10 October 2026
- **Status:** Historical experiment. The 90% screen and its output were superseded by the 10% protected-column cleaning stage and are no longer retained under [D-049](2026-10-11-decision-interim-one-current-dataset.md).
- **Purpose:** Remove source columns with less than 90% non-empty values before any OBIS row exclusions or later feature analysis.

This record preserves the 10 October experiment. The current OBIS interim dataset is the cleaned output documented in the [11 October cleaning record](2026-10-11-obis-area-230-cleaning.md); it retains one CSV, and the earlier 90% output can be regenerated from the raw source if required.

## Input and rule

- **Source:** OBIS Area 230 CSV retrieved 8 October 2026 under [D-036](2026-10-08-decision-obis-area-230-api-csv.md); 23,934 rows and 230 columns. The raw-source fingerprint and byte-preserving staging evidence are in the [source record](2026-10-08-source-obis-area-230-api-csv.md).
- **Input path at that time:** `data/interim/obis/source_validation/occurrences.csv`; this validation copy was later removed under D-049.
- **Generating code:** [`04_clean_obis_occurrences_csv.py`](../../src/data_preparation/04_clean_obis_occurrences_csv.py).
- **Rule:** Count a cell as filled when its value is not empty after trimming whitespace. Keep a column when at least 90% of all 23,934 source rows have a filled cell. Exactly 90% qualifies.
- **Row treatment:** All 23,934 source rows are preserved, including rows marked dropped, absence or non-marine. This stage removes columns only.

## Result

- **Columns:** 22 of 230 retained; 208 removed.
- **Retained columns, in source order:** `AphiaID`, `absence`, `aphiaID`, `basisOfRecord`, `bathymetry`, `class`, `classid`, `dataset_id`, `decimalLatitude`, `decimalLongitude`, `dropped`, `flags`, `id`, `kingdom`, `kingdomid`, `marine`, `node_id`, `originalScientificName`, `phylum`, `phylumid`, `scientificName`, `shoredistance`.
- **Output:** `data/interim/obis/cleaning/occurrences.csv`; 23,934 rows, 22 columns, 6,925,359 bytes; SHA-256 `c12bf1912a27aa9c2fa2a4698d2eba64186e1c0be77bb1fda344d23fd056858b`.

The screen removes several potentially useful fields because they fall below the requested threshold: `occurrenceID` is 86.7% filled, `scientificNameID` 89.4%, `eventDate` 78.2%, `family` 83.8%, `genus` 80.1%, `species` 73.2%, `taxonRank` 43.5%, `depth` 27.8% and `coordinateUncertaintyInMeters` 46.4%. The unique OBIS `id` column is retained, and `scientificName` meets the threshold. That experimental output could not support `occurrenceID`-based duplicate review or later date, depth, taxon-rank and coordinate-uncertainty checks. The raw source remains available at `data/raw/obis/csv/area-230-20261008T055217394846Z.csv`.

This is a completeness screen, not a semantic-validity or feature-correlation assessment. Any nonblank text counts as filled. No values are changed, no missing values are imputed, and no row, species or feature-selection rules are applied in this experiment. Its output is superseded; the prior row-filter result remains in the [historical row-cleaning record](2026-10-10-obis-area-230-cleaning.md).

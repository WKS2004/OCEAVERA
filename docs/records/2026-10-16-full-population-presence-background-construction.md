# OCEAVERA — Full-population long-format presence/background construction

**Status:** Full-population long-format presence/background candidate generated; scientific target and domain approval remain pending

The dataset contains every Policy B observation once as a positive row, followed by one separately sampled marine background row per source observation. Label 0 is a sampled background example, not a confirmed absence. This is a candidate dataset, not an approved final target or validated training set.

## Dataset and labels

| Measure | Result |
| --- | ---: |
| Output shape | 4,706 × 527 |
| Source positives preserved | 2,353 |
| Sampled background rows | 2,353 |
| Original source fields | 519 |
| Environmental feature columns | 382 |
| Distinct occupied / background cells | 362 / 2,353 |
| Positive/background cell overlap | 0 |
| Preliminary species-level eligible positive rows | 1,729 |
| File size / SHA-256 | 9,412,505 bytes / `234177bf3641856cdd10b425f2da957a27210f876d31092ba715a53cee7a429f` |
| GeoParquet | 1.1.0, EPSG:4326, WKB Point, ZSTD |

## Period, pool and environmental coverage

| Period | Slice | Positives | Backgrounds | Candidate pool | Positive non-null env. values | Background non-null env. values |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2000-2009 | baseline_2000 | 376 | 376 | 24,175 | 104,433 | 125,215 |
| 2010-2019 | baseline_2010 | 596 | 596 | 23,799 | 183,504 | 198,475 |
| 2020-2026 | ssp245_2020 | 1,381 | 1,381 | 23,203 | 426,262 | 481,990 |

Across the 382 environmental features, positive rows contain 714,199 non-null values and background rows contain 805,680. All 2,353 sampled backgrounds have all six core predictors. Source quarantines and missing environmental values remain null.

## Taxonomic eligibility and duplicate observations

Of 2,353 preserved positives, 2,353 have a valid positive AphiaID, 2,009 have explicit species rank, and 501 distinct valid AphiaIDs occur at species rank. The preliminary technical screen flags 1,729 as eligible and retains 624 as ineligible. Ineligibility reason counts are non-exclusive: {"missing_core_environment": 271, "source_cell_centre_not_marine": 324, "unverified_species_rank": 344}.
There are 300 repeated valid species/AphiaID × grid-cell × period combinations involving 920 rows (620 excess rows beyond one per combination). These rows remain present and are not independent model samples.

## Sampling and source verification

Sampling used seed `20261016`. All 362 occupied Policy B cells were excluded across taxa and periods; background cells are unique globally. The GSHHG-water cell-centre pools require complete values for all six core predictors. 106 NetCDF products and 1,012 catalogue mappings were checked. The 898,846 background environmental positions were read back and compared to the period-matched source arrays: 0 numerical mismatches, 0 null/fill discrepancies, maximum absolute difference 0.

The geographic and bathymetric summaries in the JSON report compare original occurrence locations with sampled water-cell centres. Uniform sampling across the broad marine mask may produce different location and depth distributions from the occurrence process and may make classification look easier than it is.

## Preservation and interpretation limits

All 519 source fields and the original Point geometries are verified on the first 2,353 rows. Background rows have no copied occurrence IDs, source-row IDs or event dates; `paired_presence_source_row` links each background to its conditioning source row. The five accepted integration GeoParquets are checked before and after by SHA-256.

The 1:1 ratio does not represent real-world prevalence. Background label 0 is not absence. The 2020–2026 rows use the SSP245 2020 slice. Future modelling requires group review, taxonomic/target decisions and spatially separated validation that groups shared cells across taxa and periods. No feature selection, imputation, training table, model, or evaluation was generated.

D-055 archive evidence: [manifest](2026-10-16-presence-background-archive-manifest.json). The superseded nested-column D-056 artifact is preserved under `data/interim/pseudo_absence/archive/d056_nested_columns` and listed in [its archive manifest](2026-10-16-nested-paired-background-archive-manifest.json).
See [D-056](2026-10-16-decision-paired-presence-background.md), the [data dictionary](2026-10-16-full-population-presence-background-data-dictionary.md) and [provisional evaluation plan](2026-10-16-full-population-presence-background-evaluation-plan.md).

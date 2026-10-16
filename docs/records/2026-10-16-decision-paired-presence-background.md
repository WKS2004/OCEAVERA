# Decision D-056 — Full-population long-format presence/background construction

- **Date:** 16 October 2026
- **Status:** Implemented and technically verified. Group approval of the modelling population, accessible domain, comparison design and target interpretation remains open.
- **Revision:** The user replaced the earlier nested-column layout with one positive and one separate background row per Policy B observation. The earlier nested-column dataset and supporting records are preserved byte-for-byte in the D-056 archive.
- **Supersedes:** The three-taxon, 338-row experimental construction recorded in D-055. D-055 remains historically accurate.

## Decision

Script 10 preserves all 2,353 Policy B observations as positive label-1 rows, then appends 2,353 separate sampled marine background rows with label 0. The result is a 4,706 × 527 long-format GeoParquet: the first 2,353 rows are unchanged source observations, and the next 2,353 rows are background examples. Label 0 is not a confirmed species absence. This 1:1 construction ratio does not estimate real-world prevalence.

All 519 original field definitions remain in their original order. Eight fields are appended: presence_background_label, sample_type, target_taxon_key, paired_presence_source_row, eligible_species_level_ml, ml_eligibility_reason, background_sampling_method and sample_id. Incomplete taxonomic and environmental records are retained. Taxonomic identifiers on background rows are conditioning information for the paired target only; they do not claim an occurrence at the sampled point.

Use seed 20261016. Sample without replacement from raster-cell centres strictly inside the validated GSHHG water polygon, with finite values for all six core predictors. Exclude every cell occupied by any Policy B observation and prevent background-cell reuse across all periods, taxa and source rows. Match each background to its source observation period: 2000–2009 uses baseline 2000, 2010–2019 uses baseline 2010 and 2020–2026 uses the SSP245 2020 projection slice. Stop if the full sample cannot be drawn.

The preliminary species-level eligibility flag requires a positive integer AphiaID, explicit species rank, complete source values for the six core predictors and a source raster-cell centre inside GSHHG water; Policy B already enforces absence=false and marine=true. Ineligible records remain in the candidate population. This technical screen does not verify taxonomy or establish sample adequacy.

## Measured result

The current output and detailed JSON evidence are in the [construction report](2026-10-16-full-population-presence-background-construction.md) and [machine-readable report](2026-10-16-full-population-presence-background-construction.json).

| Measure | Result |
| --- | ---: |
| Policy B source | 2,353 rows × 519 columns |
| Long-format output | 4,706 rows × 527 columns |
| Positive / background rows | 2,353 / 2,353 |
| Valid AphiaID rows / distinct valid AphiaIDs | 2,353 / 614 |
| Explicit species-rank rows / distinct species-rank AphiaIDs | 2,009 / 501 |
| Preliminary eligible / ineligible positive rows | 1,729 / 624 |
| Distinct occupied / background grid cells | 362 / 2,353 |
| Positive/background cell overlap | 0 |
| Environmental definitions | 382 |
| Positive / background non-null environmental values | 714,199 / 805,680 |
| Background source comparisons | 898,846 positions; 0 numerical or null/fill mismatches |
| GeoParquet | 1.1.0, WKB Point, EPSG:4326, ZSTD |
| Output size / SHA-256 | 9,412,505 bytes / 234177bf3641856cdd10b425f2da957a27210f876d31092ba715a53cee7a429f |

| Period | Positives | Backgrounds | Candidate pool at draw | Source slice |
| --- | ---: | ---: | ---: | --- |
| 2000–2009 | 376 | 376 | 24,175 | baseline 2000 |
| 2010–2019 | 596 | 596 | 23,799 | baseline 2010 |
| 2020–2026 | 1,381 | 1,381 | 23,203 | SSP245 2020 |

There are 300 repeated valid species/AphiaID × cell × period combinations involving 920 positive rows (620 rows beyond one per combination). Across all taxa, 2,099 source rows share a cell and period with another row. They remain in the output and are not independent observations.

The geographic and depth summaries show a material difference between the sampled domain and the occurrence locations: median longitude is 80.290°E for positives and 81.925°E for backgrounds; median latitude is 7.112°N and 6.375°N, respectively. Median source bathymetry is −15.9 m for positive rows with a value and −3,771.6 m for backgrounds. Broad uniform water-cell sampling therefore creates a strong depth contrast that could make classification artificially easy. The sampling domain and bias treatment require scientific review before modelling.

## Verification and limits

Script 10 checked the actual NetCDF time mappings and 106 source products across 1,012 catalogue mappings. Read-back comparison covered all 898,846 background environmental feature positions with zero numerical mismatches, zero null/fill discrepancies and maximum absolute difference 0. All six core background predictors are complete. The remaining source missing values and scientific quarantines remain null; no imputation or fabricated occurrence/event metadata was added to background rows.

All source values and original Point geometries in the first 2,353 rows were checked against the 2,353 × 519 input. The two fields that require background nulls use nullable output types: integration_source_row becomes nullable Int64 and marine_uncertainty_verified becomes nullable Boolean; the positive-row values remain exact. The five accepted integration GeoParquets have matching before/after SHA-256 fingerprints.

The previous nested-column D-056 output and its supporting records are preserved under data/interim/pseudo_absence/archive/d056_nested_columns/, with checksums in the [archive manifest](2026-10-16-nested-paired-background-archive-manifest.json). The earlier D-055 data and reports remain preserved under data/interim/pseudo_absence/archive/d055_three_species/ with their [archive manifest](2026-10-16-presence-background-archive-manifest.json).

This is a complete construction candidate, not a deduplicated species-level modelling table. A later approved stage must define the target population and accessible area, review environmental and depth comparability, address OBIS effort bias, prevent shared grid cells from leaking across validation folds and decide how to handle repeated positives. No feature selection, imputation, model training or evaluation was performed.

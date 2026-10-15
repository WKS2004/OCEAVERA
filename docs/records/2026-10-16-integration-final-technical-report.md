# OCEAVERA — Final integration technical and scientific report

> **Historical D-053 evidence:** the marine and grid counts in this report describe the former strict uncertainty-footprint policy. D-054 replaced those four derived outputs with Policy B water-centre candidates. The original strict-policy temporal, coverage, marine and grid reports are preserved as byte-verified `*-strict-policy.*` files. See the [current D-054 execution report](2026-10-16-policy-b-execution-report.md).

- **Date:** 16 October 2026 (Asia/Colombo)
- **Status:** CONDITIONAL PASS; all requested processing stages completed
- **Decision:** [D-053](2026-10-16-decision-final-integration-completion.md)
- **Evidence basis:** current GeoParquets, original NetCDF files, manifests, independent checks, actual test output and executed notebook

## A — Executive implementation status

**CONDITIONAL PASS — the requested processing pipeline has completed.** All five interim GeoParquets were produced and read back. No processing stage remains blocked.

Confirmed fixes: unsafe near-epoch date-unit inference; blind historical Kelvin conversion; publication of unresolved temperature ranges and cloud-fraction standard deviations; absent reusable marine reference; missing positional-confidence handling and taxonomy exclusion counts.

The original NetCDF semantic defects cannot be repaired responsibly from the evidence available. Their affected values are quarantined as null while all 382 columns and immutable source data remain available. There are 709 retained observations with known marine uncertainty footprints and 590 retained with explicitly unknown uncertainty.

Basic quality EDA and species eligibility review can proceed conditionally. These are not training-ready data. No species selection, feature selection, pseudo-absence construction, preprocessing, modelling or deployment was performed.

## B — Files changed and execution evidence

Modified processing files: `src/data_preparation/08_integrate_spatiotemporal_data.py` and `src/data_preparation/09_filter_and_grid_data.py`. Modified tests: `tests/test_integration_spatial.py` and `tests/test_filter_and_grid_data.py`. No upstream intake or cleaning implementation was changed or rerun.

Updated active guides: README.md, CONTRIBUTING.md, PROJECT_REQUIREMENTS.md, src/README.md, data/README.md, docs/README.md, docs/data/data-storage-and-provenance.md, docs/ml/ml-workflow-and-evidence-gates.md, docs/project/decision-register.md, docs/project/repository-readiness-and-alignment.md and notebooks/README.md. D-053, this report, current run/verification records, source/date/integrity evidence, contributor logs and the branch notebook record actual work. Prior reports and scripts are preserved in 2026-10-16-pre-completion-evidence.json. The worktree had extensive earlier changes; no commit was made.

The integrated output directory contained no GeoParquets at the start of this task. The five affected outputs were regenerated from the existing cleaned OBIS input and unchanged Bio-ORACLE sources. The GSHHG source archive and prepared reference were added. Original source files were preserved. Exactly two main processing scripts remain.

Runtime: existing WSL Ubuntu_New OCEAVERA Python 3.14.8; NumPy 2.5.4, pandas 3.0.6, netCDF4 1.7.4, GeoPandas 1.2.0, PyArrow 26.0.0, pyproj 3.8.0. No package/environment operation was performed. requirements.txt now explicitly pins the already installed pyproj dependency used directly for geodesic calculations.

| Command | Exit status |
| --- | --- |
| python src/data_preparation/08_integrate_spatiotemporal_data.py | 0 |
| python src/data_preparation/09_filter_and_grid_data.py | 0 |
| python -m unittest discover -s tests -v | 0 |
| python -m compileall -q src tests | 0 |
| python -m pip check | 0 |
| git diff --check | 0 |
| python .agents/scripts/validate_agent_resources.py | 0 |

Script 08's terminal completion and manifest/read-back evidence were observed; a complete raw stdout file was not retained. Script 09 reuse, tests, compilation, dependency and repository output files are linked by the execution JSON. Independent environmental/integrity checks and notebook execution also completed successfully.

Routine commands require no flags:

```bash
python src/data_preparation/08_integrate_spatiotemporal_data.py
python src/data_preparation/09_filter_and_grid_data.py

```

Script 09 does not import/execute Script 08, reopen environmental NetCDF files, or repeat environmental extraction. It reads the completed GeoParquet, its manifest, and the reusable geography reference. A second normal execution confirmed reference reuse; no download or reference preparation ran again.

## C — Complete dataset inventory

| Dataset | Rows | Columns | Bytes | Geometry | Read-back |
| --- | --- | --- | --- | --- | --- |
| full | 23,371 | 513 | 7,866,289 | Point | PASS |
| temporal | 9,681 | 514 | 5,344,561 | Point | PASS |
| marine | 1,299 | 518 | 1,449,806 | Point | PASS |
| grid | 1,299 | 519 | 1,451,815 | Point | PASS |
| summary | 667 | 391 | 818,861 | Polygon | PASS |

**full**: `data/interim/integrated/full/integrated_observations.parquet`

SHA256: `34e756d9fa0d5478da14b6a2d627c16076c486d8e43317363d387d69a661ee34`

**temporal**: `data/interim/integrated/temporal/observations_2000_2026.parquet`

SHA256: `6669327ec1aba406bf8aa8346dc743d1ab721a1237c0266705119881cc21479a`

**marine**: `data/interim/integrated/marine/marine_observations.parquet`

SHA256: `4b7d4f1dacb7147d03d2e9db208741e73126a180404c9a7a173e35cfb55f0a6b`

**grid**: `data/interim/integrated/gridded/grid_observations.parquet`

SHA256: `db57dc3b1836eae5af872633fb7627b77209cf3875adca75c7e4bef2e31512c8`

**summary**: `data/interim/integrated/gridded/species_cell_period_summary.parquet`

SHA256: `d767b245682c681325133cf6e4015e58bb921930f82ee616d7426f86c1b9ebc0`

All five files exist, use EPSG:4326, GeoParquet 1.1.0, WKB geometry and ZSTD compression. Missing and invalid geometries: zero in every output. Generated integration_source_row identities are unique: full 23,371; temporal 9,681; marine/grid 1,299 each. Original occurrenceID values remain unchanged: 3,071 are blank, 20,300 are nonblank and 20,242 nonblank IDs are distinct, leaving 58 repeated-ID occurrences beyond the unique count. Duplicate source-row identities: zero. Summary observation identity is not applicable; its 667 species/cell/period keys are unique.

The full schema has 112 original OBIS fields, 382 environmental columns, 18 integration metadata fields and geometry. There are 965 occupied source cells before filtering. All 2,617,552 original field positions and 23,371 original-coordinate geometries matched independently. Downstream preserved-field mismatch counts are zero.

The summary binary fingerprint changed on the reuse run; its current fingerprint above was refreshed. All 254,794 summary environmental positions, group counts and cell polygons were independently rechecked. Byte identity across rewrites is not claimed.

## D — Environmental feature catalogue

Available products: **356**. Selected/inspected: **106 = 55 baseline + 50 SSP245 + 1 terrain**. Distinct source variables: **139**; output environmental definitions: **382**.

Source availability: 300 features have historical and SSP245 counterparts; 30 are historical-only; 42 SSP245-only; 10 static. All definitions remain in the catalogue. Current scientifically retained counts are 334 per historical slice and 350 for SSP245. Seven columns have some quarantined periods; two are entirely null: bio_oracle__tas_range__depthsurf and bio_oracle__clt_sd__depthsurf. The five absolute tas columns retain SSP245 values.

| Family | Variables | Features | Depths | Statistics union | Source availability | Final units | Concern |
| --- | --- | --- | --- | --- | --- | --- | --- |
| area | 1 | 1 | benthic | static | 1 static | m2 | Static; not marine-location proof |
| aspect | 1 | 1 | benthic | static | 1 static | degree | Static; not marine-location proof |
| bathymetry | 3 | 3 | benthic | max, mean, min | 3 static | m | Static; not marine-location proof |
| chl | 7 | 25 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range, sd | 18 historical-only, 6 both, 1 SSP245-only | mg m-3 | Depth/ecological suitability still to review |
| clt | 7 | 7 | surf | ltmax, ltmin, max, mean, min, range, sd | 6 both, 1 SSP245-only | 1 | sd quarantined |
| coastline | 1 | 1 | benthic | static | 1 static | 1 | Static; not marine-location proof |
| dfe | 7 | 28 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range, sd | 24 both, 4 SSP245-only | MMol' 'M-3 | Unit notation requires review |
| kdpar_mean | 6 | 6 | surf | ltmax, ltmin, max, mean, min, range | 6 historical-only | m-1 | Depth/ecological suitability still to review |
| landmass | 1 | 1 | benthic | static | 1 static | 1 | Static; not marine-location proof |
| mlotst | 7 | 7 | surf | ltmax, ltmin, max, mean, min, range, sd | 6 both, 1 SSP245-only | m | Depth/ecological suitability still to review |
| no3 | 7 | 28 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range, sd | 24 both, 4 SSP245-only | MMol' 'M-3 | Unit notation requires review |
| o2 | 7 | 28 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range, sd | 24 both, 4 SSP245-only | MMol' 'M-3 | Unit notation requires review |
| par_mean | 6 | 6 | surf | ltmax, ltmin, max, mean, min, range | 6 historical-only | einstein/m2/day | Depth/ecological suitability still to review |
| ph | 7 | 28 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range, sd | 24 both, 4 SSP245-only | 1 | Depth/ecological suitability still to review |
| phyc | 7 | 28 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range, sd | 24 both, 4 SSP245-only | MMol' 'M-3 | Unit notation requires review |
| po4 | 7 | 28 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range, sd | 24 both, 4 SSP245-only | MMol' 'M-3 | Unit notation requires review |
| si | 7 | 28 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range, sd | 24 both, 4 SSP245-only | MMol' 'M-3 | Unit notation requires review |
| siconc | 7 | 7 | surf | ltmax, ltmin, max, mean, min, range, sd | 6 both, 1 SSP245-only | 1 | Depth/ecological suitability still to review |
| sithick | 7 | 7 | surf | ltmax, ltmin, max, mean, min, range, sd | 6 both, 1 SSP245-only | m | Depth/ecological suitability still to review |
| slope | 1 | 1 | benthic | static | 1 static | degree | Static; not marine-location proof |
| so | 7 | 28 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range, sd | 24 both, 4 SSP245-only | 1e-3, PSU | PSU / 1e-3 statistic units retained |
| swd | 6 | 24 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range | 24 both | degree | Depth/ecological suitability still to review |
| sws | 6 | 24 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range | 24 both | m s**-1 | Depth/ecological suitability still to review |
| tas | 7 | 7 | surf | ltmax, ltmin, max, mean, min, range, sd | 6 both, 1 SSP245-only | degree_C | Baseline absolute values and all ranges quarantined |
| terrain_ruggedness_index | 1 | 1 | benthic | static | 1 static | 1 | Static; not marine-location proof |
| thetao | 7 | 28 | max, mean, min, surf | ltmax, ltmin, max, mean, min, range, sd | 24 both, 4 SSP245-only | degree_C | Depth/ecological suitability still to review |
| topographic_position_index | 1 | 1 | benthic | static | 1 static | 1 | Static; not marine-location proof |

Depth abbreviations surf/min/mean/max denote the actual product variants; benthic denotes static terrain. Statistics shown are the family union, not a promise that every depth/time combination exists. One column represents each variable/statistic/depth definition; decades are not duplicated into separate columns. Full combinations, original metadata, source hashes and quarantine reasons are in the machine-readable variable catalogue. degree_C is the target unit for quarantined temperature columns; a null is not a scientifically established Celsius measurement.

## E — Temperature investigation and corrections

**Root cause: the original downloads already contain the value/metadata conflict.** All 106 selected raw and cleaned files have equal SHA256 hashes. Script 07 performs structural/numerical validation and retains byte-identical payloads; it did not convert these temperatures.

The temperature variables are float64, with _FillValue=-9999.9 and no scale_factor/add_offset. Original stored numerical samples therefore equal decoded samples; this is not a packed-data decoding problem. netCDF4 masking/scaling is enabled once. No second packing transform is applied.

| Variable / actual source period | Original NetCDF | Cleaned NetCDF | Final GeoParquet | Final unit | Explanation |
| --- | --- | --- | --- | --- | --- |
| tas_ltmax / baseline_2000 | 27.84680977 | 27.84680977 | null | degree_C | Source semantics unresolved; null quarantine |
| tas_ltmin / baseline_2000 | 25.71888241 | 25.71888241 | null | degree_C | Source semantics unresolved; null quarantine |
| tas_max / baseline_2000 | 28.17973782 | 28.17973782 | null | degree_C | Source semantics unresolved; null quarantine |
| tas_mean / baseline_2000 | 26.72473488 | 26.72473488 | null | degree_C | Source semantics unresolved; null quarantine |
| tas_min / baseline_2000 | 25.16386592 | 25.16386592 | null | degree_C | Source semantics unresolved; null quarantine |
| tas_range / baseline_2000 | -270.13412811 | -270.13412811 | null | degree_C | Source semantics unresolved; null quarantine |
| tas_ltmax / ssp245_2020 | 27.97352157 | 27.97352157 | 27.97352157 | degree_C | Original declared Celsius; identity |
| tas_ltmin / ssp245_2020 | 26.05242079 | 26.05242079 | 26.05242079 | degree_C | Original declared Celsius; identity |
| tas_max / ssp245_2020 | 29.49139283 | 29.49139283 | 29.49139283 | degree_C | Original declared Celsius; identity |
| tas_mean / ssp245_2020 | 26.97555751 | 26.97555751 | 26.97555751 | degree_C | Original declared Celsius; identity |
| tas_min / ssp245_2020 | 24.85559091 | 24.85559091 | 24.85559091 | degree_C | Original declared Celsius; identity |
| tas_range / ssp245_2020 | -268.51419808 | -268.51419808 | null | degree_C | Source semantics unresolved; null quarantine |

The source-row IDs, raster indices, packed samples, original unit labels and before-correction rule results are stored in the lineage JSON for these same examples. Baseline raw tas_mean around 26–27 declares K. The preceding integration subtracted 273.15, producing approximately -246 degrees Celsius. Cleaning did not perform a first conversion: the source-label contradiction and blind integration conversion caused the published failure.

For each actual 2000, 2010 and SSP245 2020 slice, 24,503 valid original cells satisfy tas_range + 273.15 = tas_max - tas_min. Maximum residuals are 0, 0 and 2.2737367544323206e-13 respectively. Both historical and projected negative ranges are already present in the downloaded files.

Applied treatment: quarantine historical absolute tas, all tas_range and clt_sd values as null; preserve source files, columns, original units, per-period reasons and the catalogue. Do not add 273.15 to fabricate a replacement range. SSP245 absolute Celsius and tas_sd remain unchanged. There are 32,222 quarantined row-feature positions, of which 15,492 had non-null source values. Tests cover quarantine, source-array non-mutation, future Celsius identity, and automatic packing/masking including a legitimate zero.

## F — Other environmental metadata issues

- **clt_sd:** original and cleaned metadata both declare units=1, long_name=Standard deviation TotalCloudFraction. The actual SSP245 2020 ROI spans 1.4665576679–2.1197698125. This conflicts with a fraction-scale standard deviation; the source does not establish a trustworthy correction. All values are quarantined. Retain the definition for future publisher review.
- **Oxygen, nitrate, dissolved iron and silicate:** the original unit string is MMol' 'M-3. The same string and numerical values survive cleaning unchanged. It resembles a concentration notation, but its intended scale/capitalisation must not be guessed. No numerical conversion was performed. Missing or incomplete standard_name metadata is retained in the source-slice ledger. Review units and ecological relevance before these enter a model.
- **Salinity and other definitions:** source PSU and 1e-3 labels belong to different statistics; they are retained per feature rather than merged by numerical conversion. Shared feature/depth/statistic definitions and declared units are checked, but this does not independently prove ecological comparability.
- **Baseline windows:** selected titles comprise 28 products ending in 2018, 17 in 2019 and 10 in 2020. Actual time coordinates are 2000 and 2010. Exact averaging-window boundaries for each coordinate are not consistently established. Cleaning did not rewrite those labels.


The confirmed project defect was blind temperature interpretation. The remaining source labels/statistics need publisher interpretation or evidence during later feature review; they do not block unrelated extraction and filtering.

## G — Temporal data integrity

| Classification | Records |
| --- | --- |
| Before 2000 | 10,386 |
| 2000–2009 | 651 |
| 2010–2019 | 2,564 |
| 2020–2026 | 6,466 |
| After 2026 | 0 |
| Missing/invalid | 3,282 |
| Genuine ambiguity | 22 |
| Total eligible | 9,681 |
| Total excluded | 13,690 |

OBIS numeric date_start/date_mid/date_end always use epoch milliseconds, including negative, zero, small positive and four-digit numeric values. year/date_year are year fields; a year=0 placeholder is invalid. ISO dates and intervals remain supported. Original OBIS date fields are unchanged.

Compared with the immediately preceding parser: 266 false ambiguities now resolve correctly to pre-2000 dates; one previously accepted year=0 placeholder becomes missing/invalid. Thus 267 resolved-year/eligibility labels change, but **zero environmental periods and zero retained/excluded observation identities change**. There are 22 genuine conflicts left: year=1965 contradicts the event interval 1962–1964 and its midpoint evidence. They stay in the full archive and outside the temporal output.

Examples: source row 133 uses -8121600000 ms and resolves to 1969, not 1712; row 284 uses 1123200000 ms and resolves to 1970, not 2005; row 469 uses 8121600000 ms and resolves to 1970, not 2227. Row 21347's year=0 now remains unknown. All changed and remaining ambiguous rows are in the date evidence JSON.

The manifest also retains a different historical comparison: against the older first-parseable-field implementation, 429 resolved years and two period assignments differ (2000-slice count 653 to 651; 2010-slice count 2,562 to 2,564). These are not the immediate-parser change counts above.

Single years 1999/2027 are outside the supported range. Supported boundaries are 2000, 2010, 2020 and the inclusive end 2026. Without consistent point-year evidence, an interval must fit one entire supported period; cross-period intervals are ambiguous. Conflicting evidence is never silently treated as a verified year. Tests cover each boundary and missing/conflicting cases. An independent resolver checked all 23,371 source records and matched the saved year, period and eligibility with zero discrepancies.

## H — Environmental extraction correctness

**PASS for source agreement and quarantine enforcement.** Reader: netCDF4 1.7.4. The independent method imports neither processing script. It opens the original publisher-delivered NetCDF files directly, verifies raw/cleaned byte hashes, reads actual time axes and declared masking/scaling, samples distinct occupied cells and expands the results back to observation rows.

| Measure | Positions |
| --- | --- |
| All row-feature positions | 8,927,722 |
| Source-period positions before quarantine | 3,369,132 |
| Applicable retained positions | 3,336,910 |
| Non-null numerical values compared | 1,627,796 |
| Total null positions | 7,299,926 |
| Source masks among retained definitions | 1,709,114 |
| Deliberate quarantine positions | 32,222 |
| Unsupported observation-period positions | 5,229,580 |
| Unavailable feature-period positions | 329,010 |
| Legitimate zeros | 139,457 |
| Numerical mismatches | 0 |
| Null mismatches | 0 |
| Coordinate mismatches | 0 |

106 original products and 1,012 distinct product/variable/actual-time slices were checked, including static terrain. The complete per-column counts and explicit source-slice ledger are saved. Maximum numerical difference: **0**. Distinct cell samples summed across feature/period comparisons: 322,576; full archive occupied cells: 965. Source axes and stored cell centres agreed for every source product. An independent nearest-centre search from all 23,371 original coordinates reproduced the raster row, column and stable cell ID with zero mismatches. The grid spacing is approximately 0.05 degrees; point matching inherits that spatial approximation.

Null categories reconcile: 1,709,114 retained-source masks + 32,222 quarantines + 5,229,580 unsupported-date positions + 329,010 unavailable-feature positions = 7,299,926. Original source masking including quarantined definitions is 1,725,844; this overlaps quarantines and is not an additional category.

Actual source years 2000/2010 are used historically and only SSP245 2020 for 2020–2026. Terrain uses the source's static/Benthic context; 1970 is not an observation date. Current policy leaves all features, including terrain, null on temporally ineligible rows. The arrays remain source grids; no global raster was flattened.

This comparison validates numerical lineage and deliberate quarantine. It does not establish publisher semantics, ecological relevance, marine location, observed annual conditions or the correctness of the SSP scenario assumption. The full verification program is retained as text inside its JSON record for independent reproduction.

## I — Environmental completeness

| Period | Records | Complete | Partial | No values | Non-null positions | Null positions | Retained feature definitions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2000-2009 | 651 | 331 | 109 | 211 | 146,851 | 101,831 | 334 |
| 2010-2019 | 2,564 | 872 | 200 | 1,492 | 357,848 | 621,600 | 334 |
| 2020-2026 | 6,466 | 2,807 | 403 | 3,256 | 1,123,097 | 1,346,915 | 350 |

Historical eligible observations total 3,215; SSP245-assigned observations total 6,466. Across the eligible table, 4,010 are complete, 712 partial and 4,959 have no retained source values at their matched cells. Completeness is relative to applicable, non-quarantined definitions (334 historical, 350 SSP245), not all 382 columns.

Historical-only unavailability includes the PAR and kdpar statistics and some chlorophyll depth variants. Projected-only statistics, particularly sd, have no historical counterpart. Additional missingness is source fill/masking at matched cells; a successful raster match does not imply usable measurements. The per-column JSON distinguishes these causes.

No feature was automatically selected for modelling. All 382 definitions remain inspectable, but two whole columns and additional historical temperature periods are intentionally null. Later features must be chosen for species ecology, depth, units, missingness and validation design.

## J — Geographical quality and marine filtering

Flags: full ON_LAND=8,000, MARINE_UNSURE=51, overlap=42. Temporal ON_LAND=6,423, MARINE_UNSURE=41, overlap=40. Flags parse as exact JSON-array tokens; all arrays are valid. The taxonomic marine attribute and Bio-ORACLE non-null cells are not used as marine-location proof.

| Period | Flag group | Records | Complete | Partial | No values |
| --- | --- | --- | --- | --- | --- |
| 2000-2009 | ON_LAND | 271 | 123 | 0 | 148 |
| 2000-2009 | MARINE_UNSURE only | 1 | 1 | 0 | 0 |
| 2000-2009 | Neither | 379 | 207 | 109 | 63 |
| 2010-2019 | ON_LAND | 1,778 | 351 | 0 | 1,427 |
| 2010-2019 | MARINE_UNSURE only | 0 | 0 | 0 | 0 |
| 2010-2019 | Neither | 786 | 521 | 200 | 65 |
| 2020-2026 | ON_LAND | 4,374 | 1,398 | 15 | 2,961 |
| 2020-2026 | MARINE_UNSURE only | 0 | 0 | 0 | 0 |
| 2020-2026 | Neither | 2,092 | 1,409 | 388 | 295 |


There are 3,257 temporal candidates with neither flag, not automatically marine records. Of these, 2,353 pass the independent water-centre test and 904 fail it. Across all temporal records, 2,815 centres are inside water, including flagged observations still excluded by the quality policy.

Exclusive decisions reconcile to all 9,681 temporal records:

| Decision | Records |
| --- | --- |
| ON_LAND | 6,423 |
| retained_unknown_uncertainty | 590 |
| known_uncertainty_crosses_coast | 1,025 |
| outside_marine_water | 904 |
| retained_known_uncertainty_marine | 709 |
| known_uncertainty_outside_reference | 29 |
| MARINE_UNSURE | 1 |

Retained: **1,299**. Excluded: **8,382 = 6,423 ON_LAND + 1 MARINE_UNSURE-only + 904 geometry + 1,025 known coast/land uncertainty + 29 known footprints outside reference coverage**. Invalid-coordinate, malformed-flag and exact-boundary exclusions are zero in this run. Every retained observation has an original Point and valid cell.

Known positive uncertainties use WGS84 geodesic footprints, not degree buffers. The production approximation has 360 bearings and slight circumradius inflation. A separate 720-bearing check reproduced all 9,681 decisions. There are 709 known footprints entirely marine under the reference and 590 retained points with unknown uncertainty. The known-confidence-only sensitivity subset would therefore contain 709 rather than 1,299 records. Unknown uncertainty is retained explicitly, never assumed zero; known ambiguous footprints are excluded.

Full-source uncertainty availability: 10,964 numeric; 12,407 missing/non-numeric. Positive range 1–2,753,412 m; median 2,088 m, p90 100,000 m, p95 669,329 m. Marine observations occupy 188 cells. Their positional-confidence fields must accompany later analysis.

## K — Marine reference provenance

Publisher: Paul Wessel (SOEST, University of Hawai'i) and Walter H. F. Smith (NOAA). Dataset: GSHHG, version 2.3.7, released 15 June 2017. Licence: GNU Lesser General Public License as distributed with the source.

Official download: [GSHHG shapefile archive](https://ftp.soest.hawaii.edu/gshhg/gshhg-shp-2.3.7.zip); [publisher documentation](https://www.soest.hawaii.edu/wessel/gshhg/); [NOAA documentation](https://www.ngdc.noaa.gov/mgg/shorelines/shorelines.html). Citation DOI: [10.1029/96JB00104](https://doi.org/10.1029/96JB00104).

Retrieved UTC 2026-10-15T19:50:13.210656+00:00 (16 October in Asia/Colombo). Archive: `data/raw/geography/gshhg/gshhg-shp-2.3.7.zip`, **149,157,845 bytes**, SHA256 `8dbbe7e071e77e9e75f2d639239099ebca8d5c16d6a07df8169729d49f15cf41`. Original archive is unchanged.

Selected resolution: full (f), not the simplified high-resolution derivative. Study extent west/south/east/north: 77.02333333333333, 2.5665, 85.23291666666667, 11.44883333333333. These are D-048's existing collection bounds; no EEZ or final modelling-domain restriction was introduced.

Within this extent, L1 has 216 polygons, L2 has 11, L3/L4 have none. L1 land outer shells are unioned and subtracted from the rectangle; enclosed inland waters remain excluded with land. The hierarchy is inspected rather than treating lakes as ocean. No source geometry repair or Bio-ORACLE-derived mask is used.

Prepared file: `data/interim/geography/sri_lanka_marine_water.gpkg`; Polygon, EPSG:4326, 442,368 bytes; SHA256 `ef21fe8791b16e314a441480781f9e5e8cb2a47bf3e9030f57e6b2bc0f02ce8e`. Geometry is valid and the GeoPackage read-back equals the prepared water. All 16 location/topology sanity checks passed, including offshore, mainland, Delft Island, an inland-water location, all 11 L2 representatives and an exact source coastline point.

Ordinary Script 09 finds the prepared file and provenance automatically and verifies its checksum/status/scope. If absent but the matching official archive is local, it prepares once. Routine runs do not access the network. Missing or invalid sources produce a clear blocker. Optional mask/citation overrides remain available.

Limitations: the 2017 shoreline is not a contemporary survey; small islands, lagoons, reclamation and local georegistration can differ. Full resolution does not imply uniform metre accuracy. The checks verify topology and sample classification, not surveyed coastal precision. Reference coverage ends at the collection rectangle.

## L — Grid categorization

| Period | Individual rows | Occupied cells | Species-rank records | Ungrouped taxonomy | Summary rows |
| --- | --- | --- | --- | --- | --- |
| 2000-2009 | 328 | 56 | 151 | 177 | 69 |
| 2010-2019 | 237 | 59 | 170 | 67 | 141 |
| 2020-2026 | 734 | 98 | 685 | 49 | 457 |

Total: 1,299 individual records; 188 occupied cells; 358 source species-rank Aphia identifiers; 667 summary rows. The grouped occurrence_record_count sums to **1,006**, exactly the eligible species-rank observations. The other 293 remain in the individual table and are explicitly counted as ungrouped. Records without valid cells: zero.

Grid IDs are stable row*width+column identities from persisted full axes. Full raster-cell polygons may straddle land and sea; the marine verification applies to observation points and known uncertainty footprints. All original Point geometries, source fields, environmental columns and temporal metadata are preserved. Every one of the 667 actual cell Polygons independently matches the axis midpoint edges. Summary keys/counts and all 254,794 summary environmental positions reconcile to saved observations.

All current grouped identifiers use source AphiaID with numeric syntax; nomenclatural acceptance was not re-queried from WoRMS. Counts preserve repeated OBIS records and are not population abundance. No species-count or occupied-cell threshold was imposed.

## M — Test and notebook results

Actual command: python -m unittest discover -s tests -v. **25 executed; 25 passed; 0 failed; 0 skipped.** Modules: test_filter_and_grid_data.py (11), test_integration_spatial.py (13), test_integration_geoparquet.py (1). Complete runner output is saved.

New coverage includes 1969/1970 negative/zero/small epochs; all environmental-period interval boundaries; quarantine and Celsius identity; known uncertainty crossing a synthetic land hole or reference boundary; geodesic metre distances; and default-reference reuse/checksum rejection. Existing tests cover masking/scaling once, legitimate zero, exact ON_LAND/MARINE_UNSURE exclusion, persisted axes, GeoParquet read-back, Script 09 independence and summary count reconciliation.

Python compilation: PASS. pip check: PASS, no broken requirements. Existing packages remain functional, demonstrated by both scripts, direct NetCDF verification and the notebook. Repository consistency status: **PASS**; exact command/output is recorded in the execution JSON when run.

Notebook: 21 cells, 13 Markdown and 8 code; execution counts 1–8, zero error outputs. It uses concise local read-only cells, Matplotlib/Seaborn plots, saved data and manifest tables. Default execution is offline and writes no dataset files; all five dataset hashes stayed unchanged. Root discovery was executed successfully from both the project root and notebook folder. Its contributor table is preserved; registration numbers remain exclusively there.

Independent checks additionally covered 23,371 source date resolutions, 2,617,552 OBIS fields, 23,371 original coordinates, 9,681 marine decisions and 667 grid polygons, all with zero final mismatches.

## N — Scientific limitations and evaluation readiness

**Integration correctness and modelling suitability are different decisions.** Retained measurements and quarantines now have verified numerical lineage; this is not an unconditional ecological acceptance.

SSP245 2020 is an assumed projection for 2020–2026 records, not annual observed conditions. Historical 2000/2010 layers are climatological summaries with varying nominal baseline end years. Features represent several depths/statistics and are not automatically appropriate for any species. Source temperature/cloud issues remain quarantined; concentration notation and other metadata need interpretation.

Marine classification depends on GSHHG shoreline quality and the collection rectangle. 590 retained records have unknown positional uncertainty; known geodesic footprints are still approximations relative to source geography. OBIS effort, repeated sampling, taxonomic quality, availability and observation bias remain. Missing occurrences do not establish absence, and recorded presence/background scores would not automatically be occurrence probabilities.

Readiness: basic EDA and species eligibility review—CONDITIONAL PASS using quarantines/confidence; feature selection—requires ecological/source and leakage review; pseudo-absence construction—NOT READY without species/domain/sampling/bias decisions; model training—NOT READY without targets/features/preprocessing/validation decisions. None of these later analytical tasks was started.

## O — Final acceptance matrix

| Area | Status | Evidence / limit |
| --- | --- | --- |
| Source preservation | PASS | 112 OBIS fields and original coordinates preserved; 106 raw/cleaned NetCDF pairs byte-identical. |
| Environmental extraction | PASS | Retained values, masked cells, zeros and intentional quarantines agree with original sources. |
| Temperature correctness | CONDITIONAL PASS | No fabricated correction; baseline absolute tas and all tas_range values remain quarantined pending publisher clarification. |
| Scientific unit consistency | CONDITIONAL PASS | Questionable clt_sd quarantined; concentration notation, salinity statistics and climatological windows require interpretation. |
| Temporal resolution | PASS | Field units fixed; 23,371 independently resolved source dates match; 22 genuine conflicts excluded. |
| Historical matching | PASS | Actual 2000/2010 coordinates used; averaging-window meaning remains a scientific limitation. |
| SSP245 matching | PASS | Only SSP245 2020 used for eligible 2020–2026 observations, explicitly as a projection assumption. |
| GeoParquet integrity | PASS | Five current outputs read back; geometry, CRS, compression, identities and values checked. |
| Geographical flags | PASS | Exact JSON tokens; ON_LAND and MARINE_UNSURE excluded; taxon marine attribute unused. |
| Independent marine verification | CONDITIONAL PASS | 1,299 water-centre observations retained; 709 known footprints marine, 590 unknown uncertainty explicitly retained. |
| Grid categorization | PASS | 1,299 Point records, stable cell IDs and 188 occupied cells. |
| Species-by-grid summaries | PASS | 667 Polygon groups reconcile to 1,006 species-rank records; 293 records ungrouped. |
| Independent source verification | PASS | 8,927,722 positions, 1,012 original-source slices, zero value/null/coordinate mismatches. |
| Automated tests | PASS | 25 executed, 25 passed, zero failures/skips. |
| Documentation | PASS | D-053, current guides, reports, evidence, logs and executed notebook; historical evidence preserved. |
| Overall pipeline completion | CONDITIONAL PASS | All five requested processing outputs completed. Source quarantines and geographic/temporal assumptions prevent unconditional scientific acceptance. |

## P — Files to upload into ChatGPT

Upload in the following usefulness order. The first two are the self-contained report and concise machine-readable summary; the detailed evidence provides per-column/source-slice traceability. Dataset files are locally retained and ignored by Git.

1. `docs/records/2026-10-16-integration-final-technical-report.md`
2. `docs/records/2026-10-16-integration-final-technical-report.json`
3. `docs/records/2026-10-16-independent-environmental-verification.json`
4. `docs/records/2026-10-16-source-lineage-investigation.json`
5. `docs/records/2026-10-16-integration-manifest.json`
6. `docs/records/2026-10-16-integration-variable-catalog.json`
7. `docs/records/2026-10-16-output-integrity-verification.json`
8. `docs/records/2026-10-16-date-correction-evidence.json`
9. `docs/records/2026-10-16-gshhg-marine-reference.json`
10. `docs/records/2026-10-16-spatial-grid-report-strict-policy.json`
11. `docs/records/2026-10-16-environmental-coverage-by-geography-and-period-strict-policy.json`
12. `docs/records/2026-10-16-independent-environmental-verification.md`
13. `docs/records/2026-10-16-environmental-coverage-by-geography-and-period-strict-policy.md`
14. `docs/records/2026-10-16-spatial-grid-report-strict-policy.md`
15. `docs/records/2026-10-16-marine-filter-blocker-strict-policy.md`
16. `docs/records/2026-10-16-temporal-filter-report-strict-policy.json`
17. `docs/records/2026-10-16-integration-execution-evidence.json`
18. `docs/records/2026-10-16-integration-unittest-output.txt`
19. `notebooks/branch_work/05_pipeline_data_integration_and_data_cleaning.ipynb`
20. `data/interim/integrated/full/integrated_observations.parquet`
21. `data/interim/integrated/temporal/observations_2000_2026.parquet`
22. `data/interim/integrated/marine/marine_observations.parquet`
23. `data/interim/integrated/gridded/grid_observations.parquet`
24. `data/interim/integrated/gridded/species_cell_period_summary.parquet`
25. `src/data_preparation/08_integrate_spatiotemporal_data.py`
26. `src/data_preparation/09_filter_and_grid_data.py`

For original-source review, additionally provide the cleaned-source manifest at data/interim/bio_oracle/cleaning/manifest.json and the specific original NetCDF files named in the source-lineage JSON. The complete 106-product verification does not require re-running the integration. Raw source payloads and the GSHHG archive remain local; sharing permissions and size should be considered when uploading.

Recommended next step: basic EDA and species eligibility review using the marine confidence columns and the scientifically retained feature definitions. Publisher clarification is still needed before releasing quarantined values. No further investigation prompt is required to understand the results recorded here.

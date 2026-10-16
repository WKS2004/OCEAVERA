# OCEAVERA — Feature Selection, Engineering and Preprocessing

**Status:** provisional candidates for review; no species, target, feature set or model is approved.

Frozen source: `data/interim/pseudo_absence/presence_background_candidates.parquet` — 4,706 × 527, SHA-256 `234177bf3641856cdd10b425f2da957a27210f876d31092ba715a53cee7a429f`. The source remains unchanged.

Derived GeoParquet: `data/interim/model_preparation/ml_candidates.parquet` — **2,308 × 26**, 250,215 bytes, SHA-256 `a7fceef9b925eda28bfc6ca9d3e00ddbe9a554aca2617ee31b1dfe0e3c47c148`; GeoParquet 1.1.0, EPSG:4326, ZSTD.

## Population and repeats

The 1,729 eligible positive observations are paired with 1,729 existing background rows. Eligibility excludes 624 positive and 624 paired background rows. Deduplication retains 1,154 positives and 575 fewer repeated taxon/cell/period positives, plus their matched backgrounds, yielding 2,308 rows. These are records, not independent cells.

Exclusion reasons below are nonexclusive: a row with multiple eligibility reasons contributes to each reason count.

| Label | Exclusion reason | Rows |
|---:|---|---:|
| 0 | missing_core_environment | 271 |
| 0 | source_cell_centre_not_marine | 324 |
| 0 | unverified_species_rank | 344 |
| 1 | missing_core_environment | 271 |
| 1 | source_cell_centre_not_marine | 324 |
| 1 | unverified_species_rank | 344 |

| Label | Eligible distinct taxa | Excluded distinct taxa |
|---:|---:|---:|
| 0 | 441 | 280 |
| 1 | 441 | 280 |

## Spatial split

Raster-centre blocks are 0.5° wide; selected seed: 20261026. Cross-partition cell overlap: 0; block overlap: 0.

| Partition | Rows | Row share | Presence rows | Background rows | Positive taxa | Positive cells | Blocks |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 1,604 | 69.5% | 803 | 801 | 351 | 156 | 182 |
| validation | 359 | 15.6% | 179 | 180 | 137 | 43 | 40 |
| test | 345 | 14.9% | 172 | 173 | 77 | 57 | 40 |

## Feature configurations

All 382 source Bio-ORACLE features were screened on training rows only. All-null training features: 2. The source audit has 7 quarantined feature definitions and 14 feature-period entries; the associated values were confirmed null and were not admitted as predictors.

| Configuration | Numeric environmental predictors | Features |
|---|---:|---|
| core_six | 6 | `bio_oracle__thetao_mean__depthsurf, bio_oracle__so_mean__depthsurf, bio_oracle__o2_mean__depthsurf, bio_oracle__chl_mean__depthsurf, bio_oracle__ph_mean__depthsurf, bio_oracle__bathymetry_mean__benthic` |
| core_plus_engineered | 9 | `bio_oracle__thetao_mean__depthsurf, bio_oracle__so_mean__depthsurf, bio_oracle__o2_mean__depthsurf, bio_oracle__chl_mean__depthsurf, bio_oracle__ph_mean__depthsurf, bio_oracle__bathymetry_mean__benthic, eng_water_depth_m, eng_log1p_water_depth, eng_temperature_salinity_interaction` |
| domain_expanded | 13 | `bio_oracle__thetao_mean__depthsurf, bio_oracle__so_mean__depthsurf, bio_oracle__o2_mean__depthsurf, bio_oracle__chl_mean__depthsurf, bio_oracle__ph_mean__depthsurf, bio_oracle__bathymetry_mean__benthic, eng_water_depth_m, eng_log1p_water_depth, eng_temperature_salinity_interaction, bio_oracle__no3_mean__depthsurf, bio_oracle__po4_mean__depthsurf, bio_oracle__slope__benthic, bio_oracle__mlotst_mean__depthsurf` |

`target_taxon_key` is a separate categorical condition for the shared multi-species model. It is not included in numeric feature counts. Optional candidates were admitted using training coverage only.

## Candidate feature missingness and ranges

Counts describe derived candidate rows before imputation. Zero is a valid value; missing values remain missing.

| Predictor | Missing rows | Exact zeros | Minimum | Maximum |
|---|---:|---:|---:|---:|
| `bio_oracle__thetao_mean__depthsurf` | 0 | 0 | 27.555834509517588 | 29.602479963979434 |
| `bio_oracle__so_mean__depthsurf` | 0 | 0 | 32.53213697983999 | 34.81164573925927 |
| `bio_oracle__o2_mean__depthsurf` | 0 | 0 | 198.2112911199182 | 204.13532744303834 |
| `bio_oracle__chl_mean__depthsurf` | 0 | 0 | 0.11044956397865428 | 0.9876996713886851 |
| `bio_oracle__ph_mean__depthsurf` | 0 | 0 | 8.008260405084942 | 8.065124749592488 |
| `bio_oracle__bathymetry_mean__benthic` | 0 | 30 | -4410.388671875 | 0.0 |
| `eng_water_depth_m` | 0 | 30 | -0.0 | 4410.388671875 |
| `eng_log1p_water_depth` | 0 | 30 | -0.0 | 8.391944810454575 |
| `eng_temperature_salinity_interaction` | 0 | 0 | 934.8561804654713 | 1019.8322516718964 |
| `bio_oracle__no3_mean__depthsurf` | 0 | 0 | 0.0033328266623189433 | 1.1154235671051138 |
| `bio_oracle__po4_mean__depthsurf` | 0 | 0 | 0.00737181385808847 | 0.21199668840494046 |
| `bio_oracle__slope__benthic` | 0 | 0 | 0.002144859064946179 | 11.22557670685472 |
| `bio_oracle__mlotst_mean__depthsurf` | 0 | 0 | 6.843409327364079 | 24.603948632032335 |

## Engineering and preprocessing

- `eng_water_depth_m` = `max(0, -bathymetry)`; source nulls stay null and zero depth remains valid.
- `eng_log1p_water_depth` = `log1p(eng_water_depth_m)`.
- `eng_temperature_salinity_interaction` = temperature × salinity; exploratory interaction only.
- Six `ColumnTransformer` templates were serialized and reloaded without fitting: median imputation, optional `StandardScaler`, and `OneHotEncoder(handle_unknown='ignore')` for species.

## Limitations

- One-to-one pseudo-backgrounds are NOT confirmed biological absences.
- SSP245 2020 projection is used as an assumption for 2020–2026 occurrences.
- Global background sampling is biased toward deep offshore cells; interpret scores carefully.
- Source-cell repeat observations are reduced only in derived modelling candidates.
- Spatial blocks prevent shared-cell leakage but do not fully remove spatial autocorrelation.
- Background/positive pairing links may cross geographic blocks; pair source IDs are never predictors.
- Many rare taxa are not independently supported across all splits; review support CSV.
- Unseen validation/test taxon categories receive all-zero one-hot encoding; do not evaluate unseen taxa as established suitability models.
- One-hot species identity and all environment variables must be supplied consistently at inference.
- No imputers, scalers, encoders, selectors or models have been fitted. Fit training-only inside each validation fold.
- No final ecological feature or species selection and no source data mutation occurred.

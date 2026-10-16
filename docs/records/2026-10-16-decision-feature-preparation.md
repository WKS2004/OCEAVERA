# D-058 — Provisional Feature Preparation and Leakage-Aware Spatial Partitions

- **Date:** 16 October 2026
- **Status:** Technical implementation completed and checks passed; the feature, target, species and evaluation proposals remain for shared review.
- **Decision owner:** Shared project review remains responsible for accepting the candidate population, features and evaluation design.
- **Scope:** Create a new derived candidate table and unfitted preprocessing templates from the frozen D-056 population. Preserve the source candidate, the five integrated GeoParquets and Scripts 08–11.

## Proposed treatment

1. Start from the accepted 4,706 × 527 long-format GeoParquet, whose recorded SHA-256 is `234177bf3641856cdd10b425f2da957a27210f876d31092ba715a53cee7a429f`.
2. Use the existing species-level eligibility field, retain one positive occurrence for each taxon, grid cell and environmental period, and retain its existing paired sampled-background row. Label 0 remains sampled background, not confirmed absence.
3. Assign the same raster-centre-derived 0.5° WGS84 block to records from the same block across taxa and periods. Propose deterministic train, validation and test partitions near 70/15/15, with no shared block or grid cell across partitions. Report where taxon support is too sparse.
4. Screen all 382 environmental fields using training rows only; respect the recorded integration quarantines and retain all original fields in the frozen source.
5. Publish three provisional numeric feature hypotheses: six core fields, core plus positive depth/log-depth/temperature-by-salinity engineering, and the domain-expanded set. Keep target taxon as a separate categorical condition for the proposed shared multi-species design.
6. Serialize six unfitted median-imputation templates with optional scaling and unknown-safe one-hot taxon encoding. Do not fit any transformation or model on project data.

## Rationale and limits

Deduplicating identical taxon/cell/period profiles avoids representing repeated occurrences as independent environmental samples in this derived modelling view while preserving all original observations in D-056. Global spatial blocks address direct shared-cell and block leakage; they do not remove all spatial autocorrelation. A sampled background is not a confirmed absence. The 2020–2026 environmental slice remains the SSP245 2020 projection assumption. No feature, species, target, accessible area, model or ecological interpretation is scientifically approved by this technical preparation.

## Evidence and review

The frozen source remained 4,706 × 527 with SHA-256 `234177bf3641856cdd10b425f2da957a27210f876d31092ba715a53cee7a429f`. Script 12 retained 1,154 positives and 1,154 paired backgrounds in a 2,308 × 26 GeoParquet. The selected split has 1,604 train, 359 validation and 345 test rows, with zero grid-cell/block crossover; 10 of 441 taxa meet the provisional support rule in all three partitions. All 382 fields were screened on training data, seven quarantined definitions across 14 periods remained null, and all six preprocessing configurations are unfitted. Notebook 08 executed nine Code cells and saved eight generated figure outputs. The full test suite passed 52 tests, compilation and dependency checks passed, and the repository validator and Git whitespace check passed. The detailed run evidence is in the [Script 12 summary](2026-10-16-feature-preprocessing-summary.json), [execution report](2026-10-16-feature-preprocessing-report.md), [feature decision log](2026-10-16-preprocessing-feature-log.md), [training-only feature screen](../../data/interim/model_preparation/feature_screen_train_only.csv), [taxon support table](../../data/interim/model_preparation/taxon_spatial_support.csv), [feature-set manifest](../../data/interim/model_preparation/feature_set_manifest.json) and [Notebook 08](../../notebooks/branch_work/08_pipeline_feature_selection_engineering_preprocessing.ipynb). These are technical findings only. Shared review remains required before model fitting or final selection.

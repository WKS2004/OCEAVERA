# Provisional evaluation plan for the full-population presence/background dataset

- **Status:** Planning guidance only. D-009 group review remains required; this plan does not approve a target, accessible area, split or model training.
- **Decision:** [D-056](2026-10-16-decision-paired-presence-background.md)
- **Dataset:** data/interim/pseudo_absence/presence_background_candidates.parquet
- **Format:** 4,706 long-format rows: 2,353 observed positives and 2,353 sampled background examples.

## Interpret the labels and population

The first 2,353 rows preserve Policy B observations and carry label 1. The next 2,353 rows are separately sampled marine background examples and carry label 0. Label 0 is not a confirmed absence. The 1:1 ratio is not real-world prevalence and cannot support prevalence claims or calibrated occurrence probabilities.

All source records remain, including non-species ranks and incomplete environmental rows. The preliminary species-level screen marks 1,729 positive records eligible and 624 ineligible, based on identifier, taxon rank, core-feature completeness and source cell-centre checks. This does not verify taxonomy, ensure independent observations or establish adequate sample size. Select a modelling population only after scientific review.

Backgrounds are uniform draws from marine water-cell centres with complete core predictors. All 362 occupied source cells were excluded globally; sampled cells are globally unique. Candidate pools before each period's draw were 24,175, 23,799 and 23,203. This broad water-domain sampling is not effort-corrected or a species-specific accessible-area estimate.

## Material comparability risks

Background and occurrence locations differ materially. Positive median bathymetry is −15.9 m among 2,082 rows with a value; background median bathymetry is −3,771.6 m. Median longitude and latitude are 80.290°E / 7.112°N for positives and 81.925°E / 6.375°N for backgrounds. A classifier could separate these sampling distributions rather than species habitat and may achieve misleadingly optimistic scores.

The positive source set contains 300 repeated valid species/AphiaID × cell × period combinations involving 920 rows; 620 rows exceed one record per combination. Across all taxa, 2,099 positive rows share a cell and period with another row. Do not treat the 4,706 rows as independent species-level observations.

The baseline groups are 2000–2009 and 2010–2019. The 2020–2026 group uses the SSP245 2020 projected slice. It is not annual future observation data. Do not pool periods or interpret temporal change without a justified evaluation question.

## Checks required before modelling

1. **Agree the target and study region.** Review species identity and rank, OBIS sampling effort, positional uncertainty, depth/geographic differences and whether the broad GSHHG water mask is defensible for each target taxon.
2. **Define a training unit.** Decide how repeated positive records within species/cell/period are represented and whether repeated presence cells are counted once for a specific model question. Preserve the full candidate source data.
3. **Unfold selected rows.** Use positive rows and their linked background records only for reviewed eligible taxa. Retain sample_id, paired_presence_source_row, period, taxon key, grid cell, label and sampling provenance. Do not copy synthetic rows into OBIS occurrence counts.
4. **Prevent leakage.** Assign spatial groups before fitting learned transformations. A raster cell must not occur in both training and testing, including repeats across periods and species where the question requires global blocking. Consider geographic separation and neighbouring cells; justify the split against intended generalisation.
5. **Handle environmental features.** Review the 382 definitions, source quarantines, missingness and collinearity. Only six core predictors are guaranteed complete for backgrounds; positive completeness is 2,082/2,353. Choose feature sets based on scientific relevance. Fit imputation, scaling, selection and tuning on training folds only.
6. **Handle time and sampling sensitivity.** Keep baseline slices and SSP245 2020 projection rows interpretable. Compare defensible accessible-domain, depth restriction, background sampling and bias treatments as sensitivity analyses before making claims.
7. **Compare models under a common protocol.** After group approval, choose a baseline and justified alternatives, tune within training folds, use metrics appropriate to the label design and imbalance, and retain a final held-out spatial evaluation. Do not infer occurrence probabilities from constructed labels alone.
8. **Record actual evidence.** Store split assignments, selected rows, feature definitions, seeds, package/model versions, metrics, uncertainty and limitations. Do not overwrite this full-population candidate table.

## Current verification evidence

The current GeoParquet is 4,706 × 527, GeoParquet 1.1.0, WKB Point, EPSG:4326 and ZSTD. All 519 source fields and positive geometries were verified on the leading 2,353 rows; two fields use nullable types so background rows can carry no observation ID or uncertainty-verification value. All 898,846 background feature positions matched the mapped Bio-ORACLE source arrays after read-back with zero numerical and null/fill discrepancies. These checks establish technical extraction and serialization, not ecological validity or model performance.

No training table has been unfolded, no feature selection or imputation has been performed, and no model, split, score or prediction has been generated.

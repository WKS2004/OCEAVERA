# Provisional evaluation design — presence/background candidates

- **Record date:** 16 October 2026
- **Status:** Technical candidate construction is complete. Group scientific approval of focal species, accessible domain, labels and evaluation protocol is pending; this is not authorisation to train models.
- **Linked decision:** [D-055](2026-10-16-decision-presence-background-candidates.md)
- **Dataset:** `data/interim/pseudo_absence/presence_background_candidates.parquet`
- **Source:** Current Policy B grid in `data/interim/integrated/gridded/grid_observations.parquet`; six source products are identified and audited through the current integration manifest/catalogue.

## Row and label meaning

Each output row represents one focal species, Bio-ORACLE raster cell and observation period. Label `1` is an observed, verified species-rank occurrence cell. Label `0` is a randomly selected marine-grid background cell with no recorded presence for that AphiaID in any input period. Background is not confirmed absence. The input coordinates are cell centres, not exact animal locations.

The initial candidate taxa and occupied positive cells are:

| Species | AphiaID | 2000–2009 | 2010–2019 | 2020–2026 | Total positive cells |
| --- | ---: | ---: | ---: | ---: | ---: |
| *Stenella longirostris* | 137109 | 0 | 11 | 24 | 35 |
| *Lepidochelys olivacea* | 220293 | 0 | 35 | 28 | 63 |
| *Chelonia mydas* | 137206 | 13 | 18 | 40 | 71 |
| **Total** |  | **13** | **64** | **92** | **169** |

The script requested a 1:1 background-to-positive-cell ratio within each species and period, with seed `20261016`. It generated 169 background rows and 169 positive rows with no pool shortfall. Each row has six core measurements (temperature, salinity, dissolved oxygen, chlorophyll, pH and bathymetry); all 382 environmental feature definitions are retained without feature selection, imputation or normalization.

## Sampling domain and safeguards

Background candidates are Bio-ORACLE grid centres inside the reusable GSHHG positive-water geometry with complete values for all six core features. The construction does not clip to an EEZ, estimate species-specific accessible area or weight by OBIS sampling effort. It excludes every grid cell with a recorded `absence=false` occurrence for that focal AphiaID across any input period. Candidate pools were roughly 24,400 cells per species. The 169 selected background centres were all inside GSHHG water, had all core values and had no same-species recorded-presence overlap.

Observed occurrence records are collapsed within species/cell/period. The same cell may appear in more than one period; 20 species/cell locations occur in multiple periods in the output. Spatial partitions must therefore group by species and cell across periods. Reported nearest-positive distances vary substantially by species and period, from approximately 11 km to 162 km minimum distance and up to 651 km maximum. These patterns may reveal separation caused by uniform sampling; they do not validate the sampling design.

## Environmental and temporal limits

The source comparisons cover 102,758 original positive values and 129,116 output values across 382 features, with zero numeric mismatches, zero null/fill discrepancies and zero maximum absolute difference. netCDF4 applied declared mask/scale metadata once; the integration harmonizer did not reapply scale or offset. The values are technically consistent with the source products, but extraction agreement does not establish biological absence or an ecologically defensible comparison domain.

The 2000–2009 and 2010–2019 groups use the corresponding decadal baseline slices. The 2020–2026 group uses SSP245's 2020 slice as an explicit projection-based approximation. Baseline averaging windows remain imperfectly documented. Quarantined variables remain null. OBIS reporting effort and coordinate uncertainty are not corrected by this construction.

## Evaluation protocol — pending group approval

- **Generalisation question:** Not finalised. Agree whether the intended use is geographic interpolation, transfer to new marine areas, or another defined prediction task.
- **Partitions:** Not created. Before any model fitting, define spatially separated folds and a held-out geographic evaluation area. Group shared species/cell locations across periods; then examine temporal separation and sensitivity to alternative spatial block sizes.
- **Leakage controls:** Fit imputation, scaling, feature selection and all target-guided transformations inside each training fold. Keep the final test region untouched during design and tuning.
- **Baseline and alternatives:** Not selected. Choose only after the species/domain/target design and feature handling are approved.
- **Metrics:** Not selected. Choose metrics for the agreed decision and report fold variation, class construction, spatial coverage and uncertainty. Accuracy alone is insufficient.
- **Sensitivity analysis:** Before interpreting comparisons, assess alternative background domains, background counts/ratios, effort-aware or spatially restricted sampling where justified, candidate species, and temporal grouping. Report whether conclusions depend on the 1:1 uniform sample.
- **Interpretation:** Scores against constructed background should be described as relative suitability unless independent presence/absence and sampling evidence support calibrated occurrence probabilities. Predictive associations do not establish causation.

No splits, transformations, feature selection or models have been created. D-009 remains open until the group reviews the biological species choice, domain and background design. See the [machine-readable construction report](2026-10-16-presence-background-construction.json) and the [Policy B decision](2026-10-16-decision-policy-b-marine-water-centre.md).

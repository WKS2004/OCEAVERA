# Decision D-055 — Provisional species presence/background candidates

- **Date:** 16 October 2026
- **Status:** Construction configuration implemented and technically verified; group approval of focal species, sampling domain and target design remains open.
- **Question:** How should the requested candidate presence/background table be constructed from the current Policy B spatial grid for later scientific review?
- **Context:** The user requested a reproducible pseudo-absence/background construction stage and supplied the intended Script 10 implementation. The work must preserve the accepted integration outputs, distinguish background from confirmed absence and stop before model training.

## Provisional implementation decision

Script 10 reads the Policy B `grid_observations.parquet` and creates an interim candidate table at `data/interim/pseudo_absence/presence_background_candidates.parquet`. A positive is an `absence=false`, marine-water-centre observation with a verified focal AphiaID, matching source name, species-level rank, supported observation period and all six core environmental measurements. Positive records are aggregated by species, raster cell and period while preserving source-row lineage and positional-confidence categories.

The initial focal candidates are *Stenella longirostris* (AphiaID 137109), *Lepidochelys olivacea* (220293) and *Chelonia mydas* (137206). This is an execution scope, not a final group species selection. A ten occupied-cell threshold is only a code construction gate; it does not establish enough independent locations for reliable evaluation.

For each species and period, Script 10 samples background cells uniformly without replacement, using seed `20261016`, requesting one background cell per eligible positive cell. The candidate domain is the intersection of actual Bio-ORACLE grid centres with verified GSHHG positive marine water and complete values for the six core measurements. Any `absence=false` input cell for the focal AphiaID is protected from background sampling across all periods, even where its record cannot be used as a positive because taxon rank or another positive eligibility field is incomplete. The construction applies no EEZ clipping or OBIS-effort matching weights.

Label `1` means a recorded, verified focal-species presence aggregated to a species/cell/period row. Label `0` means a sampled background cell without a recorded presence for that focal AphiaID in any input period. It is not a confirmed biological absence. Classifier scores against these labels do not automatically estimate calibrated occurrence probabilities.

## Evidence

The generated GeoParquet contains 338 rows and 397 columns: 169 positive cells and 169 sampled backgrounds, balanced 1:1 overall. It retains 382 environmental feature definitions. Seven species-period combinations produced positives; Stenella has no eligible 2000–2009 positive because its two source rows do not have a verified species-level rank. No candidate-pool shortfall occurred. All 169 background centres fall inside the GSHHG water geometry, have all six core values and avoid every same-species recorded-presence cell across periods.

The source audit checked 106 selected Bio-ORACLE products and 1,012 source-variable mappings. It compared 102,758 positive occurrence feature positions and 129,116 output feature positions with the original NetCDF slices. There were zero numeric mismatches, zero null/fill discrepancies and a maximum absolute difference of zero. The report records actual axes, cell centres, source units and time-coordinate matches. netCDF4 automatic masking/scaling remained enabled; no scale or offset was applied twice. The output GeoParquet uses version 1.1.0, WKB Point geometry, EPSG:4326 and ZSTD compression. Repeated construction with the same seed produced identical content. All five integration GeoParquets and the checked marine/source metadata remained unchanged.

See the [construction report](2026-10-16-presence-background-construction.md), [machine-readable report](2026-10-16-presence-background-construction.json), [evaluation design](2026-10-16-presence-background-evaluation-plan.md), and [branch notebook](../../notebooks/branch_work/05_pipeline_data_integration_and_data_cleaning.ipynb).

## Limits and follow-up

- This configuration does not establish the final study domain, focal species, background accessibility, sampling bias correction, sensitivity design or spatial validation protocol. D-009 remains open pending group review.
- Uniform sampling does not model OBIS observation effort and may create spatial or environmental separation from positives. The report includes per-period nearest-presence distances and six-feature summaries to inform review.
- The Bio-ORACLE region is a collection rectangle, not an EEZ boundary. GSHHG centre-in-water evidence does not resolve every coordinate uncertainty footprint.
- Source uncertainty categories remain attached to positive lineages. Future evaluation must group shared species/cells across periods to prevent spatial leakage.
- The 2020–2026 examples use the SSP245 2020 slice as a projection-based approximation. Baseline product averaging windows remain unresolved; quarantined feature-period values stay null.
- Some background locations may contain unrecorded true presences. Label 0 remains background, not absence.
- No feature selection, imputation, normalization, partitioning, model fitting, model comparison or prediction is part of this decision.

The output may support descriptive review. Promote it to a modelling target only after the group accepts the species, domain, sampling design, feature handling and leakage-aware evaluation plan. Keep classifier outputs in relative-suitability terms unless independent evidence supports probability calibration.

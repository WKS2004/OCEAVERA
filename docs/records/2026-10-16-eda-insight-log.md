# OCEAVERA — Exploratory Data Analysis Insight Log

This log records descriptive evidence and follow-up questions. It does not approve a modelling population, features or method.

| Section | Observed evidence | Follow-up implication | Current status |
| --- | --- | --- | --- |
| A | 4,706 rows, 382 environmental definitions, 12 period/class/cohort cells. | Preserve label meaning and screen metadata fields for leakage. | Descriptive |
| B | 0 features are complete in the full sample; 2 are all-null; 0 infinity positions. | Review source quarantines and missingness patterns before preprocessing. | No cleaning decisions |
| C | 614 positive taxon keys; 362 occupied cells; 480 cell-periods. | Compare candidate taxa using distinct cells and repeats, not record count alone. | No species selected |
| D | Complete-case six-core rows: 4,435 full, 3,458 eligible. | Investigate depth/coast differences as sampling-domain confounding. | Descriptive only |
| E | 3,602 period/cohort pair rows crossed |ρ| ≥ 0.95; 7 definitions have quarantined periods. | Review feature family redundancy and dependence before any selection. | Screening only |
| F | Background same-taxon/period nearest-presence median 334.20 km; maximum repeated cell-period count 36. | Use spatial cell groups; review accessible domain and positional uncertainty. | Validation design open |

**Target limits:** label 0 is sampled background, not a confirmed absence. Presence repeats are not statistically independent raster cells. The 2020–2026 environmental assignment is an SSP245 2020 projection assumption. Figures are not habitat-suitability predictions.

**Preservation:** all 382 environmental feature definitions and source columns remain unchanged; no dataset, processing script 08–10, or model input was rewritten. Feature-selection candidates are listed for later group review only.

# Species-specific presence/background candidate construction

**Status:** candidate dataset generated; scientific design and species/domain acceptance remain provisional

The output is a reproducible candidate table. Label 0 marks a sampled background cell; it does not establish biological absence. Group scientific acceptance of the accessible domain and sampling design remains pending.

## Dataset summary

| Measure | Result |
| --- | ---: |
| Rows | 338 |
| Columns | 397 |
| Observed-presence cells (label 1) | 169 |
| Sampled background cells (label 0) | 169 |
| Species | 3 |
| Observation periods | 3 |
| Environmental feature definitions | 382 |
| File size | 1,150,844 bytes |
| SHA-256 | `525bcea91f224420de23a0a1540c045616fe4d1b6e93a316ab9601877d44d1d6` |

## Species and period counts

| Species | AphiaID | Period | Original observations | Original occupied cells | Eligible positives | Background pool | Background generated | Shortfall | Contributing source rows |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Stenella longirostris | 137109 | 2000-2009 | 2 | 2 | 0 | 24,455 | 0 | 0 | 0 |
| Stenella longirostris | 137109 | 2010-2019 | 19 | 11 | 11 | 24,455 | 11 | 0 | 19 |
| Stenella longirostris | 137109 | 2020-2026 | 61 | 25 | 24 | 24,455 | 24 | 0 | 60 |
| Lepidochelys olivacea | 220293 | 2000-2009 | 0 | 0 | 0 | 24,428 | 0 | 0 | 0 |
| Lepidochelys olivacea | 220293 | 2010-2019 | 41 | 35 | 35 | 24,428 | 35 | 0 | 41 |
| Lepidochelys olivacea | 220293 | 2020-2026 | 42 | 31 | 28 | 24,428 | 28 | 0 | 39 |
| Chelonia mydas | 137206 | 2000-2009 | 13 | 13 | 13 | 24,426 | 13 | 0 | 13 |
| Chelonia mydas | 137206 | 2010-2019 | 24 | 20 | 18 | 24,426 | 18 | 0 | 22 |
| Chelonia mydas | 137206 | 2020-2026 | 77 | 42 | 40 | 24,426 | 40 | 0 | 75 |

## Construction and validation

- Background cells were sampled uniformly, without replacement, with seed `20261016`; the requested background:positive ratio was 1:1 within each species and period.
- The core eligibility set contains 6 measurements: ocean temperature, salinity, dissolved oxygen, chlorophyll, pH and bathymetry. All 382 catalogue feature columns are retained; no selection, imputation or normalization is performed.
- The catalogue audit checked 106 selected NetCDF products and 1,012 source-variable mappings, including actual axes, source units and time-coordinate indices.
- Environmental comparison checked 129,116 output positions and 102,758 original positive positions. Numerical mismatches: 0; null/fill discrepancies: 0; maximum absolute difference: 0.
- All five accepted integration GeoParquets were byte-identical before and after construction: True.
- GeoParquet: 1.1.0, WKB Point, EPSG:4326, ZSTD compression.

## Limitations and readiness

- OBIS presence locations reflect uneven reporting and sampling effort; this construction does not correct that bias.
- Uniform background sampling does not model species-specific accessible area or OBIS effort and may create geographic/environmental separation from observed presences.
- The water domain is GSHHG marine water intersected with the Bio-ORACLE collection grid, not a final Sri Lankan EEZ or species-specific accessible-area boundary.
- Policy B retained points despite some known coordinate-uncertainty footprints crossing coast/land or extending beyond reference coverage; source uncertainty categories remain attached to contributing records.
- Repeated records are collapsed within species/cell/period, but the same cell can occur in different periods. Future splits must group shared cells and assess temporal leakage.
- Only six core features are required for candidate eligibility. The remaining 376 feature definitions may be missing or quarantined; no imputation is performed.
- SSP245 2020 is used for 2020-2026 as a projection-based assumption; baseline time-window metadata remains imperfect.
- Some sampled background cells may contain unrecorded true presences. Label 0 is not a confirmed absence.
- The ten-cell gate is only a construction eligibility check and does not establish enough independent locations for reliable spatial evaluation; Stenella longirostris is especially sparse.
- Future model evaluation requires spatially isolated folds that prevent shared-cell leakage; no partition, feature selection, imputation, normalization or model fit is included.
- The three focal taxa are initial candidates only; the output does not establish that all 501 observed species are modelable or that these are final group-selected species.

The output is suitable for descriptive EDA and as an input to a later, explicitly validated supervised-preprocessing stage. It is not a model-ready table or an approved final target design. Do not interpret classifier scores as calibrated occurrence probabilities.

See [D-055](2026-10-16-decision-presence-background-candidates.md), the [evaluation design](2026-10-16-presence-background-evaluation-plan.md), [D-054](2026-10-16-decision-policy-b-marine-water-centre.md), and the [independent environmental verification](2026-10-16-independent-environmental-verification.md).

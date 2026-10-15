# Decision D-054 — Policy B marine water-centre candidates

- **Date:** 16 October 2026
- **Status:** Implemented at the user's explicit request; technical execution verified. Scientific acceptance of the eventual modelling domain remains open.
- **Supersedes:** D-053's uncertainty-footprint exclusion rule for current marine and grid outputs. D-053's integration, temporal-resolution decisions and source quarantines remain in force.

## Decision

Script 09 retains a temporally eligible observation when its original OBIS `flags` value is a valid JSON array without exact `ON_LAND` or `MARINE_UNSURE` tokens and its original Point lies strictly inside the validated GSHHG 2.3.7 positive marine-water polygon. A water-centre match remains eligible when a known positional-uncertainty footprint crosses land/coast or extends beyond the reference coverage. These footprints are retained as quality and sensitivity categories; missing or invalid uncertainty is never treated as zero.

The output is a **marine water-centre candidate dataset**. The point-in-water comparison is geographic evidence about the recorded centre. It does not prove that an animal's true position or full uncertainty footprint is marine. Do not automatically recover `ON_LAND` or `MARINE_UNSURE` records; those remain excluded pending separate taxonomic and location review.

## Rationale and prior-policy comparison

D-053's stricter rule kept only the water-centre records whose known footprints were entirely in water, plus records with unknown uncertainty: 709 + 590 = 1,299. Policy B retains the same cases and an additional 1,054 water-centre candidates whose known footprints cross coast/land (1,025) or extend beyond reference coverage (29), producing 2,353 candidates. This is a technical candidate expansion, not approval of every retained location as a verified marine habitat observation.

## Scope and safeguards

- Script 08, the full integration GeoParquet, its manifest/catalogue, cleaned OBIS and Bio-ORACLE sources, raw source data and GSHHG reference remain unchanged.
- Script 09 has no required command-line flags; the routine command is `python src/data_preparation/09_filter_and_grid_data.py`.
- Script 09 reads the completed GeoParquet, manifest, raster axes and existing GSHHG reference. It does not import Script 08 or read NetCDF arrays.
- The previous four strict-policy datasets were replaced in place by Script 09's validated temporary-file publication. The prior hashes and shapes are retained in the execution report; strict-policy reports are byte-verified historical copies.
- The individual tables preserve all full-integration columns and original Point geometries. GeoParquet 1.1.0, EPSG:4326, ZSTD, raster indices/cell IDs and all 382 environmental definitions remain.
- No species selection, predictor selection, target creation, background sampling, preprocessing or model training is part of this decision.

## Executed evidence

The current outputs contain 23,371 full records, 9,681 temporal records, 2,353 marine water-centre candidates, 2,353 gridded records and 1,389 species/cell/period summary rows. The marine candidates comprise 1,389 complete, 693 partial and 271 no-valid-value environmental records; 2,082 have at least one environmental value. There are 2,009 identifier-bearing species-rank records, 501 distinct taxonomy keys, 362 occupied cells and 344 other-rank/un-grouped individual records. Summary counts sum to 2,009.

Among 9,681 temporal records, 6,423 carry `ON_LAND`, 41 carry `MARINE_UNSURE`, 40 carry both, and 6,424 carry at least one of these exact flags. There are 2,815 water-centre matches before flag exclusions; 462 of those carry an excluded flag. The remaining 6,866 points are outside the polygon (including flagged points); after flag checks, 904 unflagged non-water centres are excluded. No exact-boundary observations occur in this execution.

See the [Policy B execution report](2026-10-16-policy-b-execution-report.md), [machine-readable execution evidence](2026-10-16-policy-b-execution-report.json), [current spatial report](2026-10-16-spatial-grid-report.md), [archived strict-policy report](2026-10-16-spatial-grid-report-strict-policy.md), [temporal report](2026-10-16-temporal-filter-report.md), and [historical D-053 record](2026-10-16-decision-final-integration-completion.md).

## Remaining limits

GSHHG is a sourced coastline reference, not a current metre-accuracy shoreline survey. The reference covers the established rectangular collection extent and is not an EEZ clip or final modelling boundary. Source dates map to decadal Bio-ORACLE slices; 2020–2026 uses the SSP245 2020 coordinate as an explicit approximation. Environmental extraction and raster matching do not establish a valid marine observation. Policy B candidates still require species, sampling-bias, feature-suitability and domain review before any ML preparation.

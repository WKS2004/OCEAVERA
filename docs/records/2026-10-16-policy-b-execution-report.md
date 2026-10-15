# D-054 — Policy B execution report

- **Date:** 16 October 2026
- **Status:** PASS — Script 09 completed without flags and all five current GeoParquets passed direct read-back and integrity checks.
- **Decision:** [D-054](2026-10-16-decision-policy-b-marine-water-centre.md)

## Policy and execution

Policy B requires an eligible 2000–2026 observation, a valid JSON flags array without exact `ON_LAND` or `MARINE_UNSURE`, and an original Point strictly inside the validated GSHHG water polygon. Positional uncertainty is recorded, not used to reject a qualifying centre. Script 09 ran with zero flags in the existing WSL OCEAVERA Python 3.14.8 environment. It did not run Script 08 or reopen NetCDF arrays. The four prior derived files were replaced at their fixed paths by validated temporary-file publications; Script 09 read each completed file back before replacement.

## Current datasets

| Dataset | Shape | GeoParquet | CRS | Compression | SHA-256 |
| --- | ---: | --- | --- | --- | --- |
| Full archive | 23,371 × 513 | 1.1.0 | EPSG:4326 | ZSTD | `34e756d9fa0d5478da14b6a2d627c16076c486d8e43317363d387d69a661ee34` |
| Temporal observations | 9,681 × 514 | 1.1.0 | EPSG:4326 | ZSTD | `6669327ec1aba406bf8aa8346dc743d1ab721a1237c0266705119881cc21479a` |
| Policy B marine candidates | 2,353 × 518 | 1.1.0 | EPSG:4326 | ZSTD | `76a2812ae4d031bc9515d15931a2a97221d584b2b24cfad7e1e2fb5e77ba1d49` |
| Gridded observations | 2,353 × 519 | 1.1.0 | EPSG:4326 | ZSTD | `71fa9ff9ad959122811ef01117a2157baf0498fbcc1e93bfb340ba87d94d2fc0` |
| Species/cell/period summary | 1,389 × 391 | 1.1.0 | EPSG:4326 | ZSTD | `eb14bebd83f993894672f143f16a452470cdd1c924c390c3c061b580b8c77433` |

The full archive SHA-256 remained `34e756d9fa0d5478da14b6a2d627c16076c486d8e43317363d387d69a661ee34` before and after Script 09; this equals the integration-manifest fingerprint. All 112 original OBIS fields and 382 environmental feature definitions remain in the individual full/temporal/marine/grid schemas. Original Point geometry, raster indices and IDs were checked against source rows. Every file has valid geometry; no null geometries were found.

## Temporal and environmental coverage

| Period | Temporal | Temporal complete / partial / none | Policy B | Policy B complete / partial / none | Policy B with any environmental value |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2000-2009 | 651 | 331 / 109 / 211 | 376 | 204 / 109 / 63 | 313 |
| 2010-2019 | 2,564 | 872 / 200 / 1,492 | 596 | 354 / 196 / 46 | 550 |
| 2020-2026 | 6,466 | 2,807 / 403 / 3,256 | 1,381 | 831 / 388 / 162 | 1,219 |

Across the 2,353 Policy B candidates, **1,389** have complete coverage, **693** partial coverage and **271** no valid environmental values. **2,082** have at least one environmental value.

## Marine selection and uncertainty

Of the 9,681 temporal records, **2,815** point centres are inside GSHHG water before flags; **6,866** centres fall outside. Flag counts are `ON_LAND` **6,423**, `MARINE_UNSURE` **41**, both **40**, union **6,424**. The 40 overlaps are counted once in the 6,424-record union. Among water-centre points, **462** carry an excluded flag. After flags, **904** unflagged non-water centres are excluded; boundary, invalid-coordinate and invalid-flag exclusions are zero.

| Retained positional-confidence category | Records |
| --- | ---: |
| unknown uncertainty | 590 |
| known footprint crosses coast or land | 1,025 |
| known footprint marine | 709 |
| known footprint outside reference extent | 29 |

Policy B retains **2,353** water-centre candidates. D-053's strict policy retained **1,299**: 709 known footprints entirely in water plus 590 unknown-uncertainty points. Policy B also retains **1,054** known footprints crossing coast/land (**1,025**) or extending outside reference coverage (**29**). This explains the increase to 2,353 without treating those footprints as verified marine. The previous strict reports were copied byte-for-byte; their SHA-256 values are in the machine report.

## Species and grid summaries

There are **2,009** identifier-bearing species-rank observation rows, **501** distinct taxonomy keys, **362** occupied cells and **1,389** species/cell/period summary rows. Summary `occurrence_record_count` totals **2,009**, equal to the eligible species-rank records. **344** remaining individual observations do not enter the species-rank summary.

## Retired strict outputs and preserved inputs

The four strict-policy files were replaced by the zero-flag Script 09 run. Their former fingerprints were recorded before publication:

| Former strict output | Shape | Former SHA-256 |
| --- | ---: | --- |
| `data/interim/integrated/temporal/observations_2000_2026.parquet` | 9,681 × 514 | `6669327ec1aba406bf8aa8346dc743d1ab721a1237c0266705119881cc21479a` |
| `data/interim/integrated/marine/marine_observations.parquet` | 1,299 × 518 | `4b7d4f1dacb7147d03d2e9db208741e73126a180404c9a7a173e35cfb55f0a6b` |
| `data/interim/integrated/gridded/grid_observations.parquet` | 1,299 × 519 | `db57dc3b1836eae5af872633fb7627b77209cf3875adca75c7e4bef2e31512c8` |
| `data/interim/integrated/gridded/species_cell_period_summary.parquet` | 667 × 391 | `d767b245682c681325133cf6e4015e58bb921930f82ee616d7426f86c1b9ebc0` |

The temporal output has the same SHA-256 as before because its selection rules did not change and the writer produced identical bytes. The full integration GeoParquet and GSHHG reference were preserved; their fingerprints match the manifest/provenance records. Historical strict-policy reports remain in `docs/records/*-strict-policy.*`.

## Validation and limits

- Script 09 zero-flag execution: PASS.
- Unit tests: **27 passed**.
- `compileall`: PASS.
- `pip check`: PASS; no broken requirements.
- `git diff --check`: PASS (exit 0; one pre-existing CRLF warning in notebook 03).
- Repository structural/link validation: PASS (8 skills, 10 rules, 12 routing cases, 543 text files, 1,450 local links, 121 Markdown section links, 4 contributor identities and 4 logs).
- No target construction, background sampling, feature selection or model training was introduced.

Environmental extraction indicates values were technically available at matched grid cells; it does not establish marine point location. GSHHG point-in-water establishes location evidence for the recorded centre; it does not resolve uncertainty-footprint accuracy, sampling bias, species identity or ecological suitability. The final modelling species, spatial domain and environmental predictors remain open.

Machine-readable checksums and count details: [Policy B execution JSON](2026-10-16-policy-b-execution-report.json).

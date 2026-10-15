# OBIS–Bio-ORACLE integration run summary

- Cleaned OBIS rows preserved: **23,371**
- Original OBIS fields preserved exactly: **112 of 112**
- Output environmental feature columns: **382**
- Selected source products: **106** (55 baseline, 50 SSP245, one static terrain product)
- Output: `data/interim/integrated/full/integrated_observations.parquet` (7,862,848 bytes)
- Format: GeoParquet 1.1.0, compression ZSTD
- Distinct raster cells occupied by source observations: **965**

## Temporal assignments

| Time mapping | Source rows |
| --- | ---: |
| 2020–2026 (SSP245 coordinate 2020) | 6,466 |
| 2000–2009 (Bio-ORACLE coordinate 2000) | 653 |
| no_supported_slice | 13,690 |
| 2010–2019 (Bio-ORACLE coordinate 2010) | 2,562 |

## Spatial and environmental coverage

| Status | Rows |
| --- | ---: |
| matched | 23,371 |

| Environmental value status | Rows |
| --- | ---: |
| no_valid_source_values_at_cell | 4,959 |
| complete_environmental_values | 4,010 |
| outside_supported_time_range | 10,409 |
| missing_or_invalid_date | 3,281 |
| partial_environmental_values | 712 |

The full per-feature non-null, null, legitimate-zero and source-period counts are in the machine-readable manifest. NetCDF fill masks and scale/offset metadata were handled by netCDF4 automatic decoding exactly once.
A matched raster cell does not prove marine eligibility. The separate temporal, marine and grid workflow records that evidence gate.

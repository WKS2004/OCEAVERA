# OBIS–Bio-ORACLE integration run summary

- Cleaned OBIS rows preserved: **23,371**
- Original OBIS fields preserved exactly: **112 of 112**
- Output environmental feature columns: **382**
- Selected source products: **106** (55 baseline, 50 SSP245, one static terrain product)
- Output: `data/interim/integrated/full/integrated_observations.parquet` (7,866,289 bytes)
- Format: GeoParquet 1.1.0, compression ZSTD
- Distinct raster cells occupied by source observations: **965**

## Temporal assignments

| Time mapping | Source rows |
| --- | ---: |
| 2020–2026 (SSP245 coordinate 2020) | 6,466 |
| 2000–2009 (Bio-ORACLE coordinate 2000) | 651 |
| no_supported_slice | 13,690 |
| 2010–2019 (Bio-ORACLE coordinate 2010) | 2,564 |

## Spatial and environmental coverage

| Status | Rows |
| --- | ---: |
| matched | 23,371 |

| Environmental value status | Rows |
| --- | ---: |
| no_valid_source_values_at_cell | 4,959 |
| complete_environmental_values | 4,010 |
| outside_supported_time_range | 10,386 |
| missing_or_invalid_date | 3,282 |
| partial_environmental_values | 712 |
| ambiguous_date_assignment | 22 |

The full per-feature non-null, null, legitimate-zero and source-period counts are in the machine-readable manifest. NetCDF fill masks and scale/offset metadata were handled by netCDF4 automatic decoding exactly once.
A matched raster cell does not prove marine eligibility. Current marine water-centre candidates are selected under D-054 using valid flags and independent GSHHG point-in-water evidence; positional uncertainty remains a separate diagnostic.

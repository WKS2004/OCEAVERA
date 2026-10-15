# Temporal filtering report

- Input rows: **23,371**
- Retained rows with verified temporal eligibility from 2000 through 2026: **9,681**
- Excluded rows: **13,690**
- Output: `data/interim/integrated/temporal/observations_2000_2026.parquet`

| Period | Rows |
| --- | ---: |
| 2020-2026 | 6,466 |
| 2000-2009 | 651 |
| 2010-2019 | 2,564 |

| Exclusion or retention reason | Rows |
| --- | ---: |
| retained_2000_2026 | 9,681 |
| before_2000 | 10,386 |
| missing_or_invalid_date | 3,282 |
| ambiguous_temporal_assignment | 22 |

The temporal stage keeps individual observations and their point geometry. Single-year evidence must agree by environmental period and be consistent with date intervals. Interval-only rows are retained only when the complete interval fits one supported period. Ambiguous records remain in the full archive. The year limit is not a marine boundary.

The geographic/environmental diagnostic cross-tab is in `docs/records/2026-10-16-environmental-coverage-by-geography-and-period.md`. It is a summary only and does not perform marine filtering or species selection.

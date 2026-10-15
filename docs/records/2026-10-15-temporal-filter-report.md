# Temporal filtering report

- Input rows: **23,371**
- Retained rows with a resolved year from 2000 through 2026: **9,681**
- Excluded rows: **13,690**
- Output: `data/interim/integrated/temporal/observations_2000_2026.parquet`

| Period | Rows |
| --- | ---: |
| 2020-2026 | 6,466 |
| 2000-2009 | 653 |
| 2010-2019 | 2,562 |

| Exclusion or retention reason | Rows |
| --- | ---: |
| retained_2000_2026 | 9,681 |
| before_2000 | 10,409 |
| missing_or_invalid_date | 3,281 |

The temporal stage keeps individual observations and their point geometry. Its date resolution is documented in the integration manifest; the year limit is not a marine boundary.

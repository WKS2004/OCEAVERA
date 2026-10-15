# Environmental coverage by geographic-quality flags and observation period

- Temporal observations: **9,681**
- Cross-tab reconciliation: **9,681 / 9,681 rows**
- Missing or invalid JSON flags: **0** (not interpreted as marine verification)

| Geographic-quality group | Period | Total records | Complete environment | Partial environment | No valid values | Distinct species-rank IDs |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| ON_LAND | 2000-2009 | 271 | 123 | 0 | 148 | 73 |
| MARINE_UNSURE (excluding ON_LAND overlap) | 2000-2009 | 1 | 1 | 0 | 0 | 1 |
| Neither ON_LAND nor MARINE_UNSURE | 2000-2009 | 379 | 207 | 109 | 63 | 79 |
| ON_LAND | 2010-2019 | 1,778 | 351 | 0 | 1,427 | 243 |
| MARINE_UNSURE (excluding ON_LAND overlap) | 2010-2019 | 0 | 0 | 0 | 0 | 0 |
| Neither ON_LAND nor MARINE_UNSURE | 2010-2019 | 786 | 521 | 200 | 65 | 273 |
| ON_LAND | 2020-2026 | 4,374 | 1,398 | 15 | 2,961 | 512 |
| MARINE_UNSURE (excluding ON_LAND overlap) | 2020-2026 | 0 | 0 | 0 | 0 | 0 |
| Neither ON_LAND nor MARINE_UNSURE | 2020-2026 | 2,092 | 1,409 | 388 | 295 | 477 |

Coverage is measured against the feature columns supported by that period, including static terrain. The groups are diagnostic only; they do not select species or filter observations. `ON_LAND` has priority over `MARINE_UNSURE`; malformed/missing flag arrays are counted separately and are not treated as proof of marine location.

Current marine selection is Policy B under D-054. Exact `ON_LAND` and `MARINE_UNSURE` flags remain excluded; for other records, a water-centre match is required and uncertainty is recorded as a diagnostic.

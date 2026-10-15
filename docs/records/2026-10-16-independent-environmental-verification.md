# Independent original-source environmental verification

**PASS — numerical source agreement and quarantine enforcement. Scientific interpretation remains conditional.**

**PASS for source agreement and quarantine enforcement.** Reader: netCDF4 1.7.4. The independent method imports neither processing script. It opens the original publisher-delivered NetCDF files directly, verifies raw/cleaned byte hashes, reads actual time axes and declared masking/scaling, samples distinct occupied cells and expands the results back to observation rows.

| Measure | Positions |
| --- | --- |
| All row-feature positions | 8,927,722 |
| Source-period positions before quarantine | 3,369,132 |
| Applicable retained positions | 3,336,910 |
| Non-null numerical values compared | 1,627,796 |
| Total null positions | 7,299,926 |
| Source masks among retained definitions | 1,709,114 |
| Deliberate quarantine positions | 32,222 |
| Unsupported observation-period positions | 5,229,580 |
| Unavailable feature-period positions | 329,010 |
| Legitimate zeros | 139,457 |
| Numerical mismatches | 0 |
| Null mismatches | 0 |
| Coordinate mismatches | 0 |

106 original products and 1,012 distinct product/variable/actual-time slices were checked, including static terrain. The complete per-column counts and explicit source-slice ledger are saved. Maximum numerical difference: **0**. Distinct cell samples summed across feature/period comparisons: 322,576; full archive occupied cells: 965. Source axes and stored cell centres agreed for every source product. An independent nearest-centre search from all 23,371 original coordinates reproduced the raster row, column and stable cell ID with zero mismatches. The grid spacing is approximately 0.05 degrees; point matching inherits that spatial approximation.

Null categories reconcile: 1,709,114 retained-source masks + 32,222 quarantines + 5,229,580 unsupported-date positions + 329,010 unavailable-feature positions = 7,299,926. Original source masking including quarantined definitions is 1,725,844; this overlaps quarantines and is not an additional category.

Actual source years 2000/2010 are used historically and only SSP245 2020 for 2020–2026. Terrain uses the source's static/Benthic context; 1970 is not an observation date. Current policy leaves all features, including terrain, null on temporally ineligible rows. The arrays remain source grids; no global raster was flattened.

This comparison validates numerical lineage and deliberate quarantine. It does not establish publisher semantics, ecological relevance, marine location, observed annual conditions or the correctness of the SSP scenario assumption. The full verification program is retained as text inside its JSON record for independent reproduction.

See the [complete technical report](2026-10-16-integration-final-technical-report.md), [per-column results and source-slice ledger](2026-10-16-independent-environmental-verification.json) and [source-lineage investigation](2026-10-16-source-lineage-investigation.json).

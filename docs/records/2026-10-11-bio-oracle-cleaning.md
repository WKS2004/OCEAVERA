# Bio-ORACLE regional environmental data cleaning and validation

- **Date:** Initial scan 11 October 2026; interim materialization follow-up 12 October 2026
- **Status:** Implemented and verified. All 356 source products are readable and have byte-verified copies in the current interim stage. One product has a value requiring review. No raster values were changed, imputed, normalized or excluded.
- **Purpose:** Inspect the acquired Bio-ORACLE environmental arrays and provenance in full before later data integration, then publish the validated NetCDF products and their reports as the sole current interim stage under D-049.

## Inputs and implementation

- **Source run:** `20261009T163625858012Z`, recorded in `data/raw/bio_oracle/_runs/20261009T163625858012Z_bio_oracle_catalog.json`; the source manifest SHA-256 is `cd35ee526ffbf9a57b7279016c0e4a5c7348afabec39369e2946cadff0b12b8b`.
- **Source payloads:** 356 publisher-delivered NetCDF files, 4,017,532,960 payload bytes, and their per-layer receipts. The source run contains 2,392 environmental variable instances across 139 distinct names: 55 baseline products, 300 future-scenario products and one static terrain product.
- **Cleaner:** [`07_clean_bio_oracle_layers.py`](../../src/data_preparation/07_clean_bio_oracle_layers.py), using the Python standard library. The reader parses each current interim NetCDF file and inspects complete variable arrays while independently checking raw source, run and receipt hashes. It checks product and variable declarations, fill/missing values, finite and declared-range values, per-time statistics, coordinate axes, grid consistency, CRS metadata, candidate-domain consistency and exact duplicate arrays.
- **Current interim outputs:** 356 byte-for-byte NetCDF copies under `data/interim/bio_oracle/cleaning/<dataset-id>/`, plus `manifest.json` and `cleaning_summary.json`. The manifest records each immutable raw source and its interim product path, byte count and SHA-256. Raw products remain unchanged.
- **Environment:** The scan used the bundled Python 3.12.14 runtime and no third-party packages. The project baseline remains Python 3.14 under D-039. No Python environment or package was created, modified or installed.

Before the cleaner replaced the prior source-validation stage, it rechecked all 714 staged files against their raw payloads, source receipts and catalogue run manifest. All 714 matched; there were no missing paths, additional paths or checksum mismatches. The source-validation directory was then replaced by the `cleaning/` directory under D-049. The earlier stage remains reproducible from the raw source run and [`06_stage_bio_oracle_layers.py`](../../src/data_preparation/06_stage_bio_oracle_layers.py).

The official publisher metadata identify the terrain product as `terrain_characteristics` and document WGS84/EPSG:4326 coordinate reference metadata; see the [Bio-ORACLE ERDDAP dataset metadata](https://erddap.bio-oracle.org/erddap/info/terrain_characteristics/index.html). This does not document the numeric land/water convention for the `landmass` variable.

## Results

| Check | Observed result | Treatment |
| --- | --- | --- |
| Product inventory and readability | 356 of 356 products readable; 0 unreadable | Retain all products. |
| Product dispositions | 355 validated; 1 requires review | No product corrected or excluded. |
| Environmental variables | 2,392 instances; 139 names | All declared expected variables were inspected. |
| Declared missing values | Each variable declares `_FillValue = -9999.9`; no empty environmental variable instances | Preserve publisher values and fill sentinels. |
| Non-finite and valid-range checks | 0 NaN, 0 positive/negative infinity, 0 declared valid-range violations | No transformations applied. |
| Grid and coordinates | One 178 × 165 grid; unique, strictly increasing latitude and longitude; approximately 0.05° spacing; CRS metadata identify WGS84/EPSG:4326 | No alignment correction applied. The grid covers cell centres from 77.0250–85.2250°E and 2.5750–11.4250°N. |
| Time coordinates | Baseline labels 2000 and 2010; future-scenario labels 2020–2090; terrain is static | Preserve labels. These are decade-level products, not annual values; no separate 2100 coordinate was present. Exact averaging windows for baseline labels remain unresolved. |
| Candidate non-fill domain | `landmass` has 24,503 non-fill cells out of 29,370; its attributes do not define the numeric land/water code | Use only the non-fill pattern for cross-layer checking. Do not assign numeric land/water semantics or call it an authoritative marine mask. |
| Continuous-layer domain check | 2,390 variable instances compared; 0 valid values outside the candidate domain; 1 candidate-domain fill value | Flag the `kdpar_mean_range` fill described below. |
| Sparse terrain variable | `coastline` has 486 non-fill cells and 28,884 fill cells | Report separately; do not interpret sparse raster fill as continuous marine missingness. |
| Duplicate source files and axes | No byte-identical source files; no repeated coordinate or time axes; no grid mismatch | Keep each source product. |
| Identical within-file arrays | 14 groups of distinct sea-ice (`siconc`/`sithick`) summaries are identical all-zero arrays over this regional domain | Report as warnings and preserve. Equality is not treated as proof of a duplicate or invalid variable. |

### Item requiring review

The product `kdpar_mean_baseline_2000_2020_depthsurf` contains one fill value
for `kdpar_mean_range` at the 2000 coordinate, within the 24,503-cell
candidate non-fill domain. That slice has 24,502 finite values; its 2010
slice has 24,503. No value was imputed or modified. The product remains in the
manifest with `review_required` disposition. The targeted audit found no justified replacement; the candidate-mask interpretation remains unresolved.

## 12 October 2026 — Targeted scientific sign-off audit

This was a targeted, read-only inspection of the flagged variable, the terrain product, four representative baseline products, and the existing cleaning reports. The 356-product cleaning pipeline was not rerun. The selected target and terrain raw files are byte-identical to their current interim copies.

### The retained KdPAR fill value

In product `kdpar_mean_baseline_2000_2020_depthsurf`, variable `kdpar_mean_range`, the stored value at time 2000, latitude index 119 and longitude index 83 is exactly `-9999.9`, matching the declared `_FillValue = -9999.9`. Variable metadata identify units `m-1`, long name `Range DiffuseAttenuationCoefficientPAR`, and category `Statistics`. The stored value at the same grid cell in the 2010 slice is 0.051083154350263366.

The 3×3 neighborhood contains four candidate-domain cells. Three are finite in 2000 and all four are finite in 2010; the flagged fill is the only gap among those four. The other five cells in that neighborhood are masked in both slices. At the target cell, `landmass` is 1.0, `bathymetry_mean` is 0.0 m, and representative `kdpar_mean_mean`, chlorophyll, temperature, oxygen and nitrate values are finite in both time slices. These comparisons show the missing value is isolated in the observed neighborhood; they do not establish what value should replace it. No numerical correction or imputation is justified. Preserve the fill value.

### Candidate non-fill domain

The terrain `landmass` variable attributes are `_FillValue=-9999.9`, `ioos_category=Unknown`, `long_name=landmass`, and `units=1`. Its non-fill value is 1.0 in 24,503 cells; 4,867 cells contain the declared fill. The variable has no `flag_values`, `flag_meanings` or other attribute that defines whether 1.0 means land or water. The [publisher terrain metadata](https://erddap.bio-oracle.org/erddap/info/terrain_characteristics/index.html) also does not provide that legend.

The `bathymetry_mean` non-fill pattern exactly matches `landmass`; both have 24,503 non-fill cells and 4,867 fill cells. The full scan compared 2,390 continuous environmental variable instances: no valid values occur outside this candidate domain, and the one flagged missing value occurs inside it. This supports an internally consistent empirical non-fill environmental domain. It does not verify an authoritative marine mask or the land/water meaning of the numeric code.

### Product and issue status

The current manifest marks 355 products `validated`, zero `validated_reused`, and one `review_required`: `kdpar_mean_baseline_2000_2020_depthsurf`. The unresolved issue codes are:

| Issue code | Occurrences | Severity | Scope |
| --- | ---: | --- | --- |
| `marine_domain_missing_values` | 1 | review | The retained KdPAR fill value described above |
| `marine_mask_unresolved` | 1 | review | Global candidate-domain interpretation |
| `identical_zero_arrays` | 14 groups | warning | Identical all-zero sea-ice summaries retained as observed |

No product is unreadable or confirmed invalid. The one review product remains readable and byte-preserved, but its missing cell requires an explicit missing-value policy before extraction. The reports do not grant blanket scientific approval for every layer.

### Sign-off and next stage

No confirmed duplicate source products, duplicated coordinate/time axes, corruption, non-finite values, declared valid-range violations or numerical cleaning operations remain outstanding. The 14 identical-zero groups are warnings, not confirmed duplicates or invalid measurements. The single missing cell is correctly encoded as the declared fill value and should remain missing.

Bio-ORACLE cleaning can be closed as a completed structural and numerical validation stage with these documented limitations. Spatial integration must still choose the extraction domain and layer subset, define nodata and coastal-cell treatment, verify coordinate/grid alignment with selected OBIS locations, assess baseline time-window compatibility, and decide whether the unresolved mask can be used or needs an independently justified source. Do not interpret the 1.0 landmass code or use it as an authoritative marine mask without further evidence.

## Reproduction and verification

Run from the repository root:

```text
python src/data_preparation/06_stage_bio_oracle_layers.py --run-manifest data/raw/bio_oracle/_runs/20261009T163625858012Z_bio_oracle_catalog.json
python src/data_preparation/07_clean_bio_oracle_layers.py
```

The initial 11 October scan read every array and published its JSON reports.
After the user noted that the validated Bio-ORACLE dataset itself was absent
from interim, the cleaning stage was updated on 12 October to contain all 356
byte-for-byte NetCDF products under `cleaning/<dataset-id>/`, while leaving
the raw source tree intact. The first cleaner revision incorrectly required
an already existing `cleaning/` stage, so the user's stage-then-clean run
stopped before scanning. The corrected cleaner accepts `source_validation/`,
scans each existing interim product, streams detailed diagnostics to a
temporary spool to bound RAM, and promotes that same folder to `cleaning/`
by directory rename after a successful scan. This avoids both the missing
handoff and a second full-size NetCDF copy. The full scan passed all 356
products with 355 validated and one requiring review. A subsequent default
run rechecked source, staged receipts and interim product hashes, then reused
the saved array diagnostics. The stager's `--dry-run` also passed its
replacement-integrity check against the current cleaned stage. Use
`--force-full-scan` to read every array again; the default mode may reuse a
verified report only after rechecking source and interim hashes.

The current v2 manifest and summary hashes are:

- `manifest.json` SHA-256: `703e1d2433d944bc8c56595dc19faaa26815cb1e2cd53eab58790e256d6723e7`.
- `cleaning_summary.json` SHA-256: `b32dfcefdc3ef1cf3c316f261bd86fbc28b7703a2ee710409b0dacda690ac8c3`.

The initial JSON-only result was superseded by this current stage on 12 October;
its former hashes were `4341f6c98c178c0f4e451ed10d099ddb58fb1560935119c9738066ad1224441e`
(manifest) and `34105295f90ed9675b4759b482b152a3caca9c59eed7ce7fbb76304227828a0d`
(summary). The current report includes full diagnostics for all 356 products
and 3,460 variable records, including coordinate and auxiliary variables; it
is not a JSON-only stage.

The detailed summary records per-product/per-variable counts, coordinate and
time information, duplicate checks and issue classifications. The raw files
and receipts remain in `data/raw/bio_oracle/`; only one interim stage
directory exists at a time. Source receipts and the catalogue-manifest copy
are preserved with the dataset, and the stage script verifies them when
replacing the cleaned stage on a later run. The exact full scan can be
repeated with `--force-full-scan`.

## Limits and next evidence gate

This work is structural and numerical data validation. It did not select a
focal species, model domain, environmental predictor, marine mask convention,
time aggregation, resampling method or coastal-cell treatment. It did not
extract raster values, join environmental values to observations, create an
integrated table, construct targets, select a modelling population, or train
or evaluate a model. Missing values are not confirmed absences, and no
suitability or occurrence-probability claim follows from this scan.

The targeted review found no justified replacement for the single `kdpar_mean_range` fill value; preserve it and carry an explicit missing-value policy into extraction.
The `landmass` and `coastline` interpretation, selected layer compatibility, baseline time-window matching and modelling domain remain open for the later spatial integration stage.

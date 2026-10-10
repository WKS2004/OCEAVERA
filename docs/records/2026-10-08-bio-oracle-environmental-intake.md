# Bio-ORACLE environmental intake: metadata and implementation record

- **Date:** 8 October 2026
- **Status:** Initial bounded intake utility implemented; the 9 October test response was inspected and then deleted with its local manifest at the user's request; the historical source record remains
- **Purpose:** Record the publisher metadata reviewed and the first candidate query used to start the environmental collection phase under [D-046](2026-10-08-decision-bio-oracle-environmental-intake.md).

## Candidate resource and source evidence

| Field | Recorded information |
| --- | --- |
| Publisher | Bio-ORACLE consortium, served through its ERDDAP instance |
| Candidate resource | `thetao_baseline_2000_2019_depthsurf`, OceanTemperature surface layer |
| Stable source identifier | ERDDAP dataset ID `thetao_baseline_2000_2019_depthsurf` |
| Publisher metadata | [ERDDAP dataset metadata](https://erddap.bio-oracle.org/erddap/info/thetao_baseline_2000_2019_depthsurf/index.html) |
| Dataset documentation | [Bio-ORACLE data-layer documentation](https://www.bio-oracle.org/documentation.php) |
| Version and citation | Bio-ORACLE v3.0; Assis et al. (2024), [DOI 10.1111/geb.13813](https://doi.org/10.1111/geb.13813) |
| Metadata date checked | 8 October 2026; metadata rechecked 9 October 2026 |
| Source format | ERDDAP offered NetCDF; the collector requested a `.nc` response and retained its bytes unchanged until the test payload was deleted at the user's request |
| Advertised variable | `thetao_mean`, average ocean temperature, unit `degree_C` |
| Spatial metadata | Global WGS 84 grid; 0.05-degree latitude and longitude spacing |
| Candidate time metadata | The acquired response contains two time coordinates, 2000-01-01 and 2010-01-01 UTC. The product title says baseline 2000–2019 while ERDDAP coverage ends in 2010; Bio-ORACLE documents decadal statistics, but the exact averaging windows still need reconciliation. |
| Terms metadata | The ERDDAP layer metadata states the data may be used and redistributed for free and includes accuracy and liability disclaimers. Retain the required v3.0 citation; this record does not authorise public payload redistribution. |

The metadata describes a global grid and source variables, but does not establish local coverage, marine-mask behaviour, missingness, coastal-cell suitability or compatibility with the OBIS occurrences. The documented surface layer represents the top 0–0.49 m in the raw Copernicus source; its ecological fit to an eventual focal species is unresolved.

## Bounded feasibility query

The initial collector supported this explicit candidate query:

- Dataset ID: `thetao_baseline_2000_2019_depthsurf`
- Variable: `thetao_mean`
- Requested longitude bounds: 79–82°E
- Requested latitude bounds: 5–10°N
- Time selection: full UTC coordinate extent advertised for the chosen variable
- Output at acquisition time: a publisher ERDDAP NetCDF response under `data/raw/bio_oracle/<dataset-id>/`, with a timestamped filename and adjacent local manifest; both local files were later deleted at the user's request
- Generating artefact: [`bio_oracle_layers.py`](../../src/data_collection/bio_oracle_layers.py)

The bounds were a deliberately small Sri Lanka-adjacent feasibility window aligned with the project's regional preference. They are not an approved study area, an EEZ polygon or a final modelling boundary. The regional raster was received as NetCDF and later deleted; no values were converted, filtered or joined.

## Acquisition outcome and remaining evidence

The initial direct request from this execution host to the Bio-ORACLE ERDDAP endpoint failed at DNS resolution on 8 October. A bounded retry succeeded on 9 October and returned 103,800 bytes. The user later requested deletion of this test payload and its adjacent local manifest; neither is currently retained. The retrieval timestamp, exact query, checksum and historical read-only inspection are documented in the [source record](2026-10-09-source-bio-oracle-oceantemperature.md). The acquisition and inspection establish neither a verified marine mask nor compatibility or suitability.

The test NetCDF's structure, coordinate arrays, units, fill sentinel and simple non-fill value counts/ranges remain historical evidence in the [source record](2026-10-09-source-bio-oracle-oceantemperature.md); they cannot be rechecked against the deleted payload. Under [D-047](2026-10-09-decision-bio-oracle-catalog-intake.md), the collector now inventories Bio-ORACLE v3 and supports all-variable, all-layer regional retrieval across the available 2000–2100 horizon. D-048 later fixed the rectangle from published EEZ extrema. The first catalogue-wide retrieval completed for 356 layers before its folder was deleted; a subsequent manual run has 355/356 layers verified and one incomplete response. See the [regional source record](2026-10-09-source-bio-oracle-sri-lanka-catalog.md) for its audit. The source review and code do not establish feature selection, integration, model results or human acceptance.

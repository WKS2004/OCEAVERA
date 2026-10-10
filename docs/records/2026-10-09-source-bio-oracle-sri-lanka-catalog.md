# Bio-ORACLE v3 regional catalogue and data intake

- **Retrieval date:** 9 October 2026
- **Publisher:** Bio-ORACLE consortium, ERDDAP service
- **Catalogue:** [Bio-ORACLE ERDDAP all-datasets table](https://erddap.bio-oracle.org/erddap/tabledap/allDatasets.html)
- **Product documentation:** [Bio-ORACLE data documentation](https://www.bio-oracle.org/documentation.php)
- **Collector:** [`bio_oracle_layers.py`](../../src/data_collection/bio_oracle_layers.py)
- **Scope decision:** [D-047](2026-10-09-decision-bio-oracle-catalog-intake.md)
- **Collection rectangle:** [D-048](2026-10-09-decision-bio-oracle-sri-lanka-bbox.md)

## Requested collection

The user selected the axis-aligned rectangle made from the minimum and maximum
coordinates of the Sri Lankan EEZ feature, rather than using the EEZ polygon as
the extraction mask. The inclusive bounds are 77.02333333333333–85.23291666666667°
E and 2.5665–11.44883333333333° N. The catalogue collector requests every
gridded data variable for each in-scope Bio-ORACLE v3 layer and applies the
requested 2000-01-01 through 2100-01-01 time window where a layer has multiple
time values.

This rectangle is a source-collection extent. ERDDAP selects eligible grid
coordinate centers within the latitude/longitude bounds. It does not apply the
EEZ polygon, a marine-only mask, or a land mask; returned cells can therefore
include land and water outside the EEZ polygon. The rectangle does not define
the later modelling population or domain.

## Catalogue and layer inventory

At retrieval, the ERDDAP catalogue returned 357 rows. The collector identified
356 accessible Bio-ORACLE v3 gridded datasets whose catalogue extents intersect
the selected rectangle. All 356 layer metadata records resolved, and the plan
selected 2,392 data variables with no layers outside the requested time window.
The inventory is:

| Product family | Layers | Data variables | Advertised time coordinates |
| --- | ---: | ---: | --- |
| Baseline 2000–2018 | 28 | 168 | 2000 and 2010 |
| Baseline 2000–2019 | 17 | 102 | 2000 and 2010 |
| Baseline 2000–2020 | 10 | 60 | 2000 and 2010 |
| SSP1-1.9 | 50 | 342 | 2020–2090, eight values per layer |
| SSP1-2.6 | 50 | 342 | 2020–2090, eight values per layer |
| SSP2-4.5 | 50 | 342 | 2020–2090, eight values per layer |
| SSP3-7.0 | 50 | 342 | 2020–2090, eight values per layer |
| SSP4-6.0 | 50 | 342 | 2020–2090, eight values per layer |
| SSP5-8.5 | 50 | 342 | 2020–2090, eight values per layer |
| Static terrain characteristics | 1 | 10 | One static coordinate labelled 1970 |
| **Total** | **356** | **2,392** | |

Bio-ORACLE describes v3 as ten decadal steps from 2000 to 2100 and defines
present-day conditions as 2000–2020. Its download manager offers the present
period in two decades, 2000–2010 and 2010–2020; the documentation explicitly
states that yearly data are not provided. In the retained layer metadata, all
55 baseline grids have two time coordinates (2000 and 2010), all 300 SSP grids
have eight (2020, 2030, 2040, 2050, 2060, 2070, 2080 and 2090), and static
terrain has one coordinate labelled 1970. These counts were checked across all
356 layer manifests and metadata caches. Direct reads of representative
downloaded NetCDF coordinate arrays agree: the chlorophyll baseline payload
contains 2000-01-01 and 2010-01-01; its SSP1-1.9 payload contains 2020-01-01
through 2090-01-01 at ten-year steps; the terrain payload contains 1970-01-01.

The 2000–2018, 2000–2019 and 2000–2020 baseline suffixes are catalogue product
titles, not annual observations for every intervening year. Bio-ORACLE defines
the present-day product at catalogue level as 2000–2020 and offers separate
decade selections for 2000–2010 and 2010–2020; it does not provide yearly
values. However, the downloaded ERDDAP metadata lists only time coordinates
2000 and 2010 and does not identify the exact averaging window attached to
each coordinate. Because individual baseline titles end in 2018, 2019 or 2020,
the metadata reviewed here cannot confirm that every specific layer includes
the full 2018–2020 period. Thus a 2010–2020 baseline decade is offered by the
publisher, but its coverage through 2020 is not verified for every downloaded
layer from title and coordinate labels alone.

The 2020–2100 SSP label does not mean there is a separate value at every year
or a 2100 coordinate. The 2090-labelled SSP slice is consistent with the final
2090–2100 decade in Bio-ORACLE's documented decadal horizon; this interval
interpretation follows the publisher's decade scheme, while the actual ERDDAP
coordinate is 2090. The 1970 terrain coordinate is a static-data convention,
not an environmental observation from 1970. See the [Bio-ORACLE layer documentation](https://www.bio-oracle.org/documentation.php)
and [download manager](https://www.bio-oracle.org/downloads-to-email.php).

## Acquisition evidence and status

The collector writes one publisher-format NetCDF response per layer beneath
`data/raw/bio_oracle/<dataset-id>/`, together with an adjacent JSON manifest.
Each layer manifest records its dataset and variable metadata, catalogue and
layer metadata response hashes, exact query URL, requested rectangle and time
window, response size, NetCDF media type and SHA-256. The run manifest records
per-layer completion or failure and is updated as layers finish. Raw payloads,
manifests and cached catalogue metadata remain excluded from Git.

The bulk acquisition completed with 356 of 356 layers complete, zero failed or
pending layers, 2,392 variables, 356 per-layer manifests and 4,017,532,960
payload bytes (3.742 GiB). The run reused five earlier payloads only after the
query, rectangle, requested time window, file size and SHA-256 matched; it
downloaded the other 351 in this run. At retrieval, the local run receipt
recorded every layer status, variable list, response byte count and SHA-256;
the receipt and per-layer manifests were later deleted with the raw folder at
the user's request. The ERDDAP catalogue response SHA-256 is
`79bc42319fc79251e380fbe290a2d481932f02e8943e50c5d124a245257593a2`.

Before removal, an integrity pass checked all 356 payload paths, NetCDF
signatures, byte counts, SHA-256 values and adjacent layer manifests against
the run manifest. At that time all 356 metadata cache records were present, no
`.part` or temporary manifest files remained, and the payload/cache tree was
ignored by Git.

## Local retention history and run audits

After the integrity pass, the user requested removal of the entire
`data/raw/bio_oracle/` folder. On 9 October 2026, all 356 regional NetCDF
payloads (4,017,532,960 bytes), 713 JSON query/run receipts and cached
catalogue metadata, and the directory marker were deleted. The user later ran
the fixed collector manually, creating the partial snapshot audited below.
The user then deleted that snapshot before requesting the final acquisition
recorded in the following section.

### Earlier partial manual run audit (subsequently deleted)

- **Run ID:** `20261009T153556595419Z`; the saved run manifest reports 357
  catalogue rows, 356 regional candidates and 356 planned layers for the
  D-048 bounds and requested 2000–2100 UTC window.
- **Outcome:** Partial, not complete. The run manifest records 355 completed
  layers and one failed layer, with no pending layers. The complete layer
  manifests account for 2,385 of 2,392 requested variables. The failed layer is
  `thetao_ssp119_2020_2100_depthsurf`; its seven variables are
  `thetao_ltmax`, `thetao_ltmin`, `thetao_max`, `thetao_mean`, `thetao_min`,
  `thetao_range` and `thetao_sd`.
- **Failure evidence:** The worker records an `IncompleteRead` while reading
  the temperature response. There is no completed NetCDF payload or per-layer
  completion manifest for that dataset. Its `.part` response file is 1,048,584
  bytes and is not counted as a successful download.
- **Integrity audit:** All 355 completed NetCDF payloads were present. Their
  byte counts and SHA-256 fingerprints match their per-layer manifests; each
  has a recognised NetCDF signature. The manifests also match the run ID,
  rectangle and requested time window. No mismatch was found. Together these
  files contain 4,004,366,652 payload bytes and 2,385 data variables. This
  verifies transfer integrity and recorded query scope, not every array's
  scientific contents, units or ecological suitability.
- **Local files at audit:** `data/raw/bio_oracle/` contained 355 NetCDF files,
  355 per-layer manifests, 356 cached layer-metadata files, one run manifest
  and the one incomplete `.part` file. The payload folder remains ignored by
  Git.

This section describes the earlier partial manual snapshot only. Its incomplete
`.part` response and the 355 complete payloads were removed when the user
deleted that entire raw folder; they are not part of the final snapshot below.

### Final Python-file download and integrity audit

- **Run ID:** `20261009T163625858012Z`. The run manifest reports 357 catalogue
  rows, 356 regional candidates and 356 planned layers.
- **Requested scope:** the D-048 rectangle, 77.02333333333333–85.23291666666667°
  E and 2.5665–11.44883333333333° N; temporal layers requested from
  2000-01-01 through 2100-01-01 UTC.
- **Outcome:** Complete. All 356 layers and 2,392 variables completed, with no
  failed or pending layers. All 356 payloads were downloaded in this run; none
  were reused. The NetCDF payloads total 4,017,532,960 bytes (about 3.742 GiB).
- **Independent integrity audit:** Re-read every payload and compared its byte
  count, SHA-256 and NetCDF signature with the run manifest and per-layer
  receipt. All 356 matched. Every receipt has the run ID and requested spatial
  rectangle; the 355 time-dependent layers also match the requested 2000–2100
  bounds. The static `terrain_characteristics` layer correctly has no requested
  time bound and carries its publisher-labelled static coordinate instead.
  Each receipt's variable list matches the run manifest. No `.part` files or
  integrity mismatches were found.
- **Retention:** The current ignored raw folder contains 356 NetCDF payloads
  and 356 per-layer manifests. `git check-ignore` confirms the payload path is
  excluded from Git. The run report is
  `data/raw/bio_oracle/_runs/20261009T163625858012Z_bio_oracle_catalog.json`.

This verifies transfer integrity and recorded query scope, not every array's
scientific contents, units, marine coverage or ecological suitability. The
source time-axis interpretation and unresolved layer compatibility questions
above remain unchanged.

No payload is regridded, flattened, masked, cleaned or integrated during
acquisition. Environmental extraction, marine-cell interpretation, temporal
alignment with OBIS, layer compatibility review and predictor selection remain
later work and require their own evidence.

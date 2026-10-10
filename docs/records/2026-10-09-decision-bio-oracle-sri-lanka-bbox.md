# Decision D-048 — Sri Lankan EEZ bounding rectangle for Bio-ORACLE intake

- **ID:** D-048
- **Date:** 9 October 2026
- **Question:** Which spatial extent should the catalog-wide Bio-ORACLE intake use?
- **Context:** D-047 requires an explicit regional extent. The user compared the bounds of the current OBIS Area 230 CSV with the published extent of the Sri Lankan EEZ and selected the EEZ polygon's minimum/maximum latitude and longitude to form a rectangular collection area. Area 230 remains the biological collection scope under D-034 and is not declared equivalent to this rectangle or to Sri Lanka's EEZ polygon.
- **Evidence and source:** The Flanders Marine Institute's World EEZ v12 (2023) record for Sri Lanka, MRGID 8346, lists minimum latitude 2°33′59.4″ N, maximum latitude 11°26′55.8″ N, minimum longitude 77°01′24″ E and maximum longitude 85°13′58.5″ E. See the [Marine Regions feature record](https://www.marineregions.org/gazetteer.php?id=8346&p=details), [dataset citation and description](https://www.marineregions.org/sources.php), and [methodology](https://www.marineregions.org/eezmethodology.php). The publisher describes v12 as a GIS product built from treaty boundaries, calculated median lines where applicable and 200-nautical-mile limits; it notes a deviation from the UNCLOS EEZ definition in its treatment of internal, archipelagic and territorial waters. Sri Lanka's WGS 84 baseline points are published in the [2012 Gazette](https://msdi.navy.lk/pdf/supdoc/baselines_determining.pdf).
- **Decision:** Use the axis-aligned rectangle defined by those published EEZ extent extrema for Bio-ORACLE source intake. The geographic bounding values converted from the source DMS are west 77.02333333333333° E, east 85.23291666666667° E, south 2.5665° N and north 11.44883333333333° N. Represent the rectangle in GeoJSON coordinate order (longitude, latitude) as:

  ```json
  {
    "type": "Polygon",
    "coordinates": [[
      [77.02333333333333, 2.5665],
      [85.23291666666667, 2.5665],
      [85.23291666666667, 11.44883333333333],
      [77.02333333333333, 11.44883333333333],
      [77.02333333333333, 2.5665]
    ]]
  }
  ```

- **Rationale:** This applies the user's requested minimum/maximum EEZ-coordinate method and creates a deterministic region that can be supplied to ERDDAP's rectangular gridded-subset query. The collector records the rectangle's corners and source in each query manifest.
- **Consequences and limitations:** The source geometry is an EEZ polygon; this decision uses only its rectangular extent. Bio-ORACLE selects cells by inclusive latitude and longitude coordinate values, so land cells and marine cells outside the EEZ polygon may be returned. No polygon mask, marine-only filter, or clip is applied during acquisition. The rectangle is a collection boundary only and does not select the final modelling population or domain. Bio-ORACLE's grid resolution is 0.05 degrees; requested limits therefore select eligible grid-coordinate centers rather than creating finer resolution.
- **Status:** Accepted and applied for source collection. The latest Python-file run applied the same bounds to all 356 selected regional v3 grids and downloaded all 2,392 variables with zero failures; every payload passed the independent integrity and query-scope audit. The user deleted the earlier complete snapshot and subsequent partial manual snapshot before this run. See the [regional intake source record](2026-10-09-source-bio-oracle-sri-lanka-catalog.md) for all run histories. The final modelling domain remains a separate shared decision.
- **Affected documents and artefacts:** [Bio-ORACLE collector](../../src/data_collection/bio_oracle_layers.py), [source guide](../../src/README.md), [data directory guide](../../data/README.md), [storage conventions](../data/data-storage-and-provenance.md), [readiness review](../project/repository-readiness-and-alignment.md), [D-047](2026-10-09-decision-bio-oracle-catalog-intake.md), [regional intake source record](2026-10-09-source-bio-oracle-sri-lanka-catalog.md), and [source extent record](2026-10-09-source-marine-regions-sri-lanka-eez-bounds.md).
- **Supersedes / superseded by, if applicable:** Does not supersede D-034's Area 230 biological collection scope or define a final modelling domain; it resolves only D-047's previously open Bio-ORACLE source-collection bounds.

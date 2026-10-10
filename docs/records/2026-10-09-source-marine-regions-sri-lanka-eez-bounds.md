# Source record — Marine Regions Sri Lankan EEZ extent

- **Resource ID / record date / status:** MARINEREGIONS-EEZ-MRGID-8346-EXTENT; 9 October 2026; metadata inspected and used to define a collection rectangle; source polygon not downloaded locally
- **Publisher and resource title:** Flanders Marine Institute (VLIZ), Maritime Boundaries Geodatabase: Maritime Boundaries and Exclusive Economic Zones (200NM), version 12
- **Stable publisher URL, DOI or accession:** [Sri Lankan EEZ feature, MRGID 8346](https://www.marineregions.org/gazetteer.php?id=8346&p=details); dataset DOI [10.14284/632](https://doi.org/10.14284/632)
- **Exact version, release or feature identifier:** World EEZ v12, released 25 October 2023; Sri Lankan Exclusive Economic Zone, MRGID 8346
- **Retrieval date and method:** 9 October 2026; feature extent and methodology read from the publisher's public web pages. The full-world GeoPackage/shapefile and feature GML were not downloaded into the repository.
- **Exact query and filters:** Feature lookup by MRGID 8346; no coordinate or attribute filtering applied to the published extent metadata.
- **Published extent extrema:** Minimum latitude 2°33′59.4″ N; maximum latitude 11°26′55.8″ N; minimum longitude 77°01′24″ E; maximum longitude 85°13′58.5″ E. Converted from the source's DMS values to west 77.02333333333333° E, east 85.23291666666667° E, south 2.5665° N and north 11.44883333333333° N.
- **Derived collection geometry:** A closed rectangle in WGS 84 longitude/latitude order: `[77.02333333333333, 2.5665]`, `[85.23291666666667, 2.5665]`, `[85.23291666666667, 11.44883333333333]`, `[77.02333333333333, 11.44883333333333]`, and back to `[77.02333333333333, 2.5665]`. This is the axis-aligned envelope from the source polygon extrema, not the source EEZ polygon.
- **Licence / terms / attribution:** The feature page points to the v12 geodatabase citation and DOI; terms for redistributing source boundary geometry were not independently assessed because the geometry was not downloaded or redistributed. Cite Flanders Marine Institute (2023), *Maritime Boundaries Geodatabase: Maritime Boundaries and Exclusive Economic Zones (200NM), version 12*, DOI 10.14284/632.
- **Method and limitations:** Marine Regions v12 describes polygon areas calculated from normal/straight baselines, treaty boundaries and median lines where delimitation agreements are absent, with a 200-nautical-mile outer limit. Its methodology page notes that its EEZ product includes territorial seas, internal waters and archipelagic waters, which it identifies as a deviation from the UNCLOS EEZ definition. Sri Lanka's Navy-hosted 2012 Gazette publishes WGS 84 baseline points, not this complete EEZ polygon. The selected rectangle is intentionally larger than the irregular EEZ and may contain land and non-EEZ waters. It is an acquisition window, not a legal boundary or modelling-domain determination.
- **Generating artefacts and decision:** [D-048 collection-extent decision](2026-10-09-decision-bio-oracle-sri-lanka-bbox.md); [Bio-ORACLE collector preset](../../src/data_collection/bio_oracle_layers.py). Per-layer Bio-ORACLE manifests record the actual bounds and rectangle coordinates used.

## Publisher references

- [Marine Regions feature page and extent](https://www.marineregions.org/gazetteer.php?id=8346&p=details)
- [Marine Regions dataset citation and version details](https://www.marineregions.org/sources.php)
- [Marine Regions methodology](https://www.marineregions.org/eezmethodology.php)
- [Sri Lanka Navy-hosted 2012 Gazette of WGS 84 baselines](https://msdi.navy.lk/pdf/supdoc/baselines_determining.pdf)

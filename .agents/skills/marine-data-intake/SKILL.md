---
name: marine-data-intake
description: Assess or acquire OCEAVERA OBIS occurrences and Bio-ORACLE layers, recording provenance, feasibility and spatial-temporal-depth compatibility.
---

# Marine data intake

Read the [data rule](../../rules/data-management.md) and [governance](../../../docs/data/data-storage-and-provenance.md). Consult current authoritative publisher documentation when acquisition is requested.

1. Define a bounded candidate query and assess a feasibility sample before selecting final species/region. Record actual access, release, terms, coverage and quality evidence.
2. Preserve downloads unchanged; copy the [manifest](../../../docs/templates/data-source-record.md) into `docs/records/`, following the [record conventions](../../../CONTRIBUTING.md#project-evidence-records) for each resource. Keep metadata outside ignored payload directories.
3. Record each actual source file format; do not assume all OBIS or Bio-ORACLE resources use the example format. Assess occurrence taxonomy, coordinates, dates, duplicates/repeats and sampling coverage. For layers, inspect units, resolution, coordinate system, marine mask, temporal statistic and depth.
4. Keep full environmental arrays in their source format. Extract values for justified modelling locations into derived tables; use GeoParquet for compatible spatial tables and Parquet for compatible non-spatial ML tables. Do not flatten a complete raster just to create a tabular workflow.
5. Propose an explicit extraction/join rule, quantify unmatched records and approximations, and retain before/after counts and generating artefacts. Record actual derived formats in the dataset manifest.
6. Update the [dictionary](../../../docs/templates/data-dictionary.md) through a dated record and the [decision register](../../../docs/project/decision-register.md) for evidence-based choices.

Return provenance, compatibility findings and limitations. Do not infer absence or dataset feasibility from a candidate-source description.

## Source-specific review

For focal-species feasibility, occurrence provenance or environmental extraction choices, read the [source feasibility and integration reference](references/source-feasibility-and-integration.md).

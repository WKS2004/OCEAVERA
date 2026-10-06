# Data directory

| Directory | Purpose |
| --- | --- |
| `raw/` | Unmodified source downloads in the formats actually supplied |
| `interim/` | Reproducible cleaning, extraction and spatial integration products; GeoParquet for compatible spatial tables |
| `processed/` | Reviewed analysis-ready tables; GeoParquet where geometry is retained, Parquet for compatible non-spatial ML tables |

**Current state:** no acquired data. The directories contain structural markers only.

The existing `raw/`, `interim/` and `processed/` paths serve the proposed Bronze, Silver and Gold lifecycle roles respectively; no duplicate lifecycle directories are planned.

Data payloads are excluded from Git by default. Put tracked manifests, dictionaries, citations and processing notes in `docs/records/` under the [record conventions](../CONTRIBUTING.md#project-evidence-records). See [data storage and provenance](../docs/data/data-storage-and-provenance.md) before acquiring or sharing data. The [source manifest](../docs/templates/data-source-record.md) records individual resources; the [dictionary](../docs/templates/data-dictionary.md) describes the integrated dataset.

Preserve publisher files unchanged: CSV occurrence downloads and NetCDF environmental arrays are anticipated examples, not guaranteed packaging for any unverified resource. Extract selected raster values at modelling locations into derived tables; do not flatten complete environmental grids. Record the actual format/specification version in each dataset manifest. Manifests and compact metadata use JSON. COG (`.tif`) and ONNX (`.onnx`) remain optional, unfinalised future BLUEVERSE integration suggestions, not required OCEAVERA data/model formats.

## Member responsibilities

Sanuda leads biological data preparation; Ushan environmental preparation and integration; Adithya integrated-dataset cleaning. Wanshaja reviews these inputs. All four contribute to feasibility and final dataset decisions. See the [complete responsibility plan](../docs/project/member-responsibilities.md) for all activities, shared roles and handovers. Planned ownership does not establish an artefact or completed contribution, and technical execution remains pending authorisation.

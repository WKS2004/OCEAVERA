# Data directory

| Directory | Purpose |
| --- | --- |
| `raw/` | Unmodified source downloads |
| `interim/` | Reproducible intermediate products |
| `processed/` | Reviewed analysis-ready datasets |

**Current state:** no acquired data. The directories contain structural markers only.

Data payloads are excluded from Git by default. Put tracked manifests, dictionaries, citations and processing notes in `docs/records/` under the [record conventions](../CONTRIBUTING.md#project-evidence-records). See [data storage and provenance](../docs/data/data-storage-and-provenance.md) before acquiring or sharing data. The [source manifest](../docs/templates/data-source-record.md) records individual resources; the [dictionary](../docs/templates/data-dictionary.md) describes the integrated dataset.

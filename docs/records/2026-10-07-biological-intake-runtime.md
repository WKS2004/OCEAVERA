# Decision record

- **ID:** D-033
- **Date:** 7 October 2026
- **Question:** Which runtime and dependencies should the initial reusable biological occurrence collector use?
- **Context:** The user initially selected Python standard library for the reusable collector. A later explicit request selected AWS Open Data GeoParquet and direct GeoParquet output; D-035 adds DuckDB for remote Parquet access and writing. The modelling runtime and dependency stack remain undecided under D-014.
- **Options considered:** Python standard library; R with the OBIS robis client; defer reusable collection code until a project-wide runtime is selected. For AWS GeoParquet processing, DuckDB is required in addition to the standard-library API client.
- **Evidence and source references:** Explicit user selections on 7 October 2026; [OBIS occurrence API](https://api.obis.org/#/Occurrence/get_occurrence), [OBIS Open Data layout](https://github.com/iobis/obis-open-data), [DuckDB remote Parquet access](https://duckdb.org/docs/current/core_extensions/httpfs/https), and repository guidance in [marine-data-intake](../../.agents/skills/marine-data-intake/SKILL.md) and [data storage and provenance](../data/data-storage-and-provenance.md).
- **Decision:** Retain Python 3.10+ standard library for the small Area 230 API membership index; use DuckDB with `httpfs` and `spatial` extensions for matching AWS GeoParquet source files and direct GeoParquet output. This limited intake choice does not select the modelling runtime.
- **Rationale:** Python's standard library can fetch the small API index but cannot read remote Parquet and emit GeoParquet. DuckDB supports remote Parquet range reads and GeoParquet metadata on output, matching the user's requested source and final format.
- **Consequences and limitations:** The full AWS object scan and export remain unrun. The S3 data are organised by source dataset rather than Area 230; candidate file sizes and API/AWS snapshot parity require assessment. D-014 remains open for the modelling environment.
- **Status:** the D-035 DuckDB processing choice is superseded by D-036; Python standard library is selected for the current API downloader and JSON-to-CSV converter. The modelling runtime remains open.
- **Affected documents and artefacts:** [OBIS occurrence collector](../../src/data_collection/obis_occurrences.py), [source code index](../../src/README.md), [D-035 method record](2026-10-07-decision-obis-area-230-geoparquet.md), and [readiness review](../project/repository-readiness-and-alignment.md).
- **Supersedes / superseded by, if applicable:** Superseded in processing scope by D-035; no project-wide modelling runtime decision is made.

# Decision D-035 — OBIS Area 230 AWS GeoParquet extraction

- **Date:** 7 October 2026
- **Status:** Superseded by D-036; the recorded export attempt failed final field-schema validation and retained no output
- **Decision owner:** Project user, explicitly selected AWS Open Data and direct GeoParquet output
- **Topic:** Retrieve all Area 230 records without syncing the full OBIS AWS collection

## Decision

Use the OBIS AWS Open Data occurrence GeoParquet as the source of full
occurrence rows. Use the OBIS API to retrieve a paginated Area 230 membership
index containing `id` and `dataset_id`, with `areaid=230`, `absence=include`
and `dropped=include`. Also request the four access-page fields (`freshwater`,
`terrestrial`, `natio`, `series`) absent from the AWS source schema so the
final table can carry the access-page schema. Resolve the source-dataset files in
AWS, join the API IDs to AWS `_id`, and write the complete matched rows directly
to GeoParquet. Do not sync the full AWS collection.

Apply no taxon, date, depth, quality, or overall record-count restriction.
Retain all taxa and all rows returned by the OBIS Area 230 membership query,
including absence and dropped records. The API query does not apply a taxon,
date, depth, quality or overall record-count restriction. Emit the fields
listed on the OBIS Data Access page as columns, and retain the AWS `source`,
`interpreted`, extensions, quality arrays and geometry so the full publisher
record is preserved.

## Rationale and feasibility evidence

The user explicitly selected AWS Open Data and GeoParquet after correcting the
earlier API/CSV approach. OBIS documents AWS GeoParquet as suitable for large
subsets and organises its approximately 50 GB collection as one file per source
dataset rather than one file per geographic area. The Area 230 metadata
endpoint identifies the publisher area but does not return its polygon.
Using OBIS's own area-filtered membership IDs avoids inventing a boundary and
keeps Area 230 membership semantics. See the [feasibility assessment](2026-10-07-obis-area-230-geoparquet-feasibility.md),
[OBIS Data Access](https://obis.org/data/access/) and [OBIS Open Data README](https://github.com/iobis/obis-open-data).

DuckDB can read remote Parquet through HTTP range requests and write GeoParquet
metadata. The proposed method reads only the source-dataset objects referenced
by the Area 230 index; it does not download the entire S3 prefix. Because each
source file can contain out-of-area records, the selected object sizes and
actual bytes read are still unknown. The metadata preflight reports the
candidate object sizes before the record query.

## Safeguards and consequences

- The collector's default invocation performs no collection. `--assess`
  retrieves the small membership index and sequential S3 object headers
  without reading Parquet occurrence payloads. `--download` is separate and requires
  typed confirmation unless `--yes` is explicitly supplied.
- The export uses one DuckDB thread, stops if the candidate object set reaches
  the documented approximate full-collection size, and verifies every API ID
  maps to exactly one AWS output row before retaining the GeoParquet.
- If the live API and AWS source snapshot differ, the export fails closed and
  does not claim completeness. A subsequent source-version decision may be
  needed; do not fill gaps silently with API rows or remove records.
- The final file is a derived area subset under `data/interim/`, not an
  unchanged S3 publisher object. It is written directly as GeoParquet, without
  a CSV intermediate, and has a JSON provenance receipt.
- The earlier JSON/CSV acquisition payloads were removed at the user's
  request. Their historical counts and fingerprints remain in the
  [source record](2026-10-07-source-obis-area-230-all-occurrences.md); no
  occurrence payload is currently retained.
- DuckDB is selected only for this intake workflow. The project-wide modelling
  environment remains open under D-014.

## Execution outcome — 8 October 2026

The metadata assessment completed for the live source state: the OBIS index
reported 23,934 records over 24 pages; the four supplemental fields had zero
non-null values; and all 132 corresponding AWS object headers returned HTTP
200. Their advertised full object sizes totalled 8,561,850,485 bytes (8.562
decimal GB). This total is not a measurement of network transfer.

One export attempt scanned the matching source objects, produced temporary
per-source parts, and reached the global completeness check. The row count and
record-ID pairs matched the 23,934 API entries, but four required named
access-page fields were absent from the output schema. The collector failed
closed and removed its temporary parts and spill directory; no final
GeoParquet or receipt was retained. A later assessment confirmed the four API
values were null. A local correction to the six-column temporary-table insert
was made after the failed run; it has not been exercised against remote data.

The script performs OBIS API GET requests, S3 HEAD checks, DuckDB HTTP range
reads from public AWS objects, and may retrieve the `httpfs` and `spatial`
DuckDB extensions on first use. It contains no upload or remote-write
operation. No dataset was uploaded to OpenAI or another destination by this
script. Exact transferred bytes were not measured, so the user's reported
approximately 20 GB cannot be independently reconciled with the candidate
object-size total. After the user withdrew permission for further downloads,
no additional network requests or payload reads were made. See the full
[export attempt record](2026-10-08-obis-area-230-export-attempt.md).

## Supersession

On 8 October 2026, the user selected direct OBIS API JSON retrieval followed by
CSV conversion and explicitly authorised that retrieval. D-036 supersedes the
AWS GeoParquet method for the current Area 230 collection. The earlier export
failure remains part of the acquisition history; the API route does not reuse
or continue that AWS scan.

## Affected artefacts

- [Collector](../../src/data_collection/obis_occurrences.py)
- [Storage and provenance](../data/data-storage-and-provenance.md)
- [Readiness review](../project/repository-readiness-and-alignment.md)
- [Replacement API/CSV decision D-036](2026-10-08-decision-obis-area-230-api-csv.md)

# OBIS Area 230 export attempt outcome

- **Date:** 8 October 2026
- **Status:** Failed final schema validation; no occurrence dataset retained; no retry authorised
- **Scope:** Record the live Area 230 metadata assessment, AWS scan failure, local cleanup and transfer-measurement limits.

## Metadata assessment

The OBIS Area 230 occurrence index returned 23,934 records over 24 pages. The
assessment requested the membership identifiers plus the four access-page
fields needed because they are absent from the AWS source schema: `freshwater`,
`terrestrial`, `natio` and `series`. All four fields were null across the
assessment snapshot.

The index referenced 132 AWS source-dataset objects. All 132 sequential S3
header checks returned HTTP 200. Their advertised full object sizes summed to
8,561,850,485 bytes (8.562 decimal GB). This is the size of the complete
candidate objects, not a measurement of bytes transferred by the export.

## Export attempt

The collector queried the matching AWS source objects and wrote per-source
temporary GeoParquet parts. The final completeness audit found that the output
row count and record-ID pairs matched the 23,934 API entries, but four required
Data Access fields were absent from the schema. The collector raised an error
and removed its temporary parts and DuckDB spill directory. No final
GeoParquet dataset or receipt was retained. The local output directory was
empty on inspection, and no Python download process was running.

A local code review then found that the supplemental six-column membership
table was being inserted with only two SQL placeholders. The placeholder
count was corrected offline. The corrected exporter has not been run against
remote data. A later attempt was stopped before it queried AWS Parquet
payloads; no further payload scan was made after the user prohibited further
downloads without explicit permission.

## Network and retention limits

The collector makes OBIS API `GET` requests and S3 `HEAD` checks. DuckDB's
remote Parquet reads use HTTP range reads from AWS; the collector also asks
DuckDB to `INSTALL` its `httpfs` and `spatial` extensions, which may retrieve
extension software on first use. The script has no HTTP upload, S3 write or
other remote data-publishing operation. The Area 230 source rows were read
from public OBIS/AWS endpoints; the script did not upload an occurrence
dataset to OpenAI or another destination.

Exact transferred bytes were not instrumented or recorded. The reported
approximately 20 GB is the user's network-usage observation; it cannot be
independently reconciled with the advertised candidate-object size, because
range reads, metadata, extension retrieval and retries are not represented by
that total. The failed local export retained no occurrence output. At the time
of this record, the user prohibited further downloads; the later explicit
permission for the API/CSV route is recorded under [D-036](2026-10-08-decision-obis-area-230-api-csv.md).

## Affected artefacts

- [Collector](../../src/data_collection/obis_occurrences.py)
- [D-035 acquisition decision](2026-10-07-decision-obis-area-230-geoparquet.md)
- [Feasibility assessment](2026-10-07-obis-area-230-geoparquet-feasibility.md)
- [Readiness review](../project/repository-readiness-and-alignment.md)
- [Replacement API/CSV decision](2026-10-08-decision-obis-area-230-api-csv.md)

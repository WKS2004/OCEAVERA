# OBIS Area 230 AWS GeoParquet feasibility

- **Date:** 7 October 2026
- **Status:** Historical AWS feasibility assessment; method superseded by D-036 after the failed export attempt
- **Purpose:** Determine whether an Area 230-only GeoParquet subset can be produced from OBIS AWS Open Data without syncing the approximately 50 GB full collection.
- **Scope:** Documentation and metadata review only; no occurrence Parquet object was downloaded or queried in this assessment.

## Evidence reviewed

- OBIS [Data Access](https://obis.org/data/access/) recommends the AWS-hosted GeoParquet for programmatic work with large subsets and describes the data fields supplied by providers and added by OBIS.
- The official [OBIS Open Data repository](https://github.com/iobis/obis-open-data) documents one GeoParquet object per source dataset under `s3://obis-open-data/occurrence/`, a complete local sync of approximately 50 GB, an Athena query path and the AWS record schema. The top-level source schema includes `_id`, `dataset_id`, `node_ids`, `source`, `interpreted`, `extensions`, `missing`, `invalid`, `flags`, `dropped`, `absence` and WKB `geometry`. Absence and dropped flags are included in this AWS collection.
- A metadata-only `GET https://api.obis.org/v3/area/230` on 7 October 2026 returned Area 230 as `Sri Lanka`, type `obis`, without a geometry field. The occurrence API query can use `areaid=230`; the previous live query reported 23,934 records with both absence and dropped records included. That count is historical and may differ from the AWS source release.
- DuckDB's official documentation describes remote Parquet range reads over HTTP(S), and GeoParquet metadata on Parquet output. These capabilities support filtered access and direct GeoParquet writing without a full local bucket sync.

## Feasibility analysis

The AWS object layout has no Area 230 prefix or area partition. A direct S3 prefix download cannot isolate Sri Lanka. A spatial filter also cannot use an Area 230 boundary from the area metadata response reviewed here.

The selected design keeps OBIS itself as the authority for Area 230 membership:

1. Page the OBIS occurrence endpoint with `areaid=230`, `absence=include` and `dropped=include`, requesting `id`, `dataset_id` and four additional access-page fields (`freshwater`, `terrestrial`, `natio`, `series`) absent from the AWS source schema. This supports membership and output-schema preservation; it does not limit or clean the final occurrence dataset.
2. Use each returned `dataset_id` to identify the corresponding public AWS GeoParquet object. Read those matching source-dataset files remotely and join their `_id` values to the API IDs.
3. Write matched full records directly to a GeoParquet output. The output includes the named fields on the Data Access page as columns and retains the full original AWS `source`, `interpreted`, extension, quality and geometry structures. It does not exclude absence or dropped records or apply taxon/date/depth/quality filters.
4. Compare output IDs and row counts to the full API index. If IDs are duplicated or any API ID is missing from the AWS source snapshot, abort rather than report a complete Area 230 export.

This design can avoid downloading unrelated source-dataset objects and does not sync the full bucket. It cannot guarantee a small scan: a matching source-dataset object may contain records from outside Area 230, and matching IDs may be distributed across large source files. A sequential S3 `HEAD` preflight can sum candidate object sizes without retrieving their Parquet bodies; this is an estimate of the complete candidate objects, not actual bytes read. DuckDB can use range reads, but real transfer volume depends on Parquet row groups, projections, object sizes and query execution.

## Decision and limits

Under [D-035](2026-10-07-decision-obis-area-230-geoparquet.md), the remote index-plus-AWS-object design was selected. The collector had a membership-index/object-header `--assess` mode and a separate explicit `--download` mode. The latter set DuckDB to one thread, required typed confirmation, and refused to begin if candidate full-object sizes reached the approximate full-collection size. The contemporaneous feasibility notebook had its export cell disabled by default; that notebook was later removed under D-036.

The 8 October metadata preflight reported 23,934 API records over 24 pages; all four supplemental API fields were null; and all 132 corresponding AWS headers returned HTTP 200. Their advertised full object sizes totalled 8,561,850,485 bytes (8.562 decimal GB), not actual transfer volume. One export attempt scanned the source objects and matched all 23,934 API ID pairs, but failed the final schema check because four required fields were missing. The exception path removed staged parts and no GeoParquet output remains. A local insert-arity correction was made after that attempt but was not run against remote data. Exact transferred bytes and source-version completeness are unavailable. The earlier 23,934-row API/CSV payloads were removed; their historical query and fingerprints are recorded in the [previous source record](2026-10-07-source-obis-area-230-all-occurrences.md). The [dated outcome record](2026-10-08-obis-area-230-export-attempt.md) documents the failure. The user subsequently selected and authorised the API/CSV method under D-036; the AWS method is no longer the current plan.

## Generating artefacts and publisher references

- [Python collector](../../src/data_collection/obis_occurrences.py)
- [Current API downloader](../../src/data_collection/obis_occurrences.py)
- [Current CSV converter](../../src/data_collection/obis_json_to_csv.py)
- [OBIS data access](https://obis.org/data/access/)
- [OBIS AWS Open Data README](https://github.com/iobis/obis-open-data)
- [OBIS Area API](https://api.obis.org/v3/area/230)
- [OBIS occurrence API](https://api.obis.org/#/Occurrence/get_occurrence)
- [DuckDB HTTP(S) range reads](https://duckdb.org/docs/current/core_extensions/httpfs/https)
- [DuckDB GeoParquet output metadata](https://duckdb.org/docs/current/sql/statements/copy)

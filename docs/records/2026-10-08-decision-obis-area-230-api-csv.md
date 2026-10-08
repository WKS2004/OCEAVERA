# Decision D-036 — OBIS Area 230 API JSON and CSV

- **Date:** 8 October 2026
- **Status:** Accepted current acquisition method; retrieved output is documented in the linked source record
- **Decision owner:** Project user, explicitly selected the API method and authorised the retrieval
- **Topic:** Preserve all Area 230 API occurrences as raw JSON and a verified CSV copy

## Decision

Use the OBIS v3 occurrence API at `https://api.obis.org/v3/occurrence` to
retrieve every record returned for `areaid=230`. Include both `absence` and
`dropped` records. Apply no taxon, date, depth, quality, or total-record limit;
omit the `fields` parameter so the API returns all fields it provides.

Page sequentially using OBIS's `after` cursor: the first request uses
`after=-1`; each next request uses the final record ID from the preceding
response. Use `size=1000` as page size, not as a record limit. Retain each
complete response body unchanged in a distinct JSON page file beneath
`data/raw/obis/json/`. Keep a manifest with the query, API-reported total,
per-page row counts, cursor boundaries, SHA-256 checksums and measured HTTP
response-body bytes. Do not parallelise requests.

Convert only a verified complete JSON run into one CSV under
`data/raw/obis/csv/`. The converter includes the union of top-level fields
across all response records plus all 68 named columns on the OBIS Data Access
page. It emits every record in the original page order, does not filter or
deduplicate, serialises nested arrays/objects as compact JSON strings, and
verifies each CSV row against the retained JSON source. It retains API
`aphiaID` and mirrors it as the documented `AphiaID` column; other documented
columns absent from API records are present as blank cells.
Keep the original JSON pages as the lossless source; the CSV is a convenient
tabular copy stored in `raw/` by explicit user direction.

## Completeness and failure handling

The downloader must reach the first page's API-reported total, reject missing
or repeated IDs, preserve raw pages and checksums, and mark a run complete only
when the row total and unique-ID total match. The converter must reject an
incomplete manifest, a bad checksum, a duplicate ID, a missing field or any
row/header mismatch. If retrieval or verification fails, keep completed
response pages as an incomplete run and do not publish a CSV as complete.

The API's reported count is the comparison target for that retrieval. Website
summary counts may differ from a live API query or refresh at a different
time; retain the API count and retrieval timestamp rather than silently
dropping records to match a website figure. If a later page supplies a total
and it differs, fail closed. The API has no snapshot token, so a publisher
change during pagination remains a source limitation.

For the 8 October run, the OBIS Area 230 page displayed 23,327 records, exactly
matching the API rows for which both `absence` and `dropped` are false. The
other 607 API records are flagged as dropped and/or absence (563 dropped, 50
absence, six in both sets); D-036 retains them all.

The prior AWS GeoParquet decision D-035 is superseded for the current
collection. Preserve its failed attempt as historical evidence; do not mix its
partial scan with the new API dataset.

## Rationale and publisher guidance

The user explicitly changed the method back to API JSON followed by CSV and
provided permission for the current retrieval after previously prohibiting
downloads without permission. OBIS documents the API as programmatic access
for subsets, and its official `robis` implementation follows the occurrence
endpoint with an `after` cursor and includes `absence="include"` and
`dropped="include"` options. OBIS's data-access guidance says not to
parallelise API downloads and recommends AWS for large downloads. This
collection follows the user's selected API route and keeps all requests
sequential.

## Affected artefacts

- [JSON downloader](../../src/data_collection/obis_occurrences.py)
- [JSON-to-CSV converter](../../src/data_collection/obis_json_to_csv.py)
- [Data storage and provenance](../data/data-storage-and-provenance.md)
- [Data directory guide](../../data/README.md)
- [OBIS API Swagger UI](https://api.obis.org/)
- [OBIS official API client pagination](https://github.com/iobis/robis/blob/master/R/occurrence.R)
- [OBIS data-access guidance](https://obis.org/data/access/)
- [Completed 8 October source record](2026-10-08-source-obis-area-230-api-csv.md)

# Decision D-034 — OBIS Area 230 collection scope

- **Date:** 7 October 2026
- **Status:** Area 230 scope accepted; original API/CSV acquisition method superseded by D-035
- **Decision owner:** Project user, explicitly confirmed in the conversation
- **Topic:** Complete OBIS occurrence intake for the Area 230 (“Sri Lanka”) query

## Supersession and current state

This record preserves the user's accepted collection scope: all taxa and all
records returned by the Area 230 query, including absences and dropped
records, with no taxon, date, depth, quality or total-count exclusion. The
later user instruction selected AWS Open Data GeoParquet and direct GeoParquet
output; see [D-035](2026-10-07-decision-obis-area-230-geoparquet.md). The
earlier API JSON pages and CSV were removed from local storage on 7 October
2026. No occurrence payload is currently retained, and the 23,934 count below
is historical rather than a current AWS subset count.

## Decision

Download every occurrence record returned by the OBIS occurrence API for
`areaid=230`, across all taxa. Include records marked as absences and records
marked as dropped. Do not apply a taxon, date, depth, quality-flag, or overall
record-count filter. The original implementation exported the complete API
response set to CSV; this method and format were superseded by D-035.

The API request page size is pagination mechanics only; the previous collector
followed the OBIS cursor until it reached the API-reported total. It retained
the original JSON response pages unchanged, with a receipt recording request
parameters, retrieval time, row count and SHA-256 fingerprint for each page.
The CSV was an export of those responses, not a cleaned or curated dataset.

## Rationale and evidence

The user confirmed Area 230 as the finalised boundary for this collection
phase, and specified that this phase is for collecting all available data
before deciding which records to retain or remove. A live count request on
7 October 2026 using `areaid=230`, `absence=include`, `dropped=include` and
`qcfields=true` returned an API-reported total of 23,934 records. This is a
time-specific publisher count; the complete acquisition result and file
fingerprints are recorded in the [Area 230 source record](2026-10-07-source-obis-area-230-all-occurrences.md).

OBIS describes its Mapper CSV and full export as excluding absence records,
and says dropped records are available through the API or `robis`; the
occurrence API is therefore used to meet the full inclusion scope. See the
[OBIS data-access manual](https://manual.obis.org/access),
[OBIS data-quality manual](https://manual.obis.org/data_qc.html), and
[occurrence API](https://api.obis.org/#/Occurrence/get_occurrence).

## Boundary and interpretation

Area 230 is the OBIS-defined “Sri Lanka” area used to select records for this
collection. This decision does not establish that the publisher area is the
Sri Lankan EEZ polygon, nor does it decide which records are suitable for a
later modelling population. The historical API download retained quality
flags and other available fields for later review; the D-035 AWS output is
planned to retain its complete source fields. No missing occurrence is
converted to an absence, and no presence-probability claim follows from this
acquisition.

The acquired source may contain records with varied contributing-dataset
licences, quality states, taxonomic ranks and spatial/temporal precision.
Review the actual source metadata and ecological sensitivity before reuse or
redistribution. Preserve the full intake unchanged until any subsequent
record-level decisions are documented.

## Consequences

- D-006 now treats Area 230 as the accepted OBIS collection scope while the
  modelling domain remains open.
- D-007 focal-species selection, target construction, filtering, cleaning,
  environmental integration and model decisions remain open.
- The current [collector](../../src/data_collection/obis_occurrences.py) uses
  the API for Area 230 membership IDs and reads full records from matching AWS
  Open Data GeoParquet source files; its preflight and export have not been run.
- The [historical source record](2026-10-07-source-obis-area-230-all-occurrences.md)
  preserves the API retrieval counts and fingerprints; the payloads are not
  currently retained.

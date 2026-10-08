# Reusable implementation

The project Python baseline is 3.14, recorded in the root
[`.python-version`](../.python-version). The current scripts remain compatible
with Python 3.10 or later. Third-party Python packages
used by code or notebooks belong in the root
[`requirements.txt`](../requirements.txt), with the selected exact version.
The current OBIS utilities use only the standard library. See the
[dependency policy](../CONTRIBUTING.md#python-dependencies) for the install
command (`python -m pip install -r requirements.txt`) and update rule. Update
the manifest and the relevant setup instructions in the same change whenever
a third-party package is added, removed or changed.
For Conda, create and activate the `OCEAVERA` environment by following the
[root setup instructions](../README.md#create-the-conda-environment) before
running these scripts; it uses the baseline Python 3.14.

**Current method:** the standard-library [`obis_occurrences.py`](data_collection/obis_occurrences.py)
downloads the complete paginated Area 230 response from the OBIS API. It
includes absence and dropped records, omits the `fields` parameter, applies no
taxon/date/depth/record filter, and saves each response body unchanged beneath
`data/raw/obis/json/` with a count/checksum manifest. Requests are sequential
and use the API's `after` cursor. A run is marked complete only when the API
total and unique record IDs agree. Interrupted or failed runs retain completed
pages and can be resumed with `--resume`.

From the repository root:

```text
python src/data_collection/obis_occurrences.py
```

The separate standard-library
[`obis_json_to_csv.py`](data_collection/obis_json_to_csv.py) converts only a
complete, checksum-verified JSON run. It writes the union of every top-level
field and every record to `data/raw/obis/csv/`, serialises nested arrays and
objects as compact JSON strings, and checks each CSV row against the raw JSON.
By default it uses the newest complete run; `--json-run` selects a specific
run directory. The CSV includes all top-level API fields plus the 68 named
columns on OBIS's Data Access page; missing documented keys are blank, and
`AphiaID` mirrors the API's `aphiaID` while preserving that original column.
`--replace-existing` refreshes output only when its receipt proves it comes
from the same JSON run. Neither script writes occurrence data to
`data/interim/` or deletes earlier runs. The exact raw responses remain the
lossless source for the CSV copy.

## OBIS raw-to-interim handoff

[`stage_obis_csv.py`](data_preparation/stage_obis_csv.py) accepts the selected
OBIS CSV path at the first raw-to-interim boundary. Run it from the repository
root:

```text
python src/data_preparation/stage_obis_csv.py --obis-csv data/raw/obis/csv/<selected-run>.csv
```

The path is supplied once at this boundary. The script checks CSV row widths,
copies every byte unchanged, verifies the checksum and writes to the fixed
`data/interim/obis/source_validation/occurrences.csv` path with a fixed
`manifest.json` alongside it. Re-running replaces that phase's output after
validation rather than creating another run folder. Interim payloads and the
local manifest are ignored by Git.

This is structural validation and staging, not scientific cleaning: it removes
no rows or fields and does not decide exclusions, taxonomic rules, missing
values or feature extraction. Later OBIS transformations use separate stable
phase folders under `data/interim/obis/`; each script reads the preceding
phase's fixed path and writes its own fixed path without timestamps. This
branch contains no Bio-ORACLE code; its phase-folder layout is documented for
future work only.

The API currently reports a live total during retrieval; the actual count,
page hashes, response-body bytes and CSV fingerprint are recorded in the
[Area 230 source record](../docs/records/2026-10-08-source-obis-area-230-api-csv.md).
The failed AWS/GeoParquet attempt remains historical under [D-035](../docs/records/2026-10-07-decision-obis-area-230-geoparquet.md);
[D-036](../docs/records/2026-10-08-decision-obis-area-230-api-csv.md) selects
the current API/CSV method. The workflow does not clean, deduplicate, select
species, integrate environmental data, construct targets or model observations.

Place future preparation, spatial integration, modelling or evaluation logic
here only as those stages are authorised. Keep notebooks focused on
explanation and analysis rather than duplicated implementation.

## Member responsibilities

Reusable logic follows the working biological/target/baseline ownership of
Sanuda, environmental/integration ownership of Ushan, preprocessing/intermediate-model
ownership of Adithya and training/validation/evaluation ownership of Wanshaja.
Feature work and candidate training retain the joint ownership in the
canonical matrix. See the [complete responsibility plan](../docs/project/member-responsibilities.md)
for all activities, shared roles and handovers. Planned ownership does not
establish an artefact or completed contribution.

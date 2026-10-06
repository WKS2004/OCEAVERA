# Data storage and provenance

These are conventions for future data work. No data have been acquired in this repository, and no publisher terms or resource compatibility have been verified.

## Storage and lifecycle

| Location | Content | Handling |
| --- | --- | --- |
| `data/raw/` | Original source downloads | Preserve unchanged and associate with a source manifest |
| `data/interim/` | Intermediate transformations/extractions | Regenerate from recorded inputs and processing steps |
| `data/processed/` | Reviewed analysis-ready tables | Document schema, row meaning, target, exclusions and dataset version |
| `docs/records/` | Manifests, dictionaries and processing evidence | Follow [record conventions](../../CONTRIBUTING.md#project-evidence-records); track without credentials or sensitive payloads |
| [outputs/](../../outputs/README.md) | Generated figures, maps and evaluation outputs | Track reviewed shareable artefacts deliberately; retain generating references |

Data payloads are excluded from Git by default. The three data directories retain only their structural markers until acquisition is authorised. Keep metadata outside ignored payload directories. Inspect `git status` and ignore behaviour before sharing; an ignore rule does not remove an already tracked file.

Redistribution and versioning require a documented review of terms, size, privacy and ecological sensitivity. For a final dataset deliverable, provide the approved dataset or permissible retrieval instructions with a stable source identifier and fingerprint. The storage convention does not waive the assessment's dataset requirement.

## Acquisition provenance

Copy the [source manifest](../templates/data-source-record.md) for each actual resource. Record publisher, stable URL/DOI/accession, exact release/layer, retrieval date, query and filters, file format, source citation, licence/terms, coverage, and checksum algorithm/value where practical. Record file paths relative to the repository.

Use descriptive resource IDs and version identifiers consistently in manifests, dictionaries, notebooks and outputs. Retain the original resource identity when renaming a local file. A resource can change without changing its URL; record both retrieval details and a content fingerprint.

When an integrated dataset is created, complete a [machine-readable manifest](../templates/dataset-manifest.json) linking its source records, dictionary, processing artefact, configuration, counts and fingerprint. This complements the narrative source records; blank template fields establish no acquisition evidence.

OBIS occurrences and Bio-ORACLE layers are proposed core inputs; OBIStherm is only a possible supporting resource. Use current authoritative publisher documentation when actual acquisition begins.

## Integration and quality

Before recommending a species, region or layer, measure coverage and record quality from retrieved data. Check taxonomic identity, coordinate validity, coordinate system/order, observation dates, duplicate or repeated records, depth context and sampling concentration.

For each layer, record units, resolution, coordinate system, marine mask, no-data conventions, depth stratum, and temporal period/statistic. Specify the extraction/join method, grid alignment, coastal-cell handling and rules for unmatched points. Historical climatologies are not contemporaneous measurements; disclose any temporal approximation.

For every material filter or join, record inputs/versions, row counts before and after, exclusions and reasons, and the generating artefact. Distinguish legitimate repeated observations from duplicates. Update the [dictionary](../templates/data-dictionary.md) whenever field meaning or transformations change.

## Target and interpretation

Keep observed biological presences separate from constructed background/pseudo-absence labels. Missing occurrences are not confirmed absences. Preserve sample origin, sampling-domain and split information so the target and evaluation can be audited.

Document learned transformations and fit them within training partitions. Deterministic extraction of independently published environmental covariates can precede splitting; target-guided choices and learned transformations must respect the evaluation boundary.

## Responsible sharing

Check publisher terms and attribution requirements before reuse or redistribution. Review fine-resolution species locations for ecological sensitivity before publishing maps or coordinates. Keep credentials, tokens and unrelated personal data out of project files. Record relevant permissions or anonymisation measures without exposing sensitive details.

## Responsibility and data handover

Follow the [complete member plan](../project/member-responsibilities.md): Sanuda owns biological preparation/target inputs, Ushan environmental preparation/spatial integration and Adithya integrated cleaning/preprocessing. Wanshaja reviews source preparation and leads evaluation with group participation. Each producing member supplies provenance, field definitions, row counts, exclusions, versions and generating references; combine biological and environmental definitions in the integrated dictionary/manifest. All four decide species/domain, sampling and final features from that evidence. The allocation does not establish acquisition or authorise payload redistribution.

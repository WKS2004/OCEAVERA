# Evidence templates

Copy a form into `docs/records/`, following the [record conventions](../../CONTRIBUTING.md#project-evidence-records) when its underlying work is authorised. Leave these originals blank. Use an explicit pending or not-applicable status with a reason when a field cannot be completed; do not substitute invented evidence.

| Form | Purpose |
| --- | --- |
| [Problem framing](problem-framing-canvas.md) | Stakeholder/context, decision, lens, task, success and approval |
| [Decision record](decision-record.md) | Alternatives, evidence, rationale and consequences |
| [Source manifest](data-source-record.md) | Resource identity, access details, terms and fingerprint |
| [Data dictionary](data-dictionary.md) | Dataset version, row meaning and field-level semantics |
| [EDA log](eda-insight-log.md) | Observed findings and their decision implications |
| [Preprocessing and features](preprocessing-and-feature-decisions.md) | Evidence for cleaning, transformations and features |
| [Evaluation design](validation-and-evaluation-plan.md) | Target, sampling, partitions, metrics and leakage controls |
| [Model comparison](model-comparison.md) | Baseline and alternative results under a documented design |
| [Recommendation](recommendations-and-limitations.md) | Evidence-based practical value, uncertainty and limitations |
| [Dataset manifest](dataset-manifest.json) | Machine-readable dataset identity, source records, actual storage format, processing and fingerprint |
| [Model metadata](model-metadata.json) | Machine-readable model/run identity, artefact format, environment, evaluation, limits and acceptance |

AI-assisted activity uses the separate [contribution recording template](../project/ai-usage-log-template.md) and [per-contributor logs](../README.md#contribution-records).

A form establishes a recording format. It becomes assessment evidence only when supported by the corresponding data, analysis, decision or approval record.

The JSON forms deliberately contain nulls and empty collections. Copy and complete them from actual work; they are not acquired datasets, trained-model records or formal validation schemas. Use a code revision only when it identifies the generating work accurately; otherwise record the worktree state and relevant files/configuration without implying a commit exists.

## Responsibility for evidence

Use the [member plan's evidence mapping](../project/member-contributions/shared-responsibilities-and-evidence.md#requirement-and-evidence-coverage) for primary preparation and shared review of completed forms. Every member supplies evidence for their actual work, and all four retain responsibility for shared decisions, reproducibility and final submission. Keep these master forms blank; an assigned form or proposed owner is not a completed contribution.

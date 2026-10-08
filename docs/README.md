# Documentation index

## Authoritative documents

| Area | Document | Purpose |
| --- | --- | --- |
| Requirements | [PROJECT_REQUIREMENTS.md](../PROJECT_REQUIREMENTS.md) | Project obligations, deliverables, rubric and acceptance evidence |
| Python dependencies | [requirements.txt](../requirements.txt) | Shared third-party Python package inventory; currently no packages are required. Update it and setup guidance together under the [contributor policy](../CONTRIBUTING.md#python-dependencies) |
| Python environment | [`.python-version`](../.python-version); [root setup instructions](../README.md#create-the-conda-environment) | Project baseline is Python 3.14; CI reads the same version file. The ML framework and scientific dependency stack remain open |
| Project | [Overview and scope](project/project-overview-and-scope.md) | Identity, proposal commitments, scope and interpretation limits |
| Project | [Decision register](project/decision-register.md) | Planning positions, repository conventions and unresolved choices |
| Project | [Readiness and alignment](project/repository-readiness-and-alignment.md) | Current phase, evidence gaps and readiness |
| Project | [GitHub workflows](project/github-workflows.md) | Current CI, local checks, failure handling and prerequisites for scientific automation |
| Project | [Member responsibilities](project/member-responsibilities.md) | General division, pipeline matrix and navigation to detailed member duties |
| Project | [Shared responsibilities and evidence](project/member-contributions/shared-responsibilities-and-evidence.md) | Common participation, decisions, requirements, handovers and final submissions |
| Project | [Contributor identities](project/ai-team-members.md) | Exact account-to-name mapping for records |
| Project | [AI-usage recording template](project/ai-usage-log-template.md) | Ten required fields and attribution discipline |
| Project | [Repository review history](project/repository-review-history.md) | Preserved earlier unattributed maintenance reviews |
| Data | [Storage and provenance](data/data-storage-and-provenance.md) | Source-preserving formats, derived tables, model artefacts, integration boundaries and sharing |
| ML | [Workflow and evidence gates](ml/ml-workflow-and-evidence-gates.md) | Analytical sequence and shared progression |
| Blank forms | [Evidence templates](templates/README.md) | Reusable scientific and assessment forms |
| Contributor guidance | [CONTRIBUTING.md](../CONTRIBUTING.md) | Change workflow, evidence and activity recording, review |
| Rights | [LICENSE.md](../LICENSE.md) | All-rights-reserved policy and third-party boundaries |

Requirements state obligations, the overview sets boundaries, the member plan records proposed ownership, the register tracks choices and readiness records what exists. Update affected documents together when a material change crosses these responsibilities.

## Detailed member duties

| Member | Detailed responsibility file |
| --- | --- |
| Sanuda Abeysinghe | [Biological data, targets and baseline](project/member-contributions/sanuda-abeysinghe.md) |
| Ushan Srinuka | [Environmental data, integration and features](project/member-contributions/ushan-srinuka.md) |
| Adithya Gunawardana | [EDA, preprocessing and intermediate models](project/member-contributions/adithya-gunawardana.md) |
| Wanshaja Sooriyabandara | [Training, validation, evaluation and interpretation](project/member-contributions/wanshaja-sooriyabandara.md) |

The member files describe planned technical duties, including every proposal activity and personal evidence/handover expectations. All members must also follow the common guide. These are responsibility documents, separate from factual activity logs.

## Scientific evidence records

Store dated scientific, approval and detailed decision evidence in `docs/records/`, following [record conventions](../CONTRIBUTING.md#project-evidence-records). Copy the relevant blank form when authorised work produces actual evidence, then link observations, resource versions and generating artefacts from decisions or requirements.

Initial OBIS feasibility is recorded in the [Sri Lanka candidate assessment](records/2026-10-07-obis-sri-lanka-biological-feasibility.md), with two linked records for bounded samples whose local payloads were later removed at the user's request. The user finalised Area 230 as the complete OBIS collection scope under [D-034](records/2026-10-07-decision-obis-area-230.md). A historical 23,934-record API retrieval and its JSON/CSV fingerprints remain in the [previous source record](records/2026-10-07-source-obis-area-230-all-occurrences.md), but those payloads were subsequently removed. The [D-035 AWS/GeoParquet method](records/2026-10-07-decision-obis-area-230-geoparquet.md) and its [failed export outcome](records/2026-10-08-obis-area-230-export-attempt.md) remain historical. Under current [D-036](records/2026-10-08-decision-obis-area-230-api-csv.md), all Area 230 API JSON pages are preserved under `data/raw/obis/json/` and a verified CSV is placed under `data/raw/obis/csv/`; actual counts, page hashes and output fingerprints are in the [current source record](records/2026-10-08-source-obis-area-230-api-csv.md). [D-037](records/2026-10-08-decision-stable-derived-data-paths.md) is the historical first path decision. Current [D-038](records/2026-10-08-decision-phase-specific-derived-data-paths.md) defines stable source/phase folders: the OBIS raw-to-interim utility accepts a selected raw CSV path once, then writes unchanged bytes to a fixed source-validation path. This is structural validation and staging only, not scientific cleaning or integration. Bio-ORACLE's corresponding layout is documented; its code is not implemented in this branch. These records do not establish a selected focal species, modelling population, integrated dataset, approval, stakeholder engagement, EDA, feature engineering or modelling result. Directory markers alone are not evidence of completed work.

## Contribution records

Use the exact [contributor identities](project/ai-team-members.md) and [recording template](project/ai-usage-log-template.md). Keep meaningful AI-assisted tasks as chronological entries in the acting contributor's file under `docs/ai-contribution/`.

| Contributor | Current activity log |
| --- | --- |
| Sanuda Abeysinghe (`sanudaabey`) | [Contribution and AI-usage record](ai-contribution/sanudaabey-ai-usage.md) |
| Wanshaja Sooriyabandara (`WKS2004`) | [Contribution and AI-usage record](ai-contribution/WKS2004-ai-usage.md) |

The [responsibility plan](project/member-responsibilities.md) documents expected technical work separately from the activity logs. Only contributors with recorded activity have logs. The absence of a log does not establish that a member has performed no work. Keep human review status, unrun checks and unavailable metadata explicit.

Earlier shared maintenance notes remain in the [repository review history](project/repository-review-history.md). Their contributor identities were not recorded and have not been retrospectively assigned. Activity records support accountability; scientific artefacts establish their corresponding findings and each member remains responsible for their own assessed learning report.

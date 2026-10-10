# Documentation index

## Authoritative documents

| Area | Document | Purpose |
| --- | --- | --- |
| Requirements | [PROJECT_REQUIREMENTS.md](../PROJECT_REQUIREMENTS.md) | Project obligations, deliverables, rubric and acceptance evidence |
| Python dependencies | [requirements.txt](../requirements.txt) | Shared, exactly pinned package inventory; currently includes Jupyter Notebook and its Python kernel. Update it and setup guidance together under the [contributor policy](../CONTRIBUTING.md#python-dependencies) |
| Python environment | [`.python-version`](../.python-version); [root setup instructions](../README.md#create-the-conda-environment) | Project baseline is Python 3.14; CI reads the same version file. No environment is stored in the repository; setup and package operations by agents require explicit user authorisation under the [contributor policy](../CONTRIBUTING.md#python-dependencies) |
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

Initial OBIS feasibility is recorded in the [Sri Lanka candidate assessment](records/2026-10-07-obis-sri-lanka-biological-feasibility.md), with two linked records for bounded samples whose local payloads were later removed at the user's request. The user finalised Area 230 as the complete OBIS collection scope under [D-034](records/2026-10-07-decision-obis-area-230.md). A historical 23,934-record API retrieval and its JSON/CSV fingerprints remain in the [previous source record](records/2026-10-07-source-obis-area-230-all-occurrences.md), but those payloads were subsequently removed. The [D-035 AWS/GeoParquet method](records/2026-10-07-decision-obis-area-230-geoparquet.md) and its [failed export outcome](records/2026-10-08-obis-area-230-export-attempt.md) remain historical. Under current [D-036](records/2026-10-08-decision-obis-area-230-api-csv.md), all Area 230 API JSON pages are preserved under `data/raw/obis/json/` and a verified CSV is placed under `data/raw/obis/csv/`; actual counts, page hashes and output fingerprints are in the [current source record](records/2026-10-08-source-obis-area-230-api-csv.md). [D-037](records/2026-10-08-decision-stable-derived-data-paths.md) is the historical first path decision. Current [D-038](records/2026-10-08-decision-phase-specific-derived-data-paths.md) defines stable source/phase folders: the OBIS raw-to-interim utility accepts a selected raw CSV path once, then writes unchanged bytes to a fixed source-validation path. This is structural validation and staging only, not scientific cleaning or integration. [D-046](records/2026-10-08-decision-bio-oracle-environmental-intake.md) records the initial bounded Bio-ORACLE test; its NetCDF payload and local manifest were deleted at the user's request, with historical measurements kept in the [source record](records/2026-10-09-source-bio-oracle-oceantemperature.md). [D-047](records/2026-10-09-decision-bio-oracle-catalog-intake.md) expands intake to all regional Bio-ORACLE v3 grids and variables; [D-048](records/2026-10-09-decision-bio-oracle-sri-lanka-bbox.md) defines the EEZ-extrema rectangle. The first catalogue run completed all 356 grids and 2,392 variables (4,017,532,960 bytes), then its raw files were deleted at the user's request; a subsequent partial manual snapshot was also deleted. The latest Python-file run completed all 356 grids and 2,392 variables and passed the complete transfer-integrity and request-scope audit. The [regional source record](records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md) holds all run histories and final evidence. These records do not establish a selected focal species, modelling population, integrated dataset, approval, stakeholder engagement, EDA, feature engineering or modelling result. Directory markers alone are not evidence of completed work.

## Branch work notebooks

At branch finalisation, record the branch's actual implementation and evidence in a notebook under ../notebooks/branch_work/, following the notebook convention and D-042/D-045. Use native Markdown cells for the title, contributor table, purpose, scope and data context before concise executable Python Code cells. Execute Code cells in order and retain concise outputs. The default is offline; saved input is read-only, and notebook data stays in memory without dataset files being written. Each notebook uses a contributor table with registration number, member name and GitHub account; a registration number is permitted only in that table. The [biological data collection branch notebook](../notebooks/branch_work/pipeline_biological_data_collection.ipynb) documents the OBIS Area 230 intake and handoff. The [environmental data collection branch notebook](../notebooks/branch_work/pipeline_environmental_data_collection.ipynb) documents the Bio-ORACLE catalogue intake, selected rectangle, run evidence and offline integrity checks. Branch notebooks are implementation overviews; they do not replace factual contributor logs, scientific records or individual assessed reflections.

## Contribution records

Use the exact [contributor identities](project/ai-team-members.md) and [recording template](project/ai-usage-log-template.md). Keep meaningful AI-assisted tasks as chronological entries in the acting contributor's file under `docs/ai-contribution/`.

| Contributor | Current activity log |
| --- | --- |
| Sanuda Abeysinghe (`sanudaabey`) | [Contribution and AI-usage record](ai-contribution/sanudaabey-ai-usage.md) |
| Ushan Srinuka (`Ushan-Srinuka`) | [Contribution and AI-usage record](ai-contribution/Ushan-Srinuka-ai-usage.md) |
| Wanshaja Sooriyabandara (`WKS2004`) | [Contribution and AI-usage record](ai-contribution/WKS2004-ai-usage.md) |

The [responsibility plan](project/member-responsibilities.md) documents expected technical work separately from the activity logs. Only contributors with recorded activity have logs. The absence of a log does not establish that a member has performed no work. Keep human review status, unrun checks and unavailable metadata explicit.

Earlier shared maintenance notes remain in the [repository review history](project/repository-review-history.md). Their contributor identities were not recorded and have not been retrospectively assigned. Activity records support accountability; scientific artefacts establish their corresponding findings and each member remains responsible for their own assessed learning report.

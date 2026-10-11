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

Initial OBIS feasibility is recorded in the [Sri Lanka candidate assessment](records/2026-10-07-obis-sri-lanka-biological-feasibility.md), with linked records for bounded samples whose payloads were later removed at the user's request. The user finalised Area 230 as the complete OBIS collection scope under [D-034](records/2026-10-07-decision-obis-area-230.md). Under current [D-036](records/2026-10-08-decision-obis-area-230-api-csv.md), API JSON pages are preserved under `data/raw/obis/json/` and a verified CSV under `data/raw/obis/csv/`; counts and fingerprints are in the [current source record](records/2026-10-08-source-obis-area-230-api-csv.md). The earlier AWS/GeoParquet attempt and path conventions remain historical.

[D-038](records/2026-10-08-decision-phase-specific-derived-data-paths.md) records the former practice of retaining separate phase outputs under interim. It is superseded for interim dataset retention by [D-049](records/2026-10-11-decision-interim-one-current-dataset.md): keep one current dataset per family. Where stages use directories, keep exactly one active stage directory directly beneath each family path and replace it only after successful validation; a single-table family may use its fixed file destination. Regenerate earlier states from raw sources and scripts. OBIS now has only `data/interim/obis/cleaning/`, which contains its source-validation manifest, cleaned CSV and JSON reports. Bio-ORACLE currently has only its `source_validation/` directory; a later validated cleaning stage must replace it with `cleaning/`, not add a sibling. A single integrated interim table is planned but does not exist.

[D-046](records/2026-10-08-decision-bio-oracle-environmental-intake.md) records the initial bounded Bio-ORACLE test, whose payload was deleted at the user's request. [D-047](records/2026-10-09-decision-bio-oracle-catalog-intake.md) expands intake to all regional v3 grids and variables; [D-048](records/2026-10-09-decision-bio-oracle-sri-lanka-bbox.md) defines the EEZ-extrema rectangle. The latest run completed all 356 grids and 2,392 variables and passed the transfer-integrity and request-scope audit. The [regional source record](records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md) preserves run history and evidence.

The superseded 10 October 90% screen and EDA findings are in the [column-screening record](records/2026-10-10-obis-area-230-column-screening.md) and [EDA record](records/2026-10-10-obis-area-230-eda.md). The earlier row-filter result remains in the [historical cleaning record](records/2026-10-10-obis-area-230-cleaning.md). The current 10% protected-column and conservative row-cleaning result is 23,371 rows × 112 columns; see the [11 October cleaning record](records/2026-10-11-obis-area-230-cleaning.md). These records do not select a focal species or modelling population, approve integration, or establish feature-engineering or modelling results.

## Branch work notebooks

At branch finalisation, record the branch's actual implementation and evidence in a notebook under ../notebooks/branch_work/, following the notebook convention and D-042/D-045. Use native Markdown cells for the title, contributor table, purpose, scope and data context before concise executable Python Code cells. Execute Code cells in order and retain concise outputs. The default is offline; saved input is read-only, and notebook data stays in memory without dataset files being written. Each notebook uses a contributor table with registration number, member name and GitHub account; a registration number is permitted only in that table. The [biological data collection branch notebook](../notebooks/branch_work/01_pipeline_biological_data_collection.ipynb) documents the OBIS Area 230 intake and handoff. The [environmental data collection branch notebook](../notebooks/branch_work/02_pipeline_environmental_data_collection.ipynb) documents the Bio-ORACLE catalogue intake, selected rectangle, run evidence and offline integrity checks. The [OBIS cleaning branch notebook](../notebooks/branch_work/03_pipeline_data_cleaning_obis.ipynb) explains the cleaning purpose, concrete column and row rules, branch output counts, preserved quality data and read-only verification. Branch notebooks are implementation overviews; they do not replace factual contributor logs, scientific records or individual assessed reflections.

## Contribution records

Use the exact [contributor identities](project/ai-team-members.md) and [recording template](project/ai-usage-log-template.md). Keep meaningful AI-assisted tasks as chronological entries in the acting contributor's file under `docs/ai-contribution/`.

| Contributor | Current activity log |
| --- | --- |
| Sanuda Abeysinghe (`sanudaabey`) | [Contribution and AI-usage record](ai-contribution/sanudaabey-ai-usage.md) |
| Ushan Srinuka (`Ushan-Srinuka`) | [Contribution and AI-usage record](ai-contribution/Ushan-Srinuka-ai-usage.md) |
| Wanshaja Sooriyabandara (`WKS2004`) | [Contribution and AI-usage record](ai-contribution/WKS2004-ai-usage.md) |

The [responsibility plan](project/member-responsibilities.md) documents expected technical work separately from the activity logs. Only contributors with recorded activity have logs. The absence of a log does not establish that a member has performed no work. Keep human review status, unrun checks and unavailable metadata explicit.

Earlier shared maintenance notes remain in the [repository review history](project/repository-review-history.md). Their contributor identities were not recorded and have not been retrospectively assigned. Activity records support accountability; scientific artefacts establish their corresponding findings and each member remains responsible for their own assessed learning report.

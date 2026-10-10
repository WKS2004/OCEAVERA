# Project requirements

This is the canonical requirements and assessment reference for **OCEAVERA — Marine Habitat Intelligence**, IT3091 Machine Learning, group 2026-AI-45. It consolidates the shared proposal commitments, scientific safeguards, evidence requirements and submission obligations. Requirements describe expected work; the [readiness review](docs/project/repository-readiness-and-alignment.md) records what has been established.

## Requirement basis and change control

The [overview and scope](docs/project/project-overview-and-scope.md) preserves the working baseline from the initial group submission dated 17 September 2026. The [member responsibility plan](docs/project/member-responsibilities.md) preserves the initial allocation in Sections 6.1–6.7, including both pipeline tables. The assessment obligations below are the maintained project transcription. An initial proposal or group declaration does not establish Industry Explorer approval, stakeholder engagement or technical feasibility.

Use **must** for an obligation or accepted project safeguard, **should** for a practice that needs a recorded reason if omitted, and **may** for an optional extension. Keep final species, geography, source resources, targets, features, methods, metrics and environment choices in the [decision register](docs/project/decision-register.md), with supporting evidence. Record a material requirement change there and update affected scope, workflow and readiness documents together.

## Scope and intended output

The project must investigate a bounded marine species-distribution and habitat-suitability problem. Marine Resilience is the primary decision lens; Coastal Tourism supplies a supporting application context. A defined stakeholder or decision context must explain the practical value and limits of the intended output.

The initial direction is one focal species, with a small number permitted only when data and manageable scope justify it. Sri Lanka-focused or regionally constrained marine geography remains a preference for the modelling domain. Under [D-034](docs/records/2026-10-07-decision-obis-area-230.md), OBIS Area 230 is finalised as the complete biological collection scope; it is not asserted to equal the Sri Lankan EEZ polygon or the final modelling domain. Under current [D-036](docs/records/2026-10-08-decision-obis-area-230-api-csv.md), all Area 230 API responses are retained as JSON and converted to CSV; the [dated source record](docs/records/2026-10-08-source-obis-area-230-api-csv.md) documents the API count, page hashes and output checks. The superseded [D-035 AWS GeoParquet method](docs/records/2026-10-07-decision-obis-area-230-geoparquet.md) and its failed attempt remain historical. OBIS and Bio-ORACLE are candidate core sources; OBIStherm may support the task if justified. Under [D-047](docs/records/2026-10-09-decision-bio-oracle-catalog-intake.md) and [D-048](docs/records/2026-10-09-decision-bio-oracle-sri-lanka-bbox.md), Bio-ORACLE source intake uses the rectangular envelope of the Marine Regions Sri Lankan EEZ extent for all regional v3 layers and variables. The first catalogue retrieval and a later partial manual snapshot were deleted at the user's request. The latest Python collector run completed all 356 regional grids and 2,392 variables; the tracked [source record](docs/records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md) preserves run history and transfer-integrity evidence. Retrieved metadata exposed baseline coordinates at 2000/2010 and SSP coordinates at 2020–2090, with no 2100 coordinate. The collection rectangle is not the EEZ polygon or the final modelling domain; source coverage, layer compatibility and focal-species suitability remain subject to review. Future SSP layers are projections, but future-climate species modelling remains outside the current assignment scope.

Bio-ORACLE does not provide per-year values. At catalogue level it defines the present-day product as 2000–2020 and offers separate decades 2000–2010 and 2010–2020. The retrieved baseline metadata labels coordinates 2000 and 2010, but the ERDDAP metadata does not specify the exact averaging window for each value; individual product titles end in 2018, 2019 or 2020. Consequently, coverage through 2020 is not confirmed for every specific baseline layer. SSP labels run from 2020 through 2090, with the final decade reaching the 2100 horizon rather than a separate 2100 timestamp. See the [regional source record](docs/records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md).

The core scope covers acquisition, integration, target construction, EDA, preprocessing/features, a baseline and alternatives, validation, interpretation and reproducible reporting. A suitability map may be produced where supported by the data. Real-time prediction, future-climate projection, operational deployment, a full BLUEVERSE platform and additional unrelated models are outside the current assignment scope.

## Scientific and technical requirements

| ID | Requirement | Evidence of fulfilment |
| --- | --- | --- |
| R-01 | Define the stakeholder/context, decision need, exact research question, unit, intended output and success criteria before claiming practical value. | Completed [framing record](docs/templates/problem-framing-canvas.md), including approval status and limits |
| R-02 | Select the focal species and marine study domain from documented quantity, quality, geographic/temporal coverage and ecological relevance. | Feasibility observations and recorded species/boundary decisions |
| R-03 | Preserve original inputs unchanged in their publisher-delivered format and record exact occurrence resources, contributing datasets, environmental layers, versions, access dates, queries, citations, terms and fingerprints. Use GeoParquet for compatible derived spatial tables and Parquet for compatible non-spatial ML tables; retain full environmental arrays in their source format rather than flattening complete rasters. Select a raw source path only at its first handoff; put each interim transformation in its own stable, timestamp-free source-phase folder and use fixed paths thereafter. Record and justify any format exception. | Completed [source records](docs/templates/data-source-record.md), [dataset manifest](docs/templates/dataset-manifest.json) and processing evidence; follow [storage conventions](docs/data/data-storage-and-provenance.md) and [D-038](docs/records/2026-10-08-decision-phase-specific-derived-data-paths.md) |
| R-04 | Establish row meaning, field types/units and coordinate, temporal, depth and grid-cell compatibility. Document missingness, duplicates, taxonomic/coordinate quality, observation bias and exclusions with counts. | Completed [dictionary](docs/templates/data-dictionary.md), quality records and [EDA log](docs/templates/eda-insight-log.md) |
| R-05 | Distinguish observed presence, confirmed absence where actually available, background and pseudo-absence. Justify the accessible sampling domain, comparison design, seed/counts and observation limitations. | Target/sampling decisions and completed [evaluation design](docs/templates/validation-and-evaluation-plan.md) |
| R-06 | Define validation for the intended generalisation question. Assess spatial dependence, shared environmental cells and relevant temporal leakage; justify partitions and keep evaluation data isolated from design/tuning. | Split membership/configuration, leakage review and metric rationale |
| R-07 | Justify cleaning, preprocessing, imbalance handling and features. Fit learned transformations within training partitions; preserve reproducible treatment of missing values and out-of-domain inputs. | Completed [preprocessing and feature log](docs/templates/preprocessing-and-feature-decisions.md) and generating pipeline |
| R-08 | Compare a sensible baseline with at least three justified alternatives under a consistent protocol. Candidate algorithms are not a final model selection. | Completed [comparison record](docs/templates/model-comparison.md), parameters and comparable runs |
| R-09 | Use suitable metrics and critical evaluation beyond accuracy. Record threshold choices, fold variability and uncertainty where relevant; do not repeatedly tune against final held-out results. | Evaluation outputs and recorded selection rationale |
| R-10 | Describe presence/background outputs as relative suitability unless sampling and observation evidence support ecological occurrence probabilities. Calibration against constructed labels alone is insufficient; predictive associations do not establish causation. | Score definition, interpretation limits and calibration evidence when relevant |
| R-11 | Make an evidence-based recommendation with practical value, geographic/environmental domain, uncertainty, limitations and unsupported uses. | Completed [recommendation record](docs/templates/recommendations-and-limitations.md) linked to results |
| R-12 | Provide an agreed, versioned environment, documented execution order/configuration/seeds and data/model fingerprints. Record actual dataset and model-artefact formats and relevant format or serialization versions. Use fixed, timestamp-free paths for derived data; each phase reads its declared upstream path and writes to its own phase folder. Ensure notebook, code, metrics, figures and report agree. | Reproducible execution evidence and completed [model metadata](docs/templates/model-metadata.json) for actual trained artefacts; follow [D-038](docs/records/2026-10-08-decision-phase-specific-derived-data-paths.md) |
| R-13 | Declare actual AI assistance and human verification accurately. Record activity under verified contributor identities and preserve responsibility for individual learning submissions. | Completed [AI-usage entries](docs/README.md#contribution-records) using the [recording template](docs/project/ai-usage-log-template.md) |

The [ML workflow](docs/ml/ml-workflow-and-evidence-gates.md) defines progression gates. Python 3.14 is the project baseline under [D-039](docs/records/2026-10-08-decision-python-3-14-baseline.md), recorded in [`.python-version`](.python-version) and used for repository CI. Current OBIS and Bio-ORACLE intake scripts use the standard library and remain compatible with Python 3.10 or later. Jupyter Notebook and its Python kernel are pinned in the root [requirements.txt](requirements.txt) as notebook tooling; this does not select the ML framework or scientific package stack, model, numerical success threshold or deadline. D-046 records the initial single-layer feasibility query; D-047 and D-048 define the catalog-wide v3 intake and its EEZ-extrema collection rectangle. The rectangle does not apply an EEZ polygon mask or decide the modelling domain. The first complete and subsequent partial Bio-ORACLE snapshots were deleted at the user's request; the latest run now has all 356 layers and 2,392 variables downloaded and integrity-checked. See the [dated source record](docs/records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md) for run IDs and audit details. The root requirements file is the shared inventory for third-party Python packages and must be updated with exact version pins whenever a package is added, removed or changed. No Python environment is stored in the repository. Setup instructions are user-led; agents require explicit prior user authorisation before creating, modifying or removing an environment or installing, upgrading or removing packages. The ML environment remains subject to evidence that the selected libraries support the project baseline.

## Member responsibility coverage

Use the [overview](docs/project/member-responsibilities.md) for the division and fifteen-row matrix, and its linked member files for identities and complete activities. Its [requirement mapping](docs/project/member-contributions/shared-responsibilities-and-evidence.md#requirement-and-evidence-coverage) covers R-01–R-13, all seven evidence types, Industry Explorer conditions and final deliverables. The working contribution plan is finalised on 6 October 2026; subsequent responsibility changes require a recorded decision. Primary ownership supports shared technical participation; no member is allocated only documentation or presentation. Record completed work and review from actual evidence, and preserve each member's responsibility for their own one-A4 learning report.

## Required evidence package

Maintain all seven core evidence types: **problem-framing canvas, workflow diagram, decision log, EDA insights, preprocessing/feature decisions, model/method comparison, and recommendation with limitations**. Use [blank forms](docs/templates/README.md) for actual authorised work and follow the [record conventions](CONTRIBUTING.md#project-evidence-records).

Every completion claim must link the corresponding dated record or generating artefact. Forms, directory markers, proposed decisions and activity logs alone do not establish scientific findings or fulfilled deliverables.

## Repository requirements

- Keep canonical knowledge in maintained documents and conditional workflows in `.agents/skills/`; use [AGENTS.md](AGENTS.md) for universal agent instructions.
- Preserve existing work, professional British English, descriptive names, valid internal links and consistent UTF-8/LF formatting.
- Keep data payloads out of Git by default; preserve tracked provenance metadata without credentials or sensitive details.
- Record factual activity using the exact [contributor mapping](docs/project/ai-team-members.md). Do not fabricate allocation, contribution, approval or acceptance claims.
- Protect [member privacy](CONTRIBUTING.md#member-privacy): exclude member-specific academic identity fields and individual academic/assessment records from public documentation, logs and artefacts. Keep individual submission content within the authorised private submission process.
- Follow [LICENSE.md](LICENSE.md): all rights reserved, with original project ownership retained by the group contributors and third-party terms preserved. Academic affiliation grants no institutional ownership. A source being publicly accessible does not itself establish permission to redistribute it.
- Document actual checks and their limits. Structural checks do not replace scientific evaluation, human review or assessment evidence.

## Submission requirements

| Stage | Required content | Repository support and remaining work |
| --- | --- | --- |
| Initial group | Track; primary and optional secondary lenses with reasons; proposed task/output; workflow; core responsibility of each member | [Overview and scope](docs/project/project-overview-and-scope.md), [workflow](docs/ml/ml-workflow-and-evidence-gates.md), and [decision register](docs/project/decision-register.md) preserve shared direction. The [overview and linked detailed files](docs/project/member-responsibilities.md) preserve all four proposed ownership areas, every activity, shared duties and both pipeline tables at the user's request. Allocation remains revisable and is not completed contribution evidence. |
| Final group | Three-minute YouTube demo; final report with notebook/code; dataset and data dictionary; decision logs; model/method comparison | [Reports](reports/README.md), [notebooks](notebooks/README.md), [code](src/README.md), [data](data/README.md), and [record conventions](CONTRIBUTING.md#project-evidence-records) define destinations. Deliverables are pending. |
| Final individual | One A4 Personal Learning Journey report supporting individual contribution assessment | Required at final submission. Individual learning reports remain pending. [Contributor activity logs](docs/README.md#contribution-records) record factual AI-assisted repository work and do not replace those reports. |

The initial proposal's declaration describes an agreed group working scope. This is insufficient evidence of the prior approval required for Industry Explorer; retain approval details before claiming that condition is satisfied.

## Core rubric and traceability

| Criterion | Marks | Required evidence | Planning support | Current evidence status |
| --- | ---: | --- | --- | --- |
| Business framing and lens/task formulation | 5 | Stakeholder/context, decision need, lenses, unit, exact task/output, rationale | [Overview and scope](docs/project/project-overview-and-scope.md); [framing form](docs/templates/problem-framing-canvas.md) | Partial: task/lenses recorded; stakeholder and final unit unresolved |
| Workflow and decision log | 10 | Coherent diagram; material decisions with options, reasons, evidence | [Plan](docs/ml/ml-workflow-and-evidence-gates.md); [register](docs/project/decision-register.md); [decision form](docs/templates/decision-record.md) | Planning workflow present; implementation decisions pending |
| Data understanding, EDA, quality reasoning | 10 | Dictionary, row meaning/types, patterns/issues, implications | [Dictionary](docs/templates/data-dictionary.md); [EDA log](docs/templates/eda-insight-log.md) | The latest Bio-ORACLE intake has 356/356 layers verified. Integrated data, the dictionary and EDA findings remain pending; see the dated source record |
| Preprocessing and feature engineering | 15 | Justified handling of missingness, outliers, duplicates, categories, scaling, imbalance, leakage, relevant feature types | [Preprocessing log](docs/templates/preprocessing-and-feature-decisions.md) | Pending |
| Methods and comparison | 20 | Sensible baseline and at least three justified alternatives | [Comparison form](docs/templates/model-comparison.md) | Requirement recorded; no trained models |
| Evaluation, validation, critical judgement | 20 | Suitable metrics/splits, leakage controls, honest interpretation, comparison beyond accuracy | [Evaluation design](docs/templates/validation-and-evaluation-plan.md); [comparison](docs/templates/model-comparison.md) | Pending: final design and results unresolved |
| Recommendation, limitations, stakeholder value | 10 | Practical evidence-based recommendation, limits, risks, value | [Recommendation form](docs/templates/recommendations-and-limitations.md) | Pending |
| Reproducibility, documentation, AI transparency | 10 | Runnable notebook, report/output agreement, dataset link/fingerprint, truthful AI declaration | [Governance](docs/data/data-storage-and-provenance.md); [source manifest](docs/templates/data-source-record.md); [AI record](docs/project/ai-usage-log-template.md) | Documentation foundation present; execution evidence pending |
| **Total** | **100** | | | |

This map records coverage, not estimated marks. Blank templates do not satisfy the completed-evidence requirements.

## Industry Explorer requirements and bonus

Industry Explorer requires prior approval, a real-world problem, a suitable dataset, ethical handling, engagement, and practical value. It follows the same core rubric. Up to 10 bonus marks depend on approval and evidence review; finding an online dataset alone is insufficient.

| Bonus criterion | Marks | Evidence needed | Current status |
| --- | ---: | --- | --- |
| Real stakeholder or business context | 2 | Named stakeholder/context, decision need, realistic value | Marine domain stated; concrete decision context unresolved |
| Approved, feasible scope | 2 | Early approval; scope manageable within seven weeks | Approval not evidenced; scope bounded but feasibility unverified |
| Original, local, stakeholder-provided, or meaningfully real-world data | 2 | Verifiable source and fit to the decision lens | OBIS and Bio-ORACLE remain candidate core sources; the bounded Bio-ORACLE test and earlier regional snapshots were deleted at the user's request. The latest regional run has 356/356 layers verified; source fit remains open |
| Collection, dictionary, privacy handling | 2 | Acquisition method, dictionary, permission/anonymisation where relevant | OBIS acquisition is recorded; D-048 defines the Bio-ORACLE collection rectangle. The dated source record preserves prior deleted runs and the latest complete 356/356 transfer audit. The integrated dictionary and source-fit review remain pending |
| Practical recommendation | 2 | Evidence-based value for the stakeholder/context | Pending analysis and stakeholder framing |

The seven-week condition belongs to the bonus rubric. No project deadline, approval date, or completed engagement is inferred from it.

## Final handover checklist

- [ ] Problem-framing canvas, workflow, and decision evidence complete.
- [ ] Dataset identified with stable access details/fingerprint, acquisition steps, and dictionary; sharing terms respected.
- [ ] Source and derived dataset formats are recorded; spatial/non-spatial table choices and any exceptions are traceable. Model format is recorded only for an actual artefact; no optional BLUEVERSE integration format is treated as an OCEAVERA requirement.
- [ ] EDA and preprocessing/feature logs tied to actual data versions and decisions.
- [ ] Baseline plus at least three alternatives compared with a justified evaluation design.
- [ ] Recommendation and limitations supported by results and stakeholder context.
- [ ] Agreed environment and execution instructions recorded; notebook runs and report figures/metrics agree.
- [ ] AI assistance declared accurately; group review and verification recorded where performed.
- [ ] Final report, notebook/code, decision logs, comparison, and three-minute YouTube demo ready.
- [ ] Each member prepares the required individual one-A4 learning report.

All checklist items are pending at the current planning stage.

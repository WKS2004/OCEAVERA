# Repository readiness and alignment

- **Reviewed:** 8 October 2026
- **Phase:** finalised shared foundation and member contribution plan; Area 230 API JSON retrieval and CSV conversion under D-036 completed and recorded; D-038 phase-folder path convention and OBIS-only raw-CSV handoff implemented; Python 3.14 baseline accepted under D-039; no scientific cleaning or integration is complete; focal species, modelling population, ML stack and downstream analytical implementation remain open
- **Scope of review:** repository structure, documentation, agent guidance, repository automation, assessment requirements, initial proposal alignment, biological source feasibility/intake implementation, phase-specific data paths and branch closeout documentation.

## Assessment

The [branch work notebook](../../notebooks/branch_work/pipeline_biological_data_collection.ipynb) closes out the implementation at branch level. Under D-045, it uses native Markdown for the title, contributor table, scope and data context, followed by concise executable Python Code cells. Its ordered offline default reads the newest complete, manifest-verified local JSON run when available and uses a clearly labelled synthetic fixture otherwise. Saved files are read-only, and notebook-generated data are not written to disk. The notebook links actual source code and authoritative evidence, does not claim individual contribution or scientific results, and stores concise execution outputs and a small preview rather than raw payloads. Under D-042, its contributor table is the only repository location permitted to contain a registration number; it has no reviewed-source-commit detail or terminal Handover section.

The shared foundation is finalised for the requested structure, documentation, contributor recording and agent guidance. The initial proposal's complete division is now the finalised working member contribution plan under D-028; it records expected work, not technical completion. Initial biological source feasibility and historical Area 230 API retrievals are documented; their earlier JSON and CSV payloads were removed at the user's request. The 8 October AWS/GeoParquet attempt under D-035 scanned source objects, matched its API IDs, failed the final required-field check and removed its temporary output; its advertised object-size total did not measure transferred bytes. Under D-036, the user selected and authorised the API JSON/CSV route. The downloader retained 24 unchanged response pages: the API reported 23,934 records, all 23,934 IDs were unique, and the CSV conversion verified 23,934 rows across 230 columns against the JSON, including all 68 documented access-page names. The OBIS Area 230 page displays 23,327; exactly 23,327 API rows have both `absence=false` and `dropped=false`. The remaining 607 are flagged records (563 dropped, 50 absence, six overlapping), retained by this unrestricted collection. Counts, hashes and measured response-body bytes are recorded in the [current source record](../records/2026-10-08-source-obis-area-230-api-csv.md). Under current D-038, the OBIS handoff accepts a selected raw CSV path once and writes to a stable source-phase folder; later phases use their own fixed paths. The utility performs structural validation and byte-preserving staging only; it does not implement scientific cleaning. Bio-ORACLE's phase-folder pattern is documentation only, with no code in this branch. The focal species and modelling population remain open; no scientific cleaning, environmental integration, target, model, measured result or final submission exists.

The storage-format convention is recorded under D-032. It guides later data work but does not establish a final source selection, selected model serialization, ML framework or experiment environment, or a deployed BLUEVERSE integration. The Python 3.14 baseline is accepted separately under D-039. COG and ONNX remain optional, unfinalised future integration suggestions.

Two first-page, 10-row OBIS feasibility samples were inspected. Their raw response payloads were removed from local storage at the user's request; their source counts, provenance, sample observations and limitations remain in the [feasibility evidence](../records/2026-10-07-obis-sri-lanka-biological-feasibility.md). The historical 7 October Area 230 API query retrieved 23,934 records, including absences and dropped records, and wrote a 220-column CSV; its 24 JSON pages and CSV were later deleted. The [AWS feasibility assessment](../records/2026-10-07-obis-area-230-geoparquet-feasibility.md) is supplemented by the [8 October export outcome](../records/2026-10-08-obis-area-230-export-attempt.md): that attempt matched all indexed API ID pairs but failed its final schema check because four required access-page fields were missing. Temporary parts were deleted and no output remained when that attempt ended; the later D-036 API output is separately recorded in the [current source record](../records/2026-10-08-source-obis-area-230-api-csv.md). The advertised AWS object-size total is not measured transfer volume; exact bytes for that failed scan remain unavailable. No integrated or analysis-ready dataset, trained model, measured model result, stakeholder engagement record, or track approval record is currently retained. The feasibility samples were not representative or final candidate selections.

## Alignment with the initial proposal

| Proposal commitment | Repository evidence | Assessment |
| --- | --- | --- |
| OCEAVERA is BLUEVERSE's marine intelligence component | [Overview and scope](project-overview-and-scope.md) | Aligned; later integration remains conceptual |
| Industry Explorer selected | [Overview and scope](project-overview-and-scope.md); [requirements](../../PROJECT_REQUIREMENTS.md) | Aligned as a selected track; prior approval unverified |
| Marine Resilience primary; Coastal Tourism secondary | [Overview and scope](project-overview-and-scope.md) | Aligned; rationale retained, no additional tourism prediction task |
| Species distribution and habitat suitability task | [Overview and scope](project-overview-and-scope.md); [ML workflow](../ml/ml-workflow-and-evidence-gates.md) | Aligned at proposal level |
| OBIS and Bio-ORACLE core; OBIStherm potentially supporting | [Overview and scope](project-overview-and-scope.md); [governance](../data/data-storage-and-provenance.md) | Current Area 230 API JSON/CSV acquisition under D-036; prior AWS attempt is historical; Bio-ORACLE feasibility, source compatibility and contributing-dataset terms remain to be reviewed |
| Sri Lanka-focused/regional scope; species selected after investigation | [Decision register](decision-register.md) | Area 230 is finalised for OBIS collection; focal species and modelling population/domain remain open |
| Occurrence probability / suitability output | [Overview and scope](project-overview-and-scope.md) | Intent preserved; probability claim conditional on target/sampling evidence |
| Acquisition, integration, target, EDA, features, baseline, alternatives, evaluation, interpretation | [Workflow](../ml/ml-workflow-and-evidence-gates.md) | API JSON/CSV acquisition is implemented under D-036; the OBIS source-validation handoff is implemented under D-038. No scientific cleaning or integration is claimed. Bio-ORACLE has documentation only and no branch code |
| Candidate algorithms and metrics remain provisional | [Decision register](decision-register.md) | Aligned; no fixed stack or final algorithm |
| Every member contributes technically; material decisions shared | [Overview and scope](project-overview-and-scope.md); [contributor guidance](../../CONTRIBUTING.md) | Shared participation and every proposed member activity/role preserved in the [responsibility plan](member-responsibilities.md); no completed contribution inferred |
| AI tools assist; the group remains accountable | [AI-use conventions](ai-usage-log-template.md) | Proposal declaration acknowledged; [per-contributor activity](../README.md#contribution-records) records actual assistance and check results; human review remains pending |

## Assessment readiness

| Area | Present | Still required |
| --- | --- | --- |
| Shared initial context | Track, lens rationale, task/output, workflow, open decisions | Specific stakeholder decision and approval evidence |
| Initial member responsibilities | Finalised working allocation for all four members, all activities, shared duties and both pipeline tables in the [member plan](member-responsibilities.md) | Actual technical work, handovers and review evidence; record justified allocation changes as progress requires |
| Core evidence framework | All seven required evidence types have a document or blank form | Completed evidence based on authorised technical work |
| Data and reproducibility | Historical source records for the feasibility samples and API query; Python 3.10+ standard-library JSON downloader, CSV converter and OBIS-only raw-to-interim handoff; current source manifest and page/CSV checksums; phase-folder path contract; Python 3.14 baseline in `.python-version` and repository CI; exact Jupyter Notebook and `ipykernel` pins in root `requirements.txt`; documented `OCEAVERA` Conda setup; no Python environment stored in the repository; manifest/dictionary forms | Review acquisition completeness and contributing-source terms; apply evidence-based cleaning rules; keep Bio-ORACLE implementation out of this branch and revisit source compatibility only when that work is authorised; assess taxonomy, coordinates, dates, repeats, depth and observation concentration; select a focal species and modelling population; integrate data and confirm that the selected scientific stack supports a reproducible Python 3.14 environment. Agents need explicit user authorisation before environment or package operations under D-043 |
| Modelling and evaluation | Baseline/three-alternative requirement; spatial and target safeguards | Target, split, metric decisions, implemented comparisons and results |
| Final deliverables | Complete requirement checklist and destinations | Report, notebook/code, data/dictionary, logs, comparison, demo, individual learning reports |
| Industry Explorer bonus | Five criteria mapped; limits stated | Approval, decision context, verifiable data handling, practical recommendation evidence |

## Next shared decisions

1. Record Industry Explorer approval and the scope to which it applies.
2. Establish a verifiable stakeholder/context, decision need, and realistic success criteria.
3. Review the complete Area 230 occurrence collection with the group; select a focal species and evidence-supported modelling population/domain before documenting any later record-selection rules or integrating environmental layers.
4. Record row meaning, target/background design, validation and metric rationale before model comparison.
5. Select the ML framework, scientific dependencies and reproducible experiment configuration with support for Python 3.14 before analytical implementation beyond the standard-library intake utility; revise the baseline only if compatibility evidence requires it.
6. Review contributing-source terms, actual packaging and tool compatibility against D-032 using the acquired data; record any justified format departure.

These are progression conditions. The [member plan](member-responsibilities.md) establishes proposed ownership and shared participation; the attempted acquisition does not claim that group review or downstream technical stages have started.

## Maintenance review

The [repository review history](repository-review-history.md) preserves both earlier unattributed structural and guidance reviews. Current [contributor logs](../README.md#contribution-records) identify actual repository activity using the [exact identity mapping](ai-team-members.md). Project, data and ML knowledge remains grouped under docs. [PROJECT_REQUIREMENTS.md](../../PROJECT_REQUIREMENTS.md) is the canonical requirements reference, [CONTRIBUTING.md](../../CONTRIBUTING.md) holds record conventions and the [documentation index](../README.md#contribution-records) lists activity logs. The two record-directory READMEs were removed after preserving their guidance; the earlier review history remains unattributed.

The current [resource helper](../../.agents/scripts/validate_agent_resources.py) provides a repeatable structural check using the standard library. Manual routing cases remain review expectations rather than executed behavioural evaluations. Keep local links within the repository and check actual Git status before handover; worktree presence does not imply a commit or publication.

Update this review when new evidence changes the phase or resolves a gap. Preserve unresolved items until a dated record supports the new status.

The user-selected all-rights-reserved policy is recorded in [LICENSE.md](../../LICENSE.md) and decision D-020. Contributor ownership and limited academic identification follow the user's clarification in D-023. This rights policy does not verify third-party data terms or resolve scientific readiness gaps.

## Repository automation

The user's workflow requests authorise repository automation under D-029–D-031; D-040 extends repository checks to every branch push and adds syntax compilation for the current OBIS intake and handoff scripts. [Repository checks](../../.github/workflows/ci.yml) runs the standard-library helper and Python syntax check on pull requests, branch pushes and manual dispatch; it does not execute acquisition or download data. [Development backup maintenance](../../.github/workflows/dev-backup.yml) preserves backup-only history before mirroring `dev` to `dev-backup`. [Lowercase branch policy](../../.github/workflows/branch-policy.yml) deletes newly created branch names containing uppercase letters, without imposing name or pattern specifications. The [workflow guide](github-workflows.md) records execution conditions, permissions, action pins and prerequisites for scientific checks.

All three workflows are implemented locally. This checkout is on `pipeline/biological-data-collection` and has remote-tracking refs for `dev` and `dev-backup`; their live state has not been checked. The lowercase policy has not been exercised against a live branch. GitHub-hosted execution, repository write/force-update/delete settings and any required-check policy remain unverified. Workflow maintenance and current worktree checks are recorded in the [contribution logs](../README.md#contribution-records). This automation does not select the ML environment, start member analysis or satisfy scientific evidence gaps.

## Foundation finalisation

This section preserves the foundation review recorded before the member allocation update. Its numerical inventory is a dated review result; see the subsequent responsibility review below for the current update.

The final review covers the root documents, documentation hierarchy, blank forms, directory purposes, contributor identity/record conventions and all maintained agent resources. Scientific evidence and assessed deliverables remain subject to the gates above. The user requested finalisation; that request does not establish that each document or model result has received independent human verification.

| Surface | Final review |
| --- | --- |
| Root documents | Overview, requirements, contributor guide, agent instructions and licence agree on scope, rights and evidence limits |
| Requirements | Thirteen unique scientific/technical requirements; eight core rubric criteria total 100 marks and five conditional bonus criteria total 10 |
| Agent resources | Eight registered skills, ten routed rules and twelve manual routing cases; metadata and generated routing checked |
| Documentation | Seventy maintained text files, 356 local references and 35 section links checked; UTF-8/LF formatting and JSON valid |
| Contributor records | Four exact account/name mappings; only actual activity has a log, using the ten required fields and explicit timezone |
| Recording structure | Scientific evidence uses dated records; contribution activity uses per-account logs; redundant directory READMEs remain absent |
| Data boundaries | Raw, intermediate and processed directories contain markers only; twelve representative paths ignored and seven intended artefacts retained |
| Git inventory | Seventy-four tracked files inspected; no tracked data payload, generated result, credential file or temporary maintenance artefact identified; existing history preserved |

The [resource helper](../../.agents/scripts/validate_agent_resources.py) checks structure and record format. Manual routing cases have not been run as agent evaluations. No dataset feasibility, model quality, lecturer approval, stakeholder engagement or submission readiness is inferred from these checks. See the [contribution records](../README.md#contribution-records) for the dated actions and executed checks.

At the time of that foundation review, the next stage was a separately authorised framing/approval and data-feasibility investigation. The initial biological feasibility work remains in the [dated assessment](../records/2026-10-07-obis-sri-lanka-biological-feasibility.md). The user later finalised Area 230 as the OBIS collection scope under D-034. The earlier API/CSV retrieval and its removal are historical. D-035's AWS GeoParquet attempt failed its field audit and retained no subset; its outcome remains recorded. The user later superseded D-035 with the current API JSON/CSV method in D-036, and the actual source record now documents that retrieval. Python 3.14 is the project baseline under D-039; focal species, modelling population/domain, target, validation, ML framework and experiment environment remain open until supported by recorded evidence.

## Member responsibility documentation review

The user explicitly requested the initial proposal's member contribution division on 6 October 2026. [D-025](decision-register.md) adopts its transcription into the [canonical plan](member-responsibilities.md), preserving proposed/revisable status and the planning-versus-completed-work distinction.

The coverage review includes all four primary duties and model-building contributions; 48 member activities (11, 11, 13 and 13); nine common participation areas; thirteen shared decisions/reviews; and fifteen pipeline rows with all sixty member-role cells. Member numbering, submission identities and registration numbers were reconciled to the exact contributor mapping. Both responsibility tables were visually inspected. The final prediction duty retains the repository's evidence-dependent probability interpretation.

Requirements R-01–R-13, all seven core evidence types, final group/individual submissions and five conditional bonus evidence areas are mapped to the proposed responsibilities. Handover requirements operationalise existing evidence conventions; they do not claim the proposal allocated a sole report editor, presenter, uploader or particular candidate algorithm. Root guidance, workflow, directory purposes and relevant agent guidance point to the same plan.

Technical implementation, completed handovers, human review of this documentation, track approval and stakeholder engagement remain unevidenced. The allocation request does not start data acquisition or model development. Executed structural checks are recorded in the [acting contributor's log](../ai-contribution/WKS2004-ai-usage.md); manual routing expectations are not executed agent evaluations.

### Responsibility recheck and detailed member files

The subsequent user request asked for a coverage recheck and a general overview with separate detailed member documents. No allocation error was identified: member numbering and identities, all 48 activities, nine common participation areas, thirteen shared decisions and both responsibility tables remain consistent with the initial proposal. Joint primary ownership for feature engineering and candidate training is retained. The prediction responsibility continues to use the evidence-dependent probability qualification required by the maintained scientific safeguards.

Under D-026, the [63-line overview](member-responsibilities.md) now presents the division, role meanings and canonical fifteen-row matrix, linking four detailed member files. Each member file preserves their complete activity list, primary duty, model-building contribution, evidence/handover requirements and all fifteen personal pipeline roles. The [common guide](member-contributions/shared-responsibilities-and-evidence.md) preserves shared duties, R-01–R-13 coverage, all seven evidence types, bonus conditions, handovers, final submissions and change control.

The reorganised documents were compared again with the proposal after migration, including all sixty role cells and each member file's corresponding matrix column. Root guidance, indices, workflow section links and agent knowledge references were updated. Existing uncommitted work and earlier dated records were preserved. Documentation completeness does not establish performed member work, human acceptance or scientific/submission readiness.

### Member privacy update

Under D-027, the user's explicit privacy instruction removes academic identity fields from the four detailed member files. Earlier responsibility reviews describe the comparisons performed at that time; those sensitive fields are no longer retained in public documentation. Attribution uses project contributor names and GitHub accounts. D-042 permits a registration number only in the contributor table of a branch work notebook; it does not extend to activity logs, other documentation or verification output. [Member privacy](../../CONTRIBUTING.md#member-privacy) excludes institutional name forms, email addresses and individual academic/assessment records from public material. Responsibilities, activities and matrix roles are retained.

## Member contribution finalisation

On 6 October 2026, the user requested finalisation of the member contribution plan. D-028 adopts the existing division as the current working allocation. The earlier proposal-only statuses at D-025/D-026 are preserved as history; future responsibility changes still require a recorded decision. Finalisation covers the documentation and assignment of expected work, with no claim that technical tasks or group-wide human verification are complete.

| Review area | Final state |
| --- | --- |
| Organisation | General overview and canonical matrix; four detailed member files; one common guide |
| Member duties | All 48 activities, primary responsibilities and model-building contributions retained |
| Pipeline roles | Fifteen overview rows and sixty member-role cells; each personal role table agrees with its overview column |
| Shared participation | All nine participation areas and thirteen shared decisions/reviews retained, including joint primary ownership |
| Evidence and submissions | R-01–R-13, all seven evidence types, conditional bonus evidence, handovers and group/individual submissions covered |
| Privacy | Project contributor names/accounts; registration number allowed only in branch-work notebook contributor tables under D-042; other academic identity fields omitted and individual assessment material handled privately |
| Change control | Current plan finalised; later changes recorded without silently reassigning duties |
| Implementation | Area 230 data intake is completed and evidenced; analytical work, models, approvals and other technical contributions remain pending evidence |

The final review checked role-table agreement, identity mapping, activity counts, requirement coverage, privacy patterns, local references and formatting. The executed results and their limits are in the [contribution log](../ai-contribution/WKS2004-ai-usage.md). It establishes a consistent contribution plan, not scientific validity or assessment completion.

## Data and model storage-convention review

The user requested the storage analysis be reflected across the repository and clarified that COG and ONNX are optional, unfinalised future BLUEVERSE integration suggestions. D-032 and the dated [storage convention record](../records/2026-10-07-data-storage-format-conventions.md) now preserve source formats, GeoParquet for compatible spatial tables, Parquet for compatible non-spatial ML tables, JSON metadata, conditional model serialization and the integration boundary. The existing `raw/`, `interim/` and `processed/` layout remains authoritative.

At the time of the storage-convention review, no data had been acquired and the expected CSV/NetCDF examples had not been checked against source downloads. The 7 October Area 230 API/CSV export is historical and its payloads were removed. D-035 later selected an AWS GeoParquet method, which failed final schema validation and retained no output. D-036 now supersedes it with the current Area 230 API JSON/CSV intake; its evidence is in the [current source record](../records/2026-10-08-source-obis-area-230-api-csv.md). No model, serialization library, ML framework or experiment environment, COG or ONNX artefact has been retained, selected or generated. Python 3.14 is now the project baseline under D-039. PostGIS/API handling is documented only for a future BLUEVERSE handover; the receiving interface and implementation are not verified. The manifest and model metadata templates remain blank templates rather than evidence.

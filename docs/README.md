# Documentation index

## Authoritative documents

| Area | Document | Purpose |
| --- | --- | --- |
| Requirements | [PROJECT_REQUIREMENTS.md](../PROJECT_REQUIREMENTS.md) | Project obligations, deliverables, rubric and acceptance evidence |
| Project | [Overview and scope](project/project-overview-and-scope.md) | Identity, proposal commitments, scope and interpretation limits |
| Project | [Decision register](project/decision-register.md) | Planning positions, repository conventions and unresolved choices |
| Project | [Readiness and alignment](project/repository-readiness-and-alignment.md) | Current phase, evidence gaps and readiness |
| Project | [GitHub workflows](project/github-workflows.md) | Current CI, local checks, failure handling and prerequisites for scientific automation |
| Project | [Member responsibilities](project/member-responsibilities.md) | General division, pipeline matrix and navigation to detailed member duties |
| Project | [Shared responsibilities and evidence](project/member-contributions/shared-responsibilities-and-evidence.md) | Common participation, decisions, requirements, handovers and final submissions |
| Project | [Contributor identities](project/ai-team-members.md) | Exact account-to-name mapping for records |
| Project | [AI-usage recording template](project/ai-usage-log-template.md) | Ten required fields and attribution discipline |
| Project | [Repository review history](project/repository-review-history.md) | Preserved earlier unattributed maintenance reviews |
| Data | [Storage and provenance](data/data-storage-and-provenance.md) | Acquisition, storage, spatial integration and sharing |
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

No acquired-data, approval, stakeholder-engagement, EDA, feature-engineering or modelling record is present. The directory marker preserves the future location; it is not evidence of completed work.

## Contribution records

Use the exact [contributor identities](project/ai-team-members.md) and [recording template](project/ai-usage-log-template.md). Keep meaningful AI-assisted tasks as chronological entries in the acting contributor's file under `docs/ai-contribution/`.

| Contributor | Current activity log |
| --- | --- |
| Wanshaja Sooriyabandara (`WKS2004`) | [Contribution and AI-usage record](ai-contribution/WKS2004-ai-usage.md) |

The [responsibility plan](project/member-responsibilities.md) documents expected technical work separately from the activity logs. Only contributors with recorded activity have logs. The absence of a log does not establish that a member has performed no work. Keep human review status, unrun checks and unavailable metadata explicit.

Earlier shared maintenance notes remain in the [repository review history](project/repository-review-history.md). Their contributor identities were not recorded and have not been retrospectively assigned. Activity records support accountability; scientific artefacts establish their corresponding findings and each member remains responsible for their own assessed learning report.

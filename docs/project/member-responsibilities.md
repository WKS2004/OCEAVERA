# Member responsibilities — overview

OCEAVERA's four members contribute to one marine ML pipeline. This overview records the current working division, based on the initial group submission dated **17 September 2026**, Sections 6.1–6.7 and Tables 6.1–6.2. Detailed duties are linked below.

**Status:** contribution plan finalised on 6 October 2026 at the user's request. The proposal-based division is the current working allocation; later revisions require a recorded decision. Ownership describes expected work; it does not establish performed contributions. Data acquisition, analysis and model implementation remain pending a request to proceed. Consult [current readiness](repository-readiness-and-alignment.md).

## Member identities and primary ownership

Numbering follows the proposal's responsibility sections, not the cover-page name order. Public attribution uses the [contributor mapping](ai-team-members.md). Member-specific academic identity fields are excluded under [member privacy](../../CONTRIBUTING.md#member-privacy).

| Member | Contributor and detailed duties | GitHub account | Primary technical area |
| --- | --- | --- | --- |
| 1 | [Sanuda Abeysinghe](member-contributions/sanuda-abeysinghe.md) | `sanudaabey` | Biological data preparation, target construction and baseline modelling |
| 2 | [Ushan Srinuka](member-contributions/ushan-srinuka.md) | `Ushan-Srinuka` | Environmental data preparation, integration and feature engineering |
| 3 | [Adithya Gunawardana](member-contributions/adithya-gunawardana.md) | `AdithyaGunawardana` | EDA, preprocessing and intermediate model development |
| 4 | [Wanshaja Sooriyabandara](member-contributions/wanshaja-sooriyabandara.md) | `WKS2004` | Model training, validation, evaluation and interpretation |

## How ownership works

- **Primary:** progress and document the area, with group participation.
- **Support:** provide practical assistance to the primary member.
- **Participate:** contribute directly to the technical activity.
- **Review:** check the work and record actual findings.
- **Shared:** participate in a group-level responsibility or decision.

No member has only documentation, coordination, presentation or administrative duties. All four participate across the pipeline and understand the complete method. Feature engineering has joint primary ownership for Ushan and Adithya; candidate training for Adithya and Wanshaja. Sanuda leads the baseline with shared participation; Wanshaja leads interpretation and suitability output with shared participation.

Species, marine boundary, final features, sampling, preprocessing, candidate methods, leakage controls, validation, comparison, interpretation, limitations, final model and output review remain shared decisions. The [common guide](member-contributions/shared-responsibilities-and-evidence.md#shared-technical-responsibilities) preserves all nine participation areas and thirteen shared decisions from the proposal. Primary ownership does not confer exclusive decision authority.

## Complete pipeline responsibility matrix

The fifteen rows below preserve both proposal tables in Member 1–4 order. Each detailed member file includes its corresponding column for practical reference.

| ML activity | Sanuda — Member 1 | Ushan — Member 2 | Adithya — Member 3 | Wanshaja — Member 4 |
| --- | --- | --- | --- | --- |
| Biological data collection | Primary | Support | Support | Review |
| Environmental data collection | Support | Primary | Support | Review |
| Data cleaning | Primary — biological | Primary — environmental | Primary — integrated dataset | Review |
| Spatial data integration | Support | Primary | Support | Review |
| Target / pseudo-absence construction | Primary | Support | Support | Review |
| Exploratory data analysis | Participate | Participate | Primary | Participate |
| Preprocessing | Participate | Participate | Primary | Participate |
| Feature engineering | Participate | Primary | Primary | Participate |
| Baseline modelling | Primary / Shared | Participate | Participate | Participate |
| Candidate model training | Participate | Participate | Primary | Primary |
| Model validation | Participate | Participate | Participate | Primary |
| Model evaluation | Participate | Participate | Participate | Primary |
| Model interpretation | Participate | Participate | Participate | Primary / Shared |
| Habitat-suitability output | Participate | Participate | Participate | Primary / Shared |
| Final technical decisions | Shared | Shared | Shared | Shared |

## Evidence, handovers and submission

Detailed activities and personal handovers belong in the linked member files. The [common guide](member-contributions/shared-responsibilities-and-evidence.md) specifies:

- [R-01–R-13 coverage, seven evidence types and conditional Industry Explorer evidence](member-contributions/shared-responsibilities-and-evidence.md#requirement-and-evidence-coverage).
- [Cross-member dependencies, technical handovers and final group/individual submissions](member-contributions/shared-responsibilities-and-evidence.md#handover-and-final-submission-duties).
- [Actual contribution recording and allocation change control](member-contributions/shared-responsibilities-and-evidence.md#recording-progress-and-changes).
- [Proposal section coverage](member-contributions/shared-responsibilities-and-evidence.md#proposal-coverage-review).

All four assemble and review the final group evidence and three-minute demo; each prepares their own one-A4 Personal Learning Journey. The allocation does not select a sole editor, presenter, uploader, particular candidate algorithm, deadline or contribution percentage.

Follow [PROJECT_REQUIREMENTS.md](../../PROJECT_REQUIREMENTS.md), the [workflow gates](../ml/ml-workflow-and-evidence-gates.md) and the [decision register](decision-register.md). Keep presence/background outputs as relative suitability unless observation and sampling evidence justify ecological occurrence probabilities. Record actual work in scientific evidence and [contributor activity logs](../README.md#contribution-records), separately from this plan.

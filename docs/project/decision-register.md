# Decision register

This register separates shared proposal commitments from technical decisions still requiring evidence. Proposal positions date to 17 September 2026; repository conventions were reviewed on 6 October 2026. No entry establishes lecturer approval or a completed technical contribution.

## Status meanings

- **Planning baseline:** retained direction from the proposal; implementation feasibility remains unverified.
- **Provisional:** a candidate or intended output subject to investigation.
- **Open:** no final decision or adequate evidence exists.
- **Accepted convention:** a repository working standard adopted for the shared foundation.

Detailed decision records use proposed, accepted, rejected, or superseded status, with dates and links. An accepted technical decision still requires supporting evidence; the label alone proves nothing.

## Register

| ID | Topic | Current position | Status | Evidence needed or next action |
| --- | --- | --- | --- | --- |
| D-001 | Identity | OCEAVERA is BLUEVERSE's marine intelligence component | Planning baseline | [Overview and scope](project-overview-and-scope.md); later integration remains conceptual |
| D-002 | Track | Industry Explorer selected | Open: approval not evidenced | Record approver, date, approved scope and verifiable evidence |
| D-003 | Lenses | Marine Resilience primary; Coastal Tourism supporting context | Planning baseline | Establish a concrete decision/context and coherent secondary-lens value |
| D-004 | Task | Species distribution and habitat suitability | Planning baseline | Finalise exact question, unit and success criteria after feasibility |
| D-005 | Sources | OBIS and Bio-ORACLE core; OBIStherm optional support | Provisional | Exact resources, versions, terms, queries, coverage and compatibility |
| D-006 | Geography | Sri Lanka-focused or regionally constrained marine area | Open | Data-supported marine boundary and domain of use |
| D-007 | Species | One focal species, or a few only if justified | Open | Record counts, quality, coverage, relevance and manageable scope |
| D-008 | Unit | Spatial observation/location, potentially a grid cell | Open | Resolution, coordinate system, marine mask, repeated-record handling |
| D-009 | Target | Presence with justified background or pseudo-absence comparison | Open | Sampling domain/process, label meaning, bias and sensitivity analysis |
| D-010 | Output | Intended occurrence probability / suitability, potentially mapped | Provisional | Establish interpretation from sampling/observation design; otherwise relative suitability |
| D-011 | Methods | Simple baseline; candidate Logistic Regression, Random Forest, Gradient Boosting, XGBoost/equivalent and SVM if suitable | Provisional | At least three alternatives selected and justified against actual data |
| D-012 | Validation and metrics | Spatial validation considered; candidate precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix and calibration where relevant | Open | Partitions, leakage controls, primary metric, thresholds and interpretation |
| D-013 | BLUEVERSE handover | Later transfer of evaluated biodiversity output | Planning baseline | Output contract and limitations; deployment outside current scope |
| D-014 | Runtime | Language, dependencies and environment manager undecided | Open | Agreed stack, versioned environment and runnable workflow instructions |
| D-015 | Participation | All four members contribute technically; key decisions shared | Planning baseline | Individual allocation not reproduced or started in this shared foundation |
| D-016 | Local references | Local documentation references resolve inside this repository | Accepted convention | User direction; [contributor guidance](../../CONTRIBUTING.md) |
| D-017 | Evidence lifecycle | Copy blank templates into dated records; distinguish plans from findings | Accepted convention | [Record conventions](../../CONTRIBUTING.md#project-evidence-records); [maintenance record](repository-review-history.md) |
| D-018 | Documentation and agent architecture | Descriptive document names; canonical knowledge in docs; focused workflows with registry/routing and structural validation | Accepted convention | [Guidance review](repository-review-history.md); [agent guide](../../.agents/README.md) |
| D-019 | Contributor recording and document organisation | Exact contributor mapping; dated per-account AI-usage entries; thematic documentation; preserve unattributed review history | Accepted convention | User request of 6 October 2026; [identities](ai-team-members.md), [recording template](ai-usage-log-template.md) and [current activity](../ai-contribution/WKS2004-ai-usage.md); no technical allocation implied |
| D-020 | Reuse policy | All rights reserved; no public reuse grant; preserve third-party terms and respective ownership | Accepted convention | User-selected policy of 6 October 2026; [LICENSE.md](../../LICENSE.md) |
| D-021 | Root requirements and record navigation | Canonical requirements at the root; record conventions in contributor guidance; log index in the documentation index | Accepted convention | User request of 6 October 2026; [requirements](../../PROJECT_REQUIREMENTS.md), [record conventions](../../CONTRIBUTING.md#project-evidence-records) and [contribution index](../README.md#contribution-records) |
| D-022 | Licence presentation and permission evidence | Formal group-centred notice with numbered restrictions, written permission evidence, contributor accounts and academic/third-party boundaries; D-020 policy retained | Accepted convention | User request of 6 October 2026; [LICENSE.md](../../LICENSE.md); permission requires the relevant rights holders or a member authorised to represent them |
| D-023 | Contributor ownership and academic identification | Original project ownership belongs to the group contributors; academic association confers no institutional ownership; identify the institution only where course context requires it | Accepted convention | Explicit ownership clarification supplied by the user on 6 October 2026; [LICENSE.md](../../LICENSE.md), Section 5; updates the academic-context wording used for D-022 |
| D-024 | Shared foundation finalisation | Root documents, evidence structure, contributor records and agent guidance form the finalised shared foundation; technical implementation and assessed deliverables remain pending | Accepted convention | User request of 6 October 2026; [final foundation review](repository-readiness-and-alignment.md#foundation-finalisation); no new species, stack, member allocation or model decision |

## Recording a material decision

Copy the [decision form](../templates/decision-record.md) into a dated record under `docs/records/`, following the [record conventions](../../CONTRIBUTING.md#project-evidence-records). Retain the stable ID, options, evidence, rationale, consequences and status. Link the record from this register and update affected documents. When superseding a decision, preserve its earlier rationale and link the replacement.

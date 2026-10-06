# Sanuda Abeysinghe — member responsibilities

| Field | Value |
| --- | --- |
| Proposal member | 1 |
| Contributor | Sanuda Abeysinghe |
| GitHub account | `sanudaabey` |
| Document status | Finalised on 6 October 2026 |
| Allocation status | Current working allocation; changes require a recorded decision |
| Execution status | Planned duties; this document establishes no completed contribution |

Read the [group overview](../member-responsibilities.md) for ownership definitions and the complete matrix. This file contains this member's full proposal activities and practical evidence/handover expectations. The [shared duties](shared-responsibilities-and-evidence.md) also apply to this member, including whole-pipeline participation, shared decisions and final submissions. Identity spelling follows the [contributor mapping](../ai-team-members.md).

**Proposal reference:** Section 6.2. **Primary practical responsibility:** prepare the biological component of the ML dataset and contribute directly to initial model development.

## Required activities

1. Acquire and investigate OBIS species occurrence data.
2. Analyse candidate species and occurrence counts.
3. Check taxonomic consistency and biological record quality.
4. Clean invalid, duplicate or unsuitable occurrence records.
5. Analyse geographic and temporal distributions.
6. Contribute to selection of the focal species and study region.
7. Prepare biological occurrence observations for spatial integration.
8. Investigate background and pseudo-absence construction strategies.
9. Participate in target-variable construction.
10. Implement or support the baseline modelling approach.
11. Participate in EDA and model evaluation.

**Model-building contribution:** construction of the target dataset and baseline model, both fundamental components of the ML pipeline. The baseline remains subject to the final task and agreed protocol; a dummy classifier or simple statistical approach is a candidate rather than a fixed commitment.

## Evidence and handover

- Preserve occurrence provenance, contributing-dataset citations/terms, query, retrieval details and fingerprints using the [source form](../../templates/data-source-record.md). Report measured species counts, quality, geographic/temporal coverage and feasibility evidence.
- Record cleaning rules, counts and reasons; preserve raw inputs. Supply stable occurrence identifiers, coordinates, dates and taxonomic definitions for Ushan's integration, with biological fields in the [dictionary](../../templates/data-dictionary.md).
- Document accessible sampling domain, label meaning, bias, seed/counts and sample origin with the [evaluation design](../../templates/validation-and-evaluation-plan.md). Coordinate environmental extraction for constructed background samples with Ushan; obtain group review before final target decisions.
- Hand the versioned biological/target inputs to Ushan and Adithya. Supply the baseline configuration, generating code/notebook and results to Adithya and Wanshaja for comparable runs.
- Contribute biological and target-method sections, decision evidence and limitations to the shared report; retain actual contribution and AI-use evidence.

## Participation across the pipeline

The following is this member's column from the [canonical responsibility matrix](../member-responsibilities.md#complete-pipeline-responsibility-matrix), retaining every primary, support, participation, review and shared role. It supplements the required activities above; it does not replace shared technical duties.

| ML activity | Working role |
| --- | --- |
| Biological data collection | Primary |
| Environmental data collection | Support |
| Data cleaning | Primary — biological |
| Spatial data integration | Support |
| Target / pseudo-absence construction | Primary |
| Exploratory data analysis | Participate |
| Preprocessing | Participate |
| Feature engineering | Participate |
| Baseline modelling | Primary / Shared |
| Candidate model training | Participate |
| Model validation | Participate |
| Model evaluation | Participate |
| Model interpretation | Participate |
| Habitat-suitability output | Participate |
| Final technical decisions | Shared |

## Shared duties, submission and recording

- Participate in all [shared technical activities and decisions](shared-responsibilities-and-evidence.md#shared-technical-responsibilities); understand and review the complete pipeline. Primary ownership does not permit unilateral final scientific choices.
- Supply reproducible evidence for this member's actual work and contribute to the group report, final notebook/code, dataset/dictionary, decision logs, comparison and three-minute demo under the [handover and submission duties](shared-responsibilities-and-evidence.md#handover-and-final-submission-duties).
- Prepare this member's own one-A4 Personal Learning Journey from actual work and learning. Agents must not generate assessed individual reflections.
- Record actual work, support and review separately from planned ownership, following the [progress conventions](shared-responsibilities-and-evidence.md#recording-progress-and-changes) and [AI-use template](../ai-usage-log-template.md). Do not create an empty activity log or infer completed contribution from this file.
- Keep unresolved species, study domain, features, targets, algorithms, validation and runtime choices in the [decision register](../decision-register.md). Technical execution remains pending a request to proceed; consult [current readiness](../repository-readiness-and-alignment.md).

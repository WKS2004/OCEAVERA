# Wanshaja Sooriyabandara — member responsibilities

| Field | Value |
| --- | --- |
| Proposal member | 4 |
| Contributor | Wanshaja Sooriyabandara |
| GitHub account | `WKS2004` |
| Document status | Finalised on 6 October 2026 |
| Allocation status | Current working allocation; changes require a recorded decision |
| Execution status | Planned duties; this document establishes no completed contribution |

Read the [group overview](../member-responsibilities.md) for ownership definitions and the complete matrix. This file contains this member's full proposal activities and practical evidence/handover expectations. The [shared duties](shared-responsibilities-and-evidence.md) also apply to this member, including whole-pipeline participation, shared decisions and final submissions. Identity spelling follows the [contributor mapping](../ai-team-members.md).

**Proposal reference:** Section 6.5. **Primary practical responsibility:** develop and evaluate the main candidate models and assess predictive performance.

## Required activities

1. Implement selected candidate ML algorithms.
2. Perform model training and hyperparameter investigation where appropriate.
3. Develop the model-comparison process.
4. Select suitable evaluation metrics.
5. Investigate appropriate validation strategies.
6. Examine the effect of spatial structure on validation.
7. Produce confusion matrices and other evaluation outputs.
8. Compare candidate models beyond simple accuracy.
9. Investigate probability calibration where relevant.
10. Analyse feature importance or model interpretability where supported.
11. Generate final occurrence-prediction scores, with occurrence-probability interpretation only where justified.
12. Support habitat-suitability visualisation.
13. Participate in EDA, preprocessing review and feature-engineering decisions.

**Model-building contribution:** primary responsibility for a substantial part of training, validation and evaluation, while participating in earlier pipeline stages. Interpretation and habitat-suitability output are primary/shared responsibilities, not unilateral final model decisions.

The submission calls the final output occurrence probabilities. Under the maintained [scientific safeguards](../../../PROJECT_REQUIREMENTS.md), presence/background scores must be presented as relative suitability unless sampling and observation evidence justify ecological probabilities. Calibration against constructed labels alone does not establish that interpretation. This qualification preserves the prediction duty while preventing unsupported claims.

## Evidence and handover

- Develop the [evaluation plan](../../templates/validation-and-evaluation-plan.md) with all members: generalisation question, spatial/shared-cell and temporal leakage checks, splits, metrics, thresholds, tuning boundaries and uncertainty.
- Coordinate candidate implementation with Adithya and the baseline with Sanuda; ensure a sensible baseline plus at least three justified alternatives in total. Use the same dataset/partitions/protocol and record parameters, seeds, fold variability and held-out evaluation.
- Maintain the [model comparison](../../templates/model-comparison.md), confusion matrices and other supported evaluation outputs, calibration analysis where relevant, error/geographic patterns and supported interpretability evidence. Do not use final test scores repeatedly for tuning or infer ecological causation.
- After shared model selection, generate supported predictions and suitability visualisations with score/domain/uncertainty definitions. Complete [model metadata](../../templates/model-metadata.json) for actual artefacts and the [recommendation](../../templates/recommendations-and-limitations.md) with group review.
- Once the group has agreed on the model and environment, record the actual serialization format and library/version in model metadata. The conditional Joblib/XGBoost examples in [data governance](../../data/data-storage-and-provenance.md) do not select algorithms, libraries or deployment formats.
- Hand evaluated output, feature/schema requirements, generating method and limitations to the group for the final package and conceptual BLUEVERSE handover. Contribute model, evaluation, interpretation and output sections; retain actual contribution and AI-use evidence.

## Participation across the pipeline

The following is this member's column from the [canonical responsibility matrix](../member-responsibilities.md#complete-pipeline-responsibility-matrix), retaining every primary, support, participation, review and shared role. It supplements the required activities above; it does not replace shared technical duties.

| ML activity | Working role |
| --- | --- |
| Biological data collection | Review |
| Environmental data collection | Review |
| Data cleaning | Review |
| Spatial data integration | Review |
| Target / pseudo-absence construction | Review |
| Exploratory data analysis | Participate |
| Preprocessing | Participate |
| Feature engineering | Participate |
| Baseline modelling | Participate |
| Candidate model training | Primary |
| Model validation | Primary |
| Model evaluation | Primary |
| Model interpretation | Primary / Shared |
| Habitat-suitability output | Primary / Shared |
| Final technical decisions | Shared |

## Shared duties, submission and recording

- Participate in all [shared technical activities and decisions](shared-responsibilities-and-evidence.md#shared-technical-responsibilities); understand and review the complete pipeline. Primary ownership does not permit unilateral final scientific choices.
- Supply reproducible evidence for this member's actual work and contribute to the group report, final notebook/code, dataset/dictionary, decision logs, comparison and three-minute demo under the [handover and submission duties](shared-responsibilities-and-evidence.md#handover-and-final-submission-duties).
- Prepare this member's own one-A4 Personal Learning Journey from actual work and learning. Agents must not generate assessed individual reflections.
- Record actual work, support and review separately from planned ownership, following the [progress conventions](shared-responsibilities-and-evidence.md#recording-progress-and-changes) and [AI-use template](../ai-usage-log-template.md). Do not create an empty activity log or infer completed contribution from this file.
- Keep unresolved species, study domain, features, targets, algorithms, validation, ML framework and experiment environment choices in the [decision register](../decision-register.md). The Python baseline is 3.14 under D-039. Technical execution remains pending a request to proceed; consult [current readiness](../repository-readiness-and-alignment.md).

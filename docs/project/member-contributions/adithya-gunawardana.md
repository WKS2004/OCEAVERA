# Adithya Gunawardana — member responsibilities

| Field | Value |
| --- | --- |
| Proposal member | 3 |
| Contributor | Adithya Gunawardana |
| GitHub account | `AdithyaGunawardana` |
| Document status | Finalised on 6 October 2026 |
| Allocation status | Current working allocation; changes require a recorded decision |
| Execution status | Planned duties; this document establishes no completed contribution |

Read the [group overview](../member-responsibilities.md) for ownership definitions and the complete matrix. This file contains this member's full proposal activities and practical evidence/handover expectations. The [shared duties](shared-responsibilities-and-evidence.md) also apply to this member, including whole-pipeline participation, shared decisions and final submissions. Identity spelling follows the [contributor mapping](../ai-team-members.md).

**Proposal reference:** Section 6.4. **Primary practical responsibility:** investigate the integrated dataset and transform it into a reliable modelling dataset.

## Required activities

1. Perform detailed exploratory data analysis (EDA).
2. Analyse class distribution and potential imbalance.
3. Investigate feature distributions and correlations.
4. Analyse missing values and outliers.
5. Identify possible spatial sampling bias.
6. Investigate leakage risks.
7. Design and implement preprocessing steps.
8. Apply scaling or transformation where required.
9. Support feature selection and preprocessing pipelines.
10. Prepare appropriate training and validation datasets.
11. Train one or more selected candidate ML models.
12. Compare intermediate results with the baseline.
13. Participate in evaluation and technical interpretation.

**Model-building contribution:** develop the preprocessing pipeline and train candidate ML models using the prepared dataset. Candidate training has joint primary ownership with Wanshaja; the group must record which agreed alternatives each implements rather than infer fixed algorithms from this allocation.

## Evidence and handover

- Record observed distributions, missingness, outliers, correlations/multicollinearity, imbalance, spatial bias and decision implications in the [EDA log](../../templates/eda-insight-log.md), with dataset and generating-artefact references.
- Document justified cleaning, scaling, transformations, imputation and imbalance treatment in the [preprocessing/feature log](../../templates/preprocessing-and-feature-decisions.md). Coordinate feature engineering with Ushan and biological exclusions with Sanuda.
- Preserve the integrated dataset's recorded format. Use Parquet for compatible non-spatial modelling tables or GeoParquet where the spatial geometry remains part of the dataset; record conversions and reasons in the manifest and generating evidence.
- Agree partitions and leakage controls with Wanshaja before design-informing EDA or learned preprocessing. Prepare versioned training/validation inputs and fit learned transformations within training folds; preserve the final held-out evaluation boundary.
- Hand the reproducible preprocessing pipeline, feature order/types, partition identifiers and candidate configurations/results to Wanshaja. Compare intermediate candidates with Sanuda's baseline on the same protocol and dataset version.
- Contribute EDA, preparation and intermediate-method sections, observed findings and limitations to the shared report; retain actual contribution and AI-use evidence.

## Participation across the pipeline

The following is this member's column from the [canonical responsibility matrix](../member-responsibilities.md#complete-pipeline-responsibility-matrix), retaining every primary, support, participation, review and shared role. It supplements the required activities above; it does not replace shared technical duties.

| ML activity | Working role |
| --- | --- |
| Biological data collection | Support |
| Environmental data collection | Support |
| Data cleaning | Primary — integrated dataset |
| Spatial data integration | Support |
| Target / pseudo-absence construction | Support |
| Exploratory data analysis | Primary |
| Preprocessing | Primary |
| Feature engineering | Primary |
| Baseline modelling | Participate |
| Candidate model training | Primary |
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
- Keep unresolved species, study domain, features, targets, algorithms, validation, ML framework and experiment environment choices in the [decision register](../decision-register.md). The Python baseline is 3.14 under D-039. Technical execution remains pending a request to proceed; consult [current readiness](../repository-readiness-and-alignment.md).

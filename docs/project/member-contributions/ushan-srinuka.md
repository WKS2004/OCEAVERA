# Ushan Srinuka — member responsibilities

| Field | Value |
| --- | --- |
| Proposal member | 2 |
| Contributor | Ushan Srinuka |
| GitHub account | `Ushan-Srinuka` |
| Document status | Finalised on 6 October 2026 |
| Allocation status | Current working allocation; changes require a recorded decision |
| Execution status | Planned duties; this document establishes no completed contribution |

Read the [group overview](../member-responsibilities.md) for ownership definitions and the complete matrix. This file contains this member's full proposal activities and practical evidence/handover expectations. The [shared duties](shared-responsibilities-and-evidence.md) also apply to this member, including whole-pipeline participation, shared decisions and final submissions. Identity spelling follows the [contributor mapping](../ai-team-members.md).

**Proposal reference:** Section 6.3. **Primary practical responsibility:** prepare environmental predictors and develop the biological–environmental feature dataset.

## Required activities

1. Acquire the required Bio-ORACLE environmental data.
2. Analyse available environmental variables.
3. Examine units, spatial resolution and missing values.
4. Select candidate variables for initial integration.
5. Prepare and transform environmental data for modelling.
6. Perform spatial matching between environmental layers and biological observations.
7. Construct the integrated feature table.
8. Investigate correlations and redundancy between environmental variables.
9. Conduct relevant feature engineering.
10. Participate in EDA, preprocessing and feature selection.
11. Participate in model training and comparison.

**Model-building contribution:** directly construct model predictors and contribute to feature engineering and training. Feature engineering has joint primary ownership with Adithya in the proposal's pipeline matrix.

## Evidence and handover

- Preserve each complete environmental source in its delivered format; record that format alongside exact layers/releases, units, spatial resolution, coordinate system, temporal period/statistic, surface or benthic context, marine mask, no-data conventions, terms and fingerprints using the [source form](../../templates/data-source-record.md). Extract only justified location-level values into derived tables; do not flatten full rasters.
- Record regional restriction, transformations, extraction/join method, environmental cell IDs, unmatched observations and before/after counts. Justify temporal/depth compatibility with Sanuda; do not infer compatibility from geographic proximity alone.
- Hand the versioned integrated feature table and [dataset manifest](../../templates/dataset-manifest.json) to Adithya and Wanshaja. Use GeoParquet for compatible spatial tables and record the actual format/specification version. Maintain the [dictionary](../../templates/data-dictionary.md), including variable definitions, feature lineage, row meaning and target/sample identifiers.
- Develop feature decisions jointly with Adithya in the [feature log](../../templates/preprocessing-and-feature-decisions.md); supply documented features and applicable transformations to all modelling work under one validation protocol.
- Contribute environmental-data, integration and feature-method sections, decision evidence and limitations to the shared report; retain actual contribution and AI-use evidence.

## Participation across the pipeline

The following is this member's column from the [canonical responsibility matrix](../member-responsibilities.md#complete-pipeline-responsibility-matrix), retaining every primary, support, participation, review and shared role. It supplements the required activities above; it does not replace shared technical duties.

| ML activity | Working role |
| --- | --- |
| Biological data collection | Support |
| Environmental data collection | Primary |
| Data cleaning | Primary — environmental |
| Spatial data integration | Primary |
| Target / pseudo-absence construction | Support |
| Exploratory data analysis | Participate |
| Preprocessing | Participate |
| Feature engineering | Primary |
| Baseline modelling | Participate |
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

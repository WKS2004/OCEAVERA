# Shared responsibilities and contribution evidence

This is the detailed common guide for all four members. The [overview](../member-responsibilities.md) holds the group allocation and complete pipeline matrix; each linked member file holds that person's full activities and handover expectations. The shared duties below preserve proposal Sections 6.1 and 6.6. Requirements, evidence and submission instructions operationalise the maintained project obligations; they do not assign extra exclusive administrative roles.

The contribution plan is finalised for the current scope on 6 October 2026. Its proposal-based allocation remains revisable through recorded decisions. Planned responsibilities do not establish completed contributions, stakeholder engagement or track approval. This documentation review does not initiate technical implementation.

Follow [member privacy](../../../CONTRIBUTING.md#member-privacy) throughout reporting and contribution recording. Public attribution uses project contributor names and GitHub accounts; member-specific academic identity fields and individual assessment material are excluded. Prepare individual learning submissions through the authorised private submission process.

## Shared technical responsibilities

### Participation across the pipeline

Section 6.1 requires all four members to contribute directly to practical ML development. No member has only documentation, coordination, presentation or administrative responsibility. Every member must participate in all nine shared activity areas:

1. Dataset investigation.
2. Preprocessing decisions.
3. Exploratory analysis.
4. Feature engineering.
5. Model development.
6. Model comparison.
7. Evaluation.
8. Technical interpretation.
9. Review of the final ML pipeline.

### Group decisions and reviews

Section 6.6 identifies all thirteen responsibilities below as shared:

1. Confirm the focal species.
2. Define the study region.
3. Select the final feature set.
4. Decide the pseudo-absence or background strategy.
5. Review preprocessing choices.
6. Select candidate algorithms.
7. Check for leakage.
8. Determine appropriate validation methods.
9. Compare models.
10. Interpret model behaviour.
11. Identify limitations.
12. Select the final modelling approach.
13. Review the final habitat-suitability output.

All four must understand the complete pipeline. Record options, evidence, reasons and actual review outcomes in dated [decision records](../../templates/decision-record.md) and the [register](../decision-register.md). Primary members prepare evidence; the proposal does not set a voting rule, reviewer approval threshold or permission to silently finalise shared scientific choices.

## Requirement and evidence coverage

This operational mapping connects the proposal roles to all thirteen maintained requirements. Shared responsibilities remain shared; it adds no exclusive administrative member role.

| Requirement | Responsibility and required handover |
| --- | --- |
| R-01: framing and value | All four define stakeholder/context, decision, lenses, unit, question, output and success criteria in the [framing record](../../templates/problem-framing-canvas.md); retain approval evidence before claiming approved scope |
| R-02: species and domain | Sanuda supplies biological feasibility; Ushan supplies environmental compatibility; all four decide the feasible species and boundary |
| R-03: source provenance | Sanuda maintains biological source evidence; Ushan environmental evidence; Adithya processing lineage; Wanshaja checks links between sources, runs and reported evaluation |
| R-04: field semantics and quality | Sanuda biological quality; Ushan environmental/join definitions; Adithya integrated quality and EDA; Wanshaja review; combine into one versioned dictionary |
| R-05: target and sampling | Sanuda primary; Ushan/Adithya support; Wanshaja review; group agrees sampling meaning, domain, bias, seeds/counts and limits |
| R-06: validation and leakage | Wanshaja primary design; Adithya prepares partitions/pipelines; Sanuda/Ushan provide occurrence/grid/temporal evidence; all four review |
| R-07: preprocessing/features | Adithya primary preprocessing; Ushan and Adithya joint primary features; Sanuda/Wanshaja participate; record training-only learned transformations |
| R-08: baseline and alternatives | Sanuda leads baseline; Adithya/Wanshaja jointly lead candidate training; Ushan participates; all four justify methods and compare a baseline plus at least three alternatives |
| R-09: critical evaluation | Wanshaja primary; all four assess metrics, errors, thresholds, fold variability and uncertainty without tuning repeatedly on final evaluation |
| R-10: score interpretation | Wanshaja primary/shared interpretation; all four review target-dependent meaning, probability evidence and non-causal claims |
| R-11: recommendations and limits | All four assemble practical value and limitations from their evidence; Wanshaja supports the evaluated suitability output |
| R-12: reproducibility | Each member documents inputs, configuration, seeds and execution for their work; all four agree the runtime and verify end-to-end/report consistency |
| R-13: AI transparency and learning | Each member records their actual assistance/verification under their own verified identity and prepares their own individual learning submission |

All seven core evidence types remain required: shared framing canvas; shared workflow diagram; shared decision log; Adithya-led EDA insights with all members; Adithya/Ushan-led preprocessing and feature evidence with all members; Wanshaja-led comparison including Sanuda's baseline and Adithya's candidates; shared recommendation and limitations. Ownership of a form is not fulfilment of its scientific requirement.

Industry Explorer evidence is a group responsibility: named stakeholder/context and realistic decision value; early scope approval with manageable seven-week scope; verifiable meaningful real-world data; collection/dictionary/permission/privacy evidence where relevant; and an evidence-based practical recommendation. Sanuda/Ushan supply acquisition evidence, Adithya integrated quality/preparation evidence and Wanshaja evaluation evidence. Contact or publication requires separate authorisation, and none of these conditions is currently verified.

## Handover and final submission duties

Follow the [record conventions](../../../CONTRIBUTING.md#project-evidence-records) and [data governance](../../data/data-storage-and-provenance.md). A technical handover must identify actual contributing members, dataset/resource version and actual file formats, row/target/feature meaning, generating code/notebook, configuration/seeds, counts/checks, exclusions, limitations and unresolved issues. Record format conversions and their reasons. For actual model artefacts, include the serialization format and environment in the metadata. Link existing artefacts; do not create placeholder results or claim the recipient reviewed them without evidence.

1. Sanuda and Ushan exchange occurrence/layer compatibility evidence before final species/domain selection and integration.
2. Sanuda and Ushan provide the biological/target and integrated-feature inputs to Adithya; agree partition design with Wanshaja before design-informing EDA and learned transformations.
3. Adithya and Ushan coordinate feature/preprocessing changes; record dataset/version changes and propagate them to the baseline and every candidate run.
4. Sanuda supplies the baseline; Adithya and Wanshaja record the agreed division of candidate implementations and use the shared comparison protocol. This allocation does not select those algorithms in advance.
5. Wanshaja assembles evaluation evidence for all four to review final selection, predictions, interpretation and limitations.
6. All four assemble and review the final report, notebook/code, dataset/data dictionary, decision logs, model/method comparison and **three-minute YouTube demo**. Each supplies the technical explanation/evidence for their work; the proposal does not name a sole editor, presenter or uploader. Agree any additional logistics explicitly without replacing technical duties.
7. Each member independently prepares the required **one-A4 Personal Learning Journey** based on actual work and learning. Agents must not generate assessed individual reflections. Activity logs do not replace that submission.
8. Any later BLUEVERSE analytical handover requires evaluated artefacts, schema, domain, score meaning, uncertainty and data-use conditions. Deployment, real-time prediction, future-climate projections and unrelated marine models remain outside the immediate scope.

Use [data/](../../../data/README.md) for authorised payloads; [src/](../../../src/README.md) and [notebooks/](../../../notebooks/README.md) for implementation/analysis; [outputs/](../../../outputs/README.md) for supported results; [reports/](../../../reports/README.md) for final reporting; and dated `docs/records/` for scientific/approval evidence. Keep payloads out of Git by default and master [templates](../../templates/README.md) blank.

## Recording progress and changes

Planned ownership belongs in the overview and member files; actual work belongs in evidence and [contributor activity records](../../README.md#contribution-records). Do not create completed contribution claims, empty member logs or percentages from the allocation. Record each member's actual authorship/support/review only when evidenced, with human acceptance separate from retained agent output.

Revise an allocation through a dated decision identifying affected members, previous/new responsibilities, reason, supporting evidence, unfinished handovers and actual agreement status. Preserve the superseded arrangement, link the replacement from the [register](../decision-register.md), and update the overview, affected member files, this common guide, workflow and readiness together. Do not silently move responsibilities or infer group approval from a repository edit.

### Proposal coverage review

| Proposal section | Coverage and location |
| --- | --- |
| 6.1 | Technical primary ownership; no solely administrative roles; all nine shared participation areas; whole-pipeline understanding |
| 6.2 | [Sanuda Abeysinghe](sanuda-abeysinghe.md): member 1 project identity, original proposal status, primary duty, all eleven activities and target/baseline contribution |
| 6.3 | [Ushan Srinuka](ushan-srinuka.md): member 2 project identity, original proposal status, primary duty, all eleven activities and predictor/feature/training contribution |
| 6.4 | [Adithya Gunawardana](adithya-gunawardana.md): member 3 project identity, original proposal status, primary duty, all thirteen activities and preprocessing/candidate contribution |
| 6.5 | [Wanshaja Sooriyabandara](wanshaja-sooriyabandara.md): member 4 project identity, original proposal status, primary duty, all thirteen activities and training/validation/evaluation contribution; probability duty qualified by maintained safeguards |
| 6.6 | All thirteen shared decisions/reviews; integrated project and full-pipeline participation |
| 6.7 | [Overview matrix](../member-responsibilities.md#complete-pipeline-responsibility-matrix): all fifteen activity rows and sixty member-role cells from both tables; primary ownership does not restrict participation; allocations revisable with progress |

This is the finalised responsibility plan and its source-coverage review, not evidence that any technical activity has begun or passed review. Current completion and approval status remain in [readiness](../repository-readiness-and-alignment.md).

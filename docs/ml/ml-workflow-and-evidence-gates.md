# ML workflow and evidence gates

This is a shared analytical workflow, not a member task allocation or a fixed modelling recipe. The current phase is recorded in the [status review](../project/repository-readiness-and-alignment.md). Technical stages remain pending until requested.

## Workflow

```mermaid
flowchart TD
    A[Frame decision context, lenses, task and scope] --> B[Record track approval status and required evidence]
    B --> C[Identify candidate resources and acquire a bounded feasibility sample]
    C --> D{Coverage and quality support a manageable task?}
    D -- No --> A
    D -- Yes --> E[Select focal species, marine boundary and compatible layers]
    E --> F[Acquire final inputs and record provenance]
    F --> G[Check quality and align space, time and depth]
    G --> H[Define row meaning, target and background sampling]
    H --> I[Define validation partitions and metric rationale]
    I --> J[Explore training data and document insights]
    J --> K[Fit preprocessing and feature steps within training partitions]
    K --> L[Fit baseline and at least three justified alternatives]
    L --> M[Compare validation results and select approach]
    M --> N[Evaluate held-out performance and interpretation limits]
    N --> O[Prepare supported suitability outputs and uncertainty]
    O --> P[Make recommendation and assemble reproducible evidence]
    J -. Quality evidence may change data choices .-> E
    M -. Documented design revision .-> H
```

Limited feasibility investigation may inform framing and the approval request. It does not establish approval or stakeholder engagement. Prior approval must be evidenced before claiming an approved Industry Explorer project.

Non-outcome quality checks can cover the acquired data. Exploratory work that influences feature choice or model design must respect validation boundaries. After a design revision, maintain a genuinely held-out evaluation; do not repeatedly inspect test results to tune the pipeline.

## Evidence gates

| Gate | Evidence needed | Record or form | Current state |
| --- | --- | --- | --- |
| Framing and track | Verifiable context/decision, lenses and rationale, scope, success criteria, approval evidence | [Framing](../templates/problem-framing-canvas.md); [decisions](../project/decision-register.md) | Shared proposal direction present; decision context and approval pending |
| Data feasibility | Exact resources, permissions/terms, counts/coverage, candidate species/area, spatial-temporal-depth compatibility | [Manifest](../templates/data-source-record.md); [dictionary](../templates/data-dictionary.md) | Pending |
| Target and validation | Row meaning, positive/background definitions, sampling/bias rationale, splits, leakage controls, metrics | [Evaluation design](../templates/validation-and-evaluation-plan.md); [decisions](../project/decision-register.md) | Pending |
| Preparation and methods | Observed EDA, justified feature steps, baseline plus at least three alternatives, consistent comparison protocol | [EDA](../templates/eda-insight-log.md); [features](../templates/preprocessing-and-feature-decisions.md); [comparison](../templates/model-comparison.md) | Pending |
| Recommendation and handover | Evidence-linked value, uncertainty/domain limits, reproducible code/notebook, consistent report outputs and deliverables | [Recommendation](../templates/recommendations-and-limitations.md); [assessment checklist](../../PROJECT_REQUIREMENTS.md) | Pending |

Use evidence to revisit a gate when appropriate. Gate completion is a documented judgement, not a box inferred from a directory or blank form.

## Execution planning

The proposal leaves the runtime, environment manager, dependency versions, and execution entry points undecided. When these are selected, record the rationale and add reproducible instructions alongside the implementation. Do not introduce install commands that cannot yet run a project workflow.

No calendar deadline or member allocation is established here. Agree milestones against confirmed course dates and the approved scope; the Industry Explorer bonus requires manageable scope within seven weeks.

## Later BLUEVERSE handover

If the evaluated output is suitable for later integration, document its schema, geographic/environmental domain, target meaning, uncertainty, data-use conditions, and generation method. A reviewed analytical artefact is the proposed handover; operational deployment remains outside the current assignment scope.

Complete [model metadata](../templates/model-metadata.json) only for an actual trained artefact. Tie any acceptance claim to the dataset, reproducible environment, comparison protocol, evaluation evidence and limitations. A notebook or anonymous model file alone does not establish an accepted integration output.

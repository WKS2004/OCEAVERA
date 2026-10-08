# Analysis notebooks

**Current state:** no analysis notebook is required for the Area 230 intake.
The current acquisition is implemented in the two standard-library scripts in
`src/data_collection/` and recorded under D-036. The superseded AWS
GeoParquet feasibility notebook was removed when the user changed the intake
method back to the API.

Future notebooks should follow the [project workflow](../docs/ml/ml-workflow-and-evidence-gates.md), identify their input dataset versions and manifests, state row/target meaning, and produce outputs reproducibly in a documented environment. Keep validation boundaries explicit and remove credentials or sensitive payloads before sharing.

Use descriptive sequence/topic names when the workflow exists. Explain execution order and dependencies here at that time. Record observed findings in `docs/records/` following the [record conventions](../CONTRIBUTING.md#project-evidence-records); an exploratory notebook does not replace the required decision and insight logs.

## Member responsibilities

Notebook work follows the biological/target/baseline responsibilities of Sanuda, environmental/integration/feature responsibilities of Ushan, EDA/preprocessing/intermediate-model responsibilities of Adithya and training/evaluation responsibilities of Wanshaja. All four participate and review the complete pipeline. See the [complete responsibility plan](../docs/project/member-responsibilities.md) for all activities, shared roles and handovers. Planned ownership does not establish an artefact or completed contribution, and technical execution remains pending authorisation.

# Analysis notebooks

**Current state:** no analysis notebook is required for the Area 230 intake.
The current acquisition is implemented in the two standard-library scripts in
`src/data_collection/` and recorded under D-036. The superseded AWS
GeoParquet feasibility notebook was removed when the user changed the intake
method back to the API.

Future notebooks should follow the [project workflow](../docs/ml/ml-workflow-and-evidence-gates.md), identify their input dataset versions and manifests, state row/target meaning, and produce outputs reproducibly in a documented environment. Keep validation boundaries explicit and remove credentials or sensitive payloads before sharing.

For Python notebooks, declare every required third-party package with its
selected exact version in the root [`requirements.txt`](../requirements.txt).
From the repository root, install listed packages with
`python -m pip install -r requirements.txt`; update the manifest and notebook
setup instructions in the same change. See the
[contributor dependency policy](../CONTRIBUTING.md#python-dependencies).
The documented Python Conda environment is named `OCEAVERA` and uses the
Python 3.14 project baseline; use the [root setup instructions](../README.md#create-the-conda-environment)
when a Python notebook workflow is authorised. The ML framework and exact
package stack remain undecided.

Use descriptive sequence/topic names when the workflow exists. Explain execution order and dependencies here at that time. Record observed findings in `docs/records/` following the [record conventions](../CONTRIBUTING.md#project-evidence-records); an exploratory notebook does not replace the required decision and insight logs.

## Member responsibilities

Notebook work follows the biological/target/baseline responsibilities of Sanuda, environmental/integration/feature responsibilities of Ushan, EDA/preprocessing/intermediate-model responsibilities of Adithya and training/evaluation responsibilities of Wanshaja. All four participate and review the complete pipeline. See the [complete responsibility plan](../docs/project/member-responsibilities.md) for all activities, shared roles and handovers. Planned ownership does not establish an artefact or completed contribution, and technical execution remains pending authorisation.

# Notebooks

## Notebook types and current state

This directory holds two distinct kinds of notebook:

- **Branch work notebooks** record what a branch implements and documents when that branch is finalised. They are not personal contribution logs, assessed reflections, scientific source records or model evidence.
- **Analytical notebooks** support an authorised, reproducible scientific workflow. They identify their data and manifests, row and target meaning, environment, validation boundaries, generated outputs and limitations.

The branch work records are [pipeline_biological_data_collection.ipynb](branch_work/pipeline_biological_data_collection.ipynb) and [pipeline_environmental_data_collection.ipynb](branch_work/pipeline_environmental_data_collection.ipynb). The biological notebook documents the Area 230 API/CSV intake and read-only handoff under [D-036](../docs/records/2026-10-08-decision-obis-area-230-api-csv.md). The environmental notebook documents the D-047/D-048 Bio-ORACLE catalogue intake, fixed collection rectangle, raw payload and receipt audit, and D-038 source-validation handoff to the stable interim folder. Its offline Code cells read saved manifests, payloads and inventory without making API requests or writing dataset files; staged payload checksums are recorded in the handoff manifest and are not recalculated by the notebook. Both are branch-level implementation summaries, not personal contribution logs. No exploratory, cleaning, integration or modelling notebook is implemented.

## Branch work notebook convention

Create or update one branch work notebook as the final substantive artefact when the branch is being finalised, after its code, documentation and requested checks are complete. Store it at:

```text
notebooks/branch_work/<branch_name>.ipynb
```

Use the lowercase Git branch name in snake case: replace separators such as `/` and `-` with `_`. For example, `pipeline/biological-data-collection` becomes `pipeline_biological_data_collection.ipynb`.

Use this section order so a reader can understand each branch without relying on chat history:

1. **Title and top metadata:** the first native Markdown cell begins with the notebook title and gives project, branch name and review date. The following Markdown cell contains the contributor table with the exact columns Registration Number, Member Name and GitHub Account, using verified project identities; include a registration number only in this branch-notebook table under [D-042](../docs/records/2026-10-08-decision-branch-notebook-member-table.md). Do not include source-commit details, institutional identity forms, email addresses or other academic identifiers.
2. **Purpose and scope:** explain the work this branch addressed, what was in scope and what it deliberately did not implement.
3. **Data and provenance:** present the relevant source context, counts and provenance before the first Code cell. Use saved files read-only or make public API access an explicit opt-in that is disabled by default. Keep source and derived data in memory, use in-memory streams for demonstrations, and do not write notebook-generated dataset files. Do not embed raw payloads or full datasets.
4. **Branch result:** provide a concise map of the actual artefacts and workflow. Distinguish implementation from plans and human acceptance.
5. **Native Markdown and executable code:** use native Markdown cells for narrative and concise Python Code cells for operations. Put reader-facing context before code, divide operations into ordered steps and link to canonical source files. Use clear heading levels and concise, formal prose; keep headings, terminology and punctuation consistent, and remove redundant sections or repeated statements. Choose tables for metadata, counts and component maps, numbered steps for workflows, and bullets for scope or safeguards. Give table headers a clear visual hierarchy and leave enough horizontal padding between columns; use semantic HTML tables inside Markdown cells when precise header sizing and spacing are needed. Avoid blockquote callouts; use a short bold lead-in or a list instead. Format branch names and other identifiers as inline code. Show paths in Code-cell output and tracebacks relative to the repository root, using forward slashes where possible. Do not render prose from Python or place the complete workflow in one large cell.
6. **Environment and dependencies:** record the actual interpreter and packages used; update the root requirements manifest for every added or removed third-party dependency.
7. **Verification and limits:** execute every Python Code cell from top to bottom in the documented default mode and preserve concise outputs. Markdown cells render natively in Jupyter and are not Python code. List checks actually run, checks not run, remaining risks and scope boundaries. A successful execution or syntax check is not scientific validation or human acceptance.
8. **References and next-step context:** link decisions, requirements, readiness, relevant source and documentation, and identify the next authorised work without implying it is complete. Do not end the notebook with a separate Handover section.

Keep notebooks reproducible and reviewable: use valid notebook JSON, UTF-8 text, native Markdown cells for narrative and executable Python Code cells for operations, and no credentials or personal data beyond the explicitly permitted registration-number table field. Do not repeat registration numbers in AI logs, verification output or any other artefact. The default run must not make network requests; any API mode must require an explicit setting and must not write downloaded data or derived tables to disk. A local-file mode is read-only. Keep full payloads out of saved outputs. If a requested branch task authorises scientific analysis, document its actual run and provenance without confusing an illustrative fixture with observed data. Use canonical project documents for mutable facts; the notebook is an indexed branch overview, not a duplicate decision register.

## Analytical notebook practice

Future analytical notebooks should follow the [project workflow](../docs/ml/ml-workflow-and-evidence-gates.md), identify their input dataset versions and manifests, state row/target meaning, and produce outputs reproducibly in a documented environment. Keep validation boundaries explicit and remove credentials or sensitive payloads before sharing.

For Python notebooks, declare every required third-party package with its
selected exact version in the root [`requirements.txt`](../requirements.txt).
It currently pins `notebook` for the interface and `ipykernel` for a Python
execution kernel. Users may install listed packages from the repository root
with:

```text
python -m pip install -r requirements.txt
```

Update the manifest and notebook setup instructions in the same change. Agents
require explicit prior user authorisation before creating, modifying or
removing an environment or installing, upgrading or removing packages. The
documented Python Conda environment is named `OCEAVERA` and uses the Python
3.14 project baseline; see the [root user-led setup instructions](../README.md#create-the-conda-environment).
No Python environment is stored in this repository. Branch work notebooks use native Markdown cells for narrative and executable Python Code cells for operations. Run their Code cells in order and follow the user-led setup above. Their default path must not make network requests or persist dataset outputs. The ML framework and
scientific package stack remain undecided. See the [contributor
dependency policy](../CONTRIBUTING.md#python-dependencies).

Use descriptive sequence/topic names for analytical notebooks. Explain execution order and dependencies here when a workflow exists. Record scientific findings in `docs/records/` following the [record conventions](../CONTRIBUTING.md#project-evidence-records); an exploratory notebook does not replace required decision and insight logs.

## Member responsibilities

Notebook work follows the biological/target/baseline responsibilities of Sanuda, environmental/integration/feature responsibilities of Ushan, EDA/preprocessing/intermediate-model responsibilities of Adithya and training/evaluation responsibilities of Wanshaja. All four participate and review the complete pipeline. See the [complete responsibility plan](../docs/project/member-responsibilities.md) for all activities, shared roles and handovers. Planned ownership does not establish an artefact or completed contribution, and analytical execution remains subject to authorisation.

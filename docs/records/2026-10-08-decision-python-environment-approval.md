# Decision D-043: User authorisation for Python environment and package operations

- **ID:** D-043
- **Date:** 8 October 2026
- **Question:** When may an agent create or alter Python environments and install packages for OCEAVERA work?
- **Context:** The project baseline and package manifest are documented, but an agent may not have access to the user's preferred Python environment. Setup commands exist to support user-led setup and must not be treated as permission for an agent to run them.
- **Options considered:** Allow agents to create environments or install requirements whenever setup appears useful; require explicit user authorisation before each environment or package operation.
- **Evidence and source references:** Explicit user instruction on 8 October 2026; [contributor dependency policy](../../CONTRIBUTING.md#python-dependencies), root [agent instructions](../../AGENTS.md), and the [Python environment setup guide](../../README.md#create-the-conda-environment).
- **Decision:** Agents must obtain the user's explicit authorisation in the current task before creating, modifying or removing a Python environment, or installing, upgrading or removing Python packages. Commands in documentation are for user-led setup. Editing `requirements.txt` does not authorise installing its contents. Do not retain Python environment directories in the repository.
- **Rationale:** Preserve the user's control over environment changes and package installation, and avoid assumptions that a preferred local environment is available to an agent.
- **Consequences and limitations:** Keep the Python 3.14 project baseline, exact dependency pins and user-run setup instructions. No Python environment is stored in the repository. Do not document private machine configuration. Explicit authorisation applies to the actual requested operation; it does not imply permission for unrelated package or environment changes.
- **Status:** accepted
- **Affected documents and artefacts:** `AGENTS.md`, `.agents/rules/change-safety.md`, `.agents/README.md`, `.agents/repository-map.md`, `CONTRIBUTING.md`, `README.md`, `PROJECT_REQUIREMENTS.md`, `docs/README.md`, `docs/project/decision-register.md`, `docs/project/repository-readiness-and-alignment.md`, `docs/ml/ml-workflow-and-evidence-gates.md`, `data/README.md`, `src/README.md`, `notebooks/README.md` and the biological data collection branch notebook.
- **Supersedes / superseded by, if applicable:** None.

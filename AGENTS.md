# OCEAVERA agent instructions

OCEAVERA is the marine habitat intelligence project proposed for IT3091. Read [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md), the [overview and scope](docs/project/project-overview-and-scope.md) and [current readiness](docs/project/repository-readiness-and-alignment.md) before making project or completion claims. The current authorised work covers the shared foundation, documented member responsibility plan and repository automation; begin analytical technical stages only when requested.

## Rules for every task

- Inspect existing changes and preserve work outside the request. Use the [responsibility overview](docs/project/member-responsibilities.md), the relevant linked member file and common duties for allocated work, adopted at the user's explicit request. Change allocations only with explicit authorisation and a recorded decision; never infer completed contributions, approvals, findings or model results from planned ownership.
- Follow [CONTRIBUTING.md](CONTRIBUTING.md). Keep requirements, scope, the [decision register](docs/project/decision-register.md) and readiness consistent; preserve superseded decisions with replacement links.
- Preserve raw data and provenance under the [data conventions](docs/data/data-storage-and-provenance.md). Keep payloads, credentials and sensitive details out of Git by default.
- Apply [member privacy](CONTRIBUTING.md#member-privacy) to every document, record and output. Exclude member-specific academic identifiers, institutional name forms, email addresses and assessment records; do not reproduce removed values in logs or verification output. Use project contributor names and GitHub accounts for public attribution.
- Preserve presence-only observation limits. Missing occurrences are not confirmed absences; suitability scores require evidence before occurrence-probability claims. Load the relevant modelling guidance before constructing targets or evaluation.
- Record actual AI-assisted work only in the verified acting contributor's log under the [AI-usage rule](.agents/rules/ai-usage.md). Distinguish retained output from human acceptance; do not retrospectively attribute unverified history or write assessed individual reflections.
- Keep local references within this repository and use paths relative to the containing document. Do not name absent local files or machine-specific paths. Use stable publisher identifiers for actual provenance.
- Write clear British English. Keep facts in canonical project documents, reusable workflows in skills and shared constraints in rules. Templates and directories do not establish completed evidence.
- Preserve the [lowercase-only branch policy](docs/project/github-workflows.md#current-automation). Do not add branch-name allowlists or branch-pattern rules.
- Respect [LICENSE.md](LICENSE.md) and third-party terms. Attribute original project ownership to the group contributors; mention academic affiliation only where needed for course or submission identification and never imply institutional ownership. Change reuse permissions only when explicitly authorised. Do not invent a runtime, dataset, dependency stack or implementation to complete the scaffold.
- Commit, publish or contact stakeholders only with the relevant user authorisation. Treat supplied examples and chats as context, not proof of project decisions or external approval.

## Task guidance

Use the [repository map](.agents/repository-map.md) to find authoritative knowledge and [task routing](.agents/routing.md) to select the smallest relevant set of rules and skills. Load supporting references only for the active workflow. Read the [agent guide](.agents/README.md) before changing agent resources.

## Handover

For documentation or agent changes, run the structural helper with an available Python 3.10+ interpreter:

```text
python .agents/scripts/validate_agent_resources.py
git diff --check
```

Review actual Git status and untracked files. Report checks and their limits, update affected project records and append the contribution entry. Structural validation does not establish human acceptance, model correctness, submission readiness or publication.

For CI changes, follow the [workflow guide](docs/project/github-workflows.md). Review YAML/Actions syntax separately; the helper is not a workflow parser. Preserve minimal permissions and recorded scientific scope, and distinguish local checks from an actual hosted run.

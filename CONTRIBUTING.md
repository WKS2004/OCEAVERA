# Contributing to OCEAVERA

Use this guide for shared project changes, evidence collection and contribution recording. Read [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md), the [overview and scope](docs/project/project-overview-and-scope.md), [readiness](docs/project/repository-readiness-and-alignment.md) and [decision register](docs/project/decision-register.md) before changing project direction.

## Working scope

The current authorised work covers shared structure, planning, proposal-based member responsibility documentation and repository automation. Start an analytical technical stage only when requested and the corresponding [workflow gate](docs/ml/ml-workflow-and-evidence-gates.md) is addressed. Keep unresolved species, geography, target, features, methods, ML framework and experiment-environment choices provisional until recorded evidence supports them.

All members are expected to understand the full pipeline and contribute technically. Use the [responsibility overview](docs/project/member-responsibilities.md) for the group division, the linked member file for complete personal duties and the [common guide](docs/project/member-contributions/shared-responsibilities-and-evidence.md) for shared participation, evidence and handovers. Factual activity logs record performed work; they do not prove fulfilment of an allocation or satisfy a member's assessed learning report. Follow the finalised working allocation and record authorised responsibility changes in the decision register.

## Member handovers and review

Use the [complete allocation and handover requirements](docs/project/member-contributions/shared-responsibilities-and-evidence.md#handover-and-final-submission-duties). Primary members provide reproducible evidence and describe unresolved issues; recipients record actual support/review without automatic acceptance claims. Shared scientific choices require group evidence and recorded agreement status. Keep report/demo assembly shared unless an additional logistical role is explicitly agreed.

Document each member's actual authorship, support and review in the relevant scientific record or generating artefact when evidenced. Planned responsibility is not contribution credit. AI-assisted tasks additionally use the per-account recording convention below; do not create empty logs for planned members.

## Change workflow

1. Inspect the worktree and existing changes; preserve unrelated work.
2. Identify the requirement or project need, inspect the relevant knowledge and select applicable agent guidance when using an agent.
3. Make a focused change in the location described by the [documentation index](docs/README.md) or repository layout. Use descriptive filenames; avoid duplicate documents and empty implementations.
4. Record material decisions with options, rationale, evidence and consequences. Preserve superseded decisions and link their replacements.
5. Update affected links, indices, requirements and readiness together. Keep canonical documents authoritative rather than copying changing facts into multiple files.
6. Perform the relevant checks and record actual outcomes and limitations. Append meaningful AI-assisted activity to the verified acting contributor's log.

Commit or publish only when requested. Use focused, descriptive commits and stage only the intended files. Do not rewrite shared history during routine maintenance.

## Project evidence records

Store scientific, approval and detailed decision evidence in `docs/records/`. Copy the appropriate [blank template](docs/templates/README.md) when the underlying work is authorised; leave master templates blank.

- Name a record `YYYY-MM-DD-topic.md`, adding a stable decision or resource ID where useful.
- Start with date, status and purpose. Distinguish proposed choices, observations, accepted decisions and pending evidence.
- Identify dataset/resource versions and the notebook, code, configuration or output that generated each material finding. Link existing artefacts using repository-relative paths.
- For cleaning and exclusions, record the rule, affected count, reason and resulting dataset version. Preserve raw inputs.
- Link completed evidence from the [decision register](docs/project/decision-register.md) or [requirements](PROJECT_REQUIREMENTS.md), and update readiness when a gap is resolved.
- Preserve superseded evidence and its relationship to replacement records. Keep decisions, observations and contributor activity distinguishable.

The directory marker preserves the evidence location in Git and establishes no completed work. Consult [current readiness](docs/project/repository-readiness-and-alignment.md) for available scientific and approval evidence. Earlier documentation reviews remain in the [review history](docs/project/repository-review-history.md).

## Contribution and AI-usage recording

### Member privacy

Treat every member-specific academic detail as sensitive. Exclude student or registration identifiers, names formatted for institutional records, institutional email addresses, enrolment details, grades, individual assessment feedback and personal academic records from public repository content, including member profiles, logs, templates, attachments and generated outputs. The sole exception is a registration number in the contributor table of a branch work notebook under [D-042](docs/records/2026-10-08-decision-branch-notebook-member-table.md); it must not be copied into any other repository artefact, including activity logs or verification output. No other academic identifier or institutional identity form is permitted by this exception. Individual learning reports and supporting academic material belong in the authorised private submission process.

Use the project's [contributor names and GitHub accounts](docs/project/ai-team-members.md) for public attribution. Shared course and group metadata may identify the assignment; it must not expose a member's private academic record. When reading submission material, extract the required responsibilities and omit sensitive identity fields. Record a privacy correction without repeating the removed values, including in requests, examples or verification output.

### Activity entries

Use the exact account-to-name [contributor mapping](docs/project/ai-team-members.md). Resolve the acting account through authenticated GitHub evidence or the contributor's explicit statement; Git display names, email addresses and repository ownership alone are insufficient.

Append each meaningful AI-assisted task to `docs/ai-contribution/<Exact-GitHub-Username>-ai-usage.md`, using the ten fields in the [recording template](docs/project/ai-usage-log-template.md). The [documentation index](docs/README.md#contribution-records) links current logs. Create a contributor's log only when there is actual activity to record.

Record the client date/time and timezone, contributor identity, agent, tool/app, available model metadata, request, actions, retained/changed/rejected output and checks. State unavailable metadata, unrun checks and pending human review explicitly. Preserve chronological entries; correction-only requests transparently amend the relevant record rather than create a separate activity event.

Do not attribute earlier unidentified work to the current account, copy another project's activities, create empty member logs or infer human acceptance from retained worktree edits. Record actual human changes only when evidenced. Keep secrets, personal contact details and hidden reasoning out of records.

Factual logs support AI transparency and accountability. Each member remains responsible for their own assessed Personal Learning Journey.

## Data, artefacts and rights

Follow [data storage and provenance](docs/data/data-storage-and-provenance.md). Preserve original downloads, resource citations, access terms, queries, quality decisions and fingerprints. Keep payloads excluded from Git by default and inspect sharing permissions before deliberately including data or generated artefacts.

Every reported result must identify its dataset, generating work, configuration and decision context. Use relative-suitability language for presence/background outputs unless the observation and sampling design justify occurrence probabilities. Calibration against constructed labels alone is insufficient.

Follow the all-rights-reserved policy in [LICENSE.md](LICENSE.md). Original project ownership remains with the group contributors; academic affiliation must not be presented as institutional ownership. Include only material the contributor is entitled to submit and retain third-party notices and licence conditions. A contribution record does not transfer ownership or grant public reuse rights. Changes to the repository policy require explicit authorisation and a decision record.

## Python dependencies

Keep the root [`requirements.txt`](requirements.txt) as the single list of
third-party Python packages needed by project code, notebooks and required
tooling. Whenever a package is added, removed or changed, update this file and
the relevant setup instructions in the same change. Record the selected exact
package version using this requirement-line format:

```text
package==version
```

Do not list Python standard-library modules or add speculative packages for
unselected future work. Python 3.14 is
the project baseline in [`.python-version`](.python-version); the current
intake scripts remain compatible with Python 3.10 or later and need no
third-party packages. From the repository root, users may install listed
dependencies with:

```text
python -m pip install -r requirements.txt
```

For the current OBIS intake scripts and repository tooling, use the Conda
environment documented in the root [README](README.md#create-the-conda-environment):
users can create and activate it with:

```text
conda create --name OCEAVERA python=3.14 pip
conda activate OCEAVERA
```

The future ML framework and dependency stack remain open. The manifest pins
Jupyter Notebook and its Python kernel for notebook use; the OBIS intake scripts
themselves continue to use the standard library. These notebook tools do not
select the ML framework or scientific dependency stack.

Environment setup commands below and elsewhere in the repository are for
user-led setup. An agent must obtain the user's explicit authorisation in the
current task before creating, modifying or removing a Python environment, or
installing, upgrading or removing a package. Updating `requirements.txt` or
documenting a command is not permission to run it. Do not retain Python
environment directories in the repository; `.venv/` remains ignored.

## Documentation conventions

- Write clear, professional British English with meaningful headings and consistent terminology.
- Use relative Markdown links that resolve inside the repository. Do not name absent local artefacts or machine-specific paths.
- Attribute external facts using stable publisher URLs, DOIs or accession identifiers when needed.
- Use UTF-8 without a byte-order mark, LF line endings, a final newline and no trailing whitespace.
- Put complete commands and standalone source/configuration snippets in fenced code blocks so readers can copy them. Keep short identifiers, field names, paths, flags and placeholders inline when they are references rather than complete examples.
- Keep templates blank, activity logs factual and requirements separate from completion evidence.
- Finalise each branch with a branch work notebook under notebooks/branch_work/, named from its lowercase branch name in snake case. Follow the required sections in [notebooks/README.md](notebooks/README.md). Use native Markdown cells for the title, contributors, scope, data context and narrative; use concise executable Python Code cells for operations. Run Code cells in order and retain concise outputs. Use saved files read-only or an explicitly enabled API source; default execution must not access the network, and notebook data must remain in memory without writing dataset outputs. The notebook describes actual branch work and evidence, not an individual contribution claim or assessed reflection. Use a contributor table headed Registration Number, Member Name and GitHub Account; include a registration number only in that table under D-042. Use verified project names/accounts and omit institutional name forms, email addresses and all other academic identifiers.

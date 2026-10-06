# Contributing to OCEAVERA

Use this guide for shared project changes, evidence collection and contribution recording. Read [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md), the [overview and scope](docs/project/project-overview-and-scope.md), [readiness](docs/project/repository-readiness-and-alignment.md) and [decision register](docs/project/decision-register.md) before changing project direction.

## Working scope

The current authorised work covers shared structure, planning and proposal-based member responsibility documentation. Start a technical stage only when requested and the corresponding [workflow gate](docs/ml/ml-workflow-and-evidence-gates.md) is addressed. Keep unresolved species, geography, target, features, methods and environment choices provisional until recorded evidence supports them.

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

Treat every member-specific academic detail as sensitive. Exclude student or registration identifiers, names formatted for institutional records, institutional email addresses, enrolment details, grades, individual assessment feedback and personal academic records from public repository content, including member profiles, logs, templates, attachments and generated outputs. Individual learning reports and supporting academic material belong in the authorised private submission process.

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

## Documentation conventions

- Write clear, professional British English with meaningful headings and consistent terminology.
- Use relative Markdown links that resolve inside the repository. Do not name absent local artefacts or machine-specific paths.
- Attribute external facts using stable publisher URLs, DOIs or accession identifiers when needed.
- Use UTF-8 without a byte-order mark, LF line endings, a final newline and no trailing whitespace.
- Keep templates blank, activity logs factual and requirements separate from completion evidence.

## Review before handover

For documentation and agent-resource changes, run from the repository root with an available Python 3.10+ interpreter:

```text
python .agents/scripts/validate_agent_resources.py
git diff --check
git status --short
```

The helper checks maintained resource formats, routing, local files and section links, text conventions and contributor-record structure, including untracked text files. Follow the [agent guide](.agents/README.md) when changing the registry or generated routing.

Review agreement between requirements, scope, decisions and readiness. Check for accidental data, credentials, caches, missing references and unrelated edits. For future executable work, use the agreed environment and the checks required by the active request and workflow; report unrun checks honestly.

State what changed, what was checked and what remains unresolved. Structural checks establish repository consistency; scientific validity and submission readiness require the evidence in [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md).

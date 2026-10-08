# Agent resource guide

## Purpose and boundaries

The root [AGENTS.md](../AGENTS.md) contains the instructions that apply to every task. This directory holds task routing, focused constraints, reusable workflows and their structural checks. The [documentation index](../docs/README.md) remains the source of project knowledge; agent guidance does not establish data findings, approved scope or implementation completion.

## Choose the relevant guidance

1. Read root instructions and inspect current worktree changes.
2. Use the [repository map](repository-map.md) for the authoritative document or directory.
3. Select the relevant row in [task routing](routing.md). Load the base rules and only the conditional rules/skills needed for the task.
4. Read a skill's supporting references only for the active mode.
5. Record material decisions and evidence in project documentation and run applicable checks. Append actual AI assistance and outcomes to the verified acting contributor's log under the [recording rule](rules/ai-usage.md).

## Maintained resources

| Resource | Responsibility |
| --- | --- |
| [Repository map](repository-map.md) | Navigation to current project knowledge and implementation destinations |
| [Task routing](routing.md) | Generated task-to-skill/rule navigation |
| [Skill registry](registry/skills.json) | Project-owned inventory, trigger boundaries, rules and knowledge references |
| [Routing review cases](evals/routing-cases.json) | Human-readable tasks, expected guidance and unacceptable claims |
| [Validation helper](scripts/validate_agent_resources.py) | Deterministic inventory, metadata, routing, file/section links, formatting and contribution-record checks |

There are no vendored external skills. Future imports require an exact upstream revision, licence, compatibility review and a registry entry. Framework or deployment skills belong here only when the project actually adopts the relevant implementation surface.

The review cases are manual semantic expectations. The helper checks their references and coverage; it does not run an agent or prove behavioural compliance. Model correctness requires actual datasets and evaluation evidence.

## Contributor recording

The [contributor mapping](../docs/project/ai-team-members.md) is canonical. The [template](../docs/project/ai-usage-log-template.md) defines ten required fields, and the [log index](../docs/README.md#contribution-records) links actual contributor activity. The helper checks exact filename/account/name agreement, valid calendar dates, required fields and explicit timezone; it cannot authenticate identities, prove actions or establish human acceptance. Preserve those evidence limits in every entry.

## Validate and maintain

The repository helper requires Python 3.10 or later and only its standard library. This maintenance-tool requirement does not select the ML runtime or add modelling dependencies.

Run from the repository root with an available Python interpreter:

```text
python .agents/scripts/validate_agent_resources.py
```

When the registry changes, regenerate the routing view, then validate:

```text
python .agents/scripts/validate_agent_resources.py --write-routing
python .agents/scripts/validate_agent_resources.py
```

Section checks cover ATX Markdown headings, including repeated-heading suffixes; fenced code is excluded. They do not validate external URLs or the truth of a linked claim.

The helper checks the simple single-line frontmatter and quoted interface metadata used by the maintained skills. It is not a general YAML parser. It skips `data/raw/` payloads because source bytes must remain unchanged; tracked provenance and code remain subject to text-format checks. Extend the schema check before adopting more complex metadata; do not bypass a rejected format.

Keep rules as constraints, skills as workflows and project documents as knowledge. Avoid duplicate fact sheets, empty support directories or adapters for tools the group has not selected. Ordinary analytical work changes project evidence; guidance changes should be justified by a requested resource change or a demonstrated workflow gap.

## Member allocation guidance

The [member responsibility plan](../docs/project/member-responsibilities.md) is canonical for the explicitly requested proposal allocation. Read the overview, the relevant linked member file and common guide before member-specific work or contribution reporting. The overview holds the canonical group matrix; detailed files hold full individual activities; the common guide holds shared obligations. Follow the finalised working allocation while preserving its proposal provenance, recorded change control, joint ownership and shared decisions; document actual work separately. A responsibility update does not begin technical implementation or authorise assessed individual reflections.

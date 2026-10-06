# Validation and handover evidence

Apply before handing over a repository change.

| Changed surface | Relevant checks |
| --- | --- |
| Documents, root instructions, rules or skills | [Resource helper](../scripts/validate_agent_resources.py), local links, formatting and Git whitespace |
| Skill registry or routing | Registry completeness, regenerated routing view, case references and skill descriptions |
| Data conventions | Ignore boundaries, tracked metadata destinations and raw-payload preservation |
| Future executable ML work | Agreed environment, actual affected behaviour, dataset/target contracts and validation partitions |

Run narrow meaningful checks for the changed surface. The resource helper uses only the standard library and avoids the optional upstream validator dependency. Report what ran, failed or was unavailable; a static check is not model evaluation or human acceptance.

Review actual Git status and include untracked files in documentation checks. Do not infer a commit or publication from worktree presence. Manual routing scenarios remain unexecuted behavioural expectations unless an actual evaluation is recorded.

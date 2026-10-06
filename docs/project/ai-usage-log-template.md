# AI-usage recording template

Use this format for each meaningful AI-assisted repository contribution. Resolve the acting identity from the [contributor mapping](ai-team-members.md), then append the entry to that contributor's log in [AI contributions](../README.md#contribution-records). Keep this master template blank.

Create a log only when its contributor has actual activity to record. The filename is the exact GitHub username followed by `-ai-usage.md`. Do not create empty logs for other contributors or copy their work into the acting contributor's log.

## Entry template

Copy the following entry and replace each placeholder with factual information. Use the client date/time and timezone; do not infer task duration from a record timestamp.

```markdown
## YYYY-MM-DD — Task title

- **Date/time or time range:** [Actual date/time or verified interval, with timezone]
- **GitHub Username:** [Exact username from the mapping]
- **Team Member Name:** [Exact actual name from the mapping]
- **Agent Name:** [Agent assisting with this contribution]
- **Tool/App:** [Actual application or tool used]
- **AI Model:** [Visible model identifier, or explicitly unavailable]
- **Summary of the user's request:** [What the contributor requested]
- **Summary of what the AI Agent did:** [Actual work and affected repository artefacts]
- **AI output accepted/changed/rejected:** [What was retained, changed or rejected; state human review/acceptance separately]
- **Verification/evidence:** [Checks actually performed, their results/limits, identity source and relevant local links]
```

## Recording discipline

- Record meaningful work promptly after the relevant checks. A request to correct an existing record updates that record and is not itself a new contribution event.
- Describe actions rather than claiming ownership of the whole project. Distinguish AI assistance, the contributor's request, actual human changes and verified human review.
- Work retained in the worktree is not proof of human acceptance, a commit or publication. State pending review explicitly.
- State unavailable model metadata honestly. Do not guess a model from the product name.
- Preserve previous entries. Correct factual errors transparently when requested; do not rewrite history or retrospectively attribute older unverified work.
- Keep secrets, personal contact details, hidden reasoning and unsupported claims out of logs.
- Link scientific findings to their [evidence records](../../CONTRIBUTING.md#project-evidence-records). An activity log does not establish data quality, model correctness or assessment completion.
- Factual contribution logs support accountability; they do not replace a member's assessed Personal Learning Journey or authorise writing it on their behalf.

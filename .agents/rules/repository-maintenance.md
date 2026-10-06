# Repository maintenance rules

Apply when reviewing structure, documentation quality, requirement coverage or project status.

- Use the [overview and scope](../../docs/project/project-overview-and-scope.md), [assessment map](../../PROJECT_REQUIREMENTS.md), [decision register](../../docs/project/decision-register.md) and [status review](../../docs/project/repository-readiness-and-alignment.md) for their distinct purposes. Reconcile contradictions without inventing decisions or approvals.
- Preserve the shared planning boundary. Documentation improvement does not authorise acquisition, member analysis, model development or deployment.
- Keep local references inside the repository and make Markdown links relative to the containing file. Do not name absent local source artefacts or machine-specific paths.
- Separate planned support, actual evidence and final readiness. Blank templates, empty directories and candidate methods do not satisfy implementation evidence.
- Use directory READMEs where they add useful guidance; keep records under their central conventions and index rather than adding redundant READMEs. Keep templates blank and completed evidence in dated records. Update the index and affected requirement links when artefacts are added.
- Verify meaningful structural invariants: local links and routes resolve, references stay inside the repository, formatting is consistent, and ignore rules protect payloads while preserving metadata. Inspect Git status; untracked files are not committed evidence.
- Do not introduce a stack, CI configuration, fabricated outputs or member allocations to make the repository appear complete. Follow the user-selected policy in [LICENSE.md](../../LICENSE.md); change reuse rights only with explicit authorisation. Add implementation choices only when relevant work is authorised.

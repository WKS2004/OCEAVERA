# Task routing

Generated from the [skill registry](registry/skills.json). Change the registry and regenerate this view; project knowledge remains in documentation.

For every task, read [change scope](rules/change-safety.md), [validation](rules/validation.md) and [contributor recording](rules/ai-usage.md). Then select the matching workflow below. Load only supporting references needed for the active mode.

| Requested work | Workflow | Conditional rules |
| --- | --- | --- |
| Repository structure, documentation naming, readiness and agent-resource review | [Repository alignment](skills/repository-alignment/SKILL.md) | [repository maintenance](rules/repository-maintenance.md), [documentation](rules/documentation.md) |
| Stakeholder context, decision value, lenses, scope and approval evidence | [Industry Explorer framing](skills/industry-explorer-framing/SKILL.md) | [project scope](rules/project-scope.md), [assignment evidence](rules/assignment-evidence.md) |
| Source feasibility, species selection, acquisition, quality and spatial integration | [Marine data intake](skills/marine-data-intake/SKILL.md) | [data management](rules/data-management.md) |
| Data exploration, cleaning, preprocessing and environmental feature decisions | [Marine EDA and features](skills/marine-eda-and-features/SKILL.md) | [data management](rules/data-management.md), [eda and preprocessing](rules/eda-and-preprocessing.md) |
| Presence/background target construction, sampling domain and observation bias | [Marine background sampling](skills/marine-background-sampling/SKILL.md) | [data management](rules/data-management.md), [modelling and evaluation](rules/modelling-and-evaluation.md) |
| Spatial partitions, repeated grid cells, leakage and generalisation design | [Marine spatial validation](skills/marine-spatial-validation/SKILL.md) | [modelling and evaluation](rules/modelling-and-evaluation.md), [eda and preprocessing](rules/eda-and-preprocessing.md) |
| Baseline and alternative models, comparable evaluation and suitability interpretation | [Species distribution modelling](skills/species-distribution-modelling/SKILL.md) | [modelling and evaluation](rules/modelling-and-evaluation.md) |
| Assessment evidence, report traceability, AI-use disclosure and submission readiness | [IT3091 evidence](skills/it3091-evidence/SKILL.md) | [assignment evidence](rules/assignment-evidence.md), [documentation](rules/documentation.md) |

Cross-cutting work may need more than one workflow: target sampling and spatial partitions should agree, data preparation and feature choices should respect validation, and assessment reporting should link actual technical evidence.

This map selects guidance; it does not authorise a technical stage or establish that implementation exists. Consult the [repository map](repository-map.md) and current readiness before making completion claims.

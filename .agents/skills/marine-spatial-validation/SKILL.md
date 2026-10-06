---
name: marine-spatial-validation
description: Design or audit OCEAVERA spatial evaluation folds, shared-grid-cell grouping, leakage controls and geographic generalisation claims.
---

# Marine spatial validation

Read the [modelling rule](../../rules/modelling-and-evaluation.md) and [partition reference](references/partition-design.md). Use for partition changes or spatial leakage reviews.

1. State the generalisation question and the actual geographic, temporal and environmental domain.
2. Inspect repeated locations, environmental-cell identity, sample concentration and dependence relevant to that question.
3. Compare defensible geographic/group partitions, document practical constraints and preserve class/sample feasibility within folds.
4. Keep learned preparation, feature selection and tuning inside training folds. Distinguish deterministic covariate extraction from target-guided design choices.
5. Record split membership/configuration, metric rationale and held-out isolation in a dated [validation plan](../../../docs/templates/validation-and-evaluation-plan.md). Link the [decision register](../../../docs/project/decision-register.md).
6. Report fold variation and domain limits from actual results. A random-split comparison may be informative but is not automatically proof of spatial transfer.

Return a justified protocol or evidence-backed leakage review. Do not invent fold counts, separation distances or performance results.

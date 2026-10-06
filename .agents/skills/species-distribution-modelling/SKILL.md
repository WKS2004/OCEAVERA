---
name: species-distribution-modelling
description: Design or evaluate OCEAVERA species targets, background sampling, spatial validation, model comparisons and suitability interpretation.
---

# Species distribution modelling

Read the [modelling rule](../../rules/modelling-and-evaluation.md). Confirm actual row meaning, occurrence definition, sampling domain and intended use.

1. Compare defensible background/pseudo-absence schemes, observation-bias controls and their effect on target meaning. Missing records are not confirmed absence.
2. Document the split, leakage controls, metrics and selection protocol in a dated [evaluation-design](../../../docs/templates/validation-and-evaluation-plan.md) record before model comparison.
3. Fit a simple baseline and at least three justified alternatives under comparable validation. Fit learned preprocessing and tuning within training partitions; retain held-out evaluation.
4. Assess discrimination, relevant uncertainty, error patterns and calibration. Do not equate calibration against constructed background labels with true occurrence probability.
5. Capture actual results in a dated [comparison](../../../docs/templates/model-comparison.md) record and update the [decision register](../../../docs/project/decision-register.md).
6. Prepare suitability outputs only where supported; state spatial/environmental domain, extrapolation, uncertainty and predictive-association limits before recommending use.

Return the justified design or measured comparison and its interpretation limits. Do not select final algorithms or thresholds before the data and target support them.

## Focused design workflows

Use [background sampling](../marine-background-sampling/SKILL.md) when changing the constructed comparison or target semantics, and [spatial validation](../marine-spatial-validation/SKILL.md) when defining partitions or reviewing geographic leakage. Keep this workflow focused on comparable methods and supported interpretation.

## Reproducible artefact handover

For an actual trained model, complete the [model metadata](../../../docs/templates/model-metadata.json) with dataset/run identity, features, environment, configuration, metrics with partition IDs, limits and content fingerprint. Any later BLUEVERSE handover requires recorded acceptance evidence; it does not authorise deployment or treat a notebook as an accepted model.

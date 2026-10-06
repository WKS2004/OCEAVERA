# Species-distribution modelling rules

Apply when constructing targets/backgrounds, designing validation, comparing methods or interpreting outputs. Consult the [evaluation form](../../docs/templates/validation-and-evaluation-plan.md) and [comparison form](../../docs/templates/model-comparison.md).

- Missing occurrence records are not confirmed absences. Define observed presence and constructed comparison rows, sampling domain, observation-bias considerations and sensitivity to plausible background schemes.
- Presence/background classifier scores depend on sampling and observation processes. Calibration against constructed labels alone does not justify true occurrence probability; use relative suitability unless stronger interpretation is supported.
- Partition before fitting learned preprocessing, feature selection or tuning. Address repeated locations, neighbouring samples and spatial groups that could make evaluation optimistic. Deterministic extraction of independently published covariates is not itself learned preprocessing; target-guided layer choices must respect partitions.
- Consider spatially separated validation and justify the actual split against the generalisation question. State any limitation of random splitting.
- Use a sensible baseline and at least three justified alternatives under a comparable protocol. Select metrics from target, imbalance and decision context; do not rely on accuracy alone.
- Separate validation-led selection from held-out evaluation. Do not repeatedly tune on test outcomes; document design revisions and retain an honest evaluation boundary.
- Report error patterns, uncertainty, domain limits, extrapolation and calibration where appropriate. Associations do not establish ecological causation.
- Record final target, sampling, split, features, metrics and methods in the [decision register](../../docs/project/decision-register.md), with linked evidence.

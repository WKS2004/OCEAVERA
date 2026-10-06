# EDA and preprocessing rules

Apply when exploring data or choosing cleaning, transformations or features. Use the [EDA log](../../docs/templates/eda-insight-log.md) and [feature log](../../docs/templates/preprocessing-and-feature-decisions.md) as blank forms for dated records.

- Establish dataset version, row/target meaning, geographic/time/depth domain, units and coverage before interpreting summaries.
- Record counts through material filters. Investigate taxonomy, coordinate validity, repeats, missingness, extraction failures, sampling concentration, class construction and environmental distributions.
- Separate non-outcome quality checks from exploration that informs feature or model choices. Keep outcome-guided exploration within training partitions and fit learned transformations there.
- Explain exclusions, imputation, scaling, encoding, imbalance treatment and derived features from evidence. Compare alternatives when choices could materially affect evaluation.
- Consider ecological relevance and model behaviour when assessing redundancy; correlation alone does not require feature removal. Rare observations are not automatically errors.
- Preserve raw inputs, regenerate derived data, and update the dictionary and logs. Interpret associations without claiming ecological causation.

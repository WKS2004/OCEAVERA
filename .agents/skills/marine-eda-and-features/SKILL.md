---
name: marine-eda-and-features
description: Explore OCEAVERA marine data quality and justify cleaning, preprocessing and environmental features. Use for EDA and feature decisions on actual datasets.
---

# Marine EDA and features

Read the [EDA rule](../../rules/eda-and-preprocessing.md) and relevant [data rule](../../rules/data-management.md).

1. Confirm dataset version, row/target meaning, sampling domain, units and validation boundaries. Inspect quality and coverage before transforming records.
2. Explore relevant distributions, missingness, spatial concentration, class construction and environmental relationships. Keep outcome-guided exploration within training partitions.
3. Record observations and decision implications in a dated copy of the [EDA log](../../../docs/templates/eda-insight-log.md).
4. Justify material exclusions, imputations, scaling, encoding, imbalance treatment and feature derivation against evidence and plausible alternatives. Fit learned steps on training data only.
5. Update dated [feature-log](../../../docs/templates/preprocessing-and-feature-decisions.md) and [dictionary](../../../docs/templates/data-dictionary.md) records, linking generating artefacts and changed decisions.

Return observed findings, justified preparation choices and unresolved quality/interpretation limits. Preserve raw inputs and avoid ecological-causation claims.

# Partition design review

Read when selecting or reviewing evaluation partitions.

- Define the intended use: interpolation within sampled environments, geographic transfer or another explicit question. The split should test that question.
- Preserve point and environmental-grid identities so repeated or equivalent rows can be grouped appropriately. Distinct coordinates do not guarantee independent environmental observations.
- Review spatial blocks, grouped locations and temporal separation where relevant. Choose sizes and grouping from actual data and the prediction domain; no fixed distance or fold count is required by this guidance.
- Record fold membership, sample/class counts, configuration and random seeds where used. Explain unusable folds or reduced coverage rather than silently dropping them.
- Fit learned imputation, scaling, feature selection, imbalance treatment and tuning within training partitions. Covariate extraction from independent published layers can be deterministic; choices informed by target outcomes require partition discipline.
- Preserve a held-out assessment after design changes. Repeatedly choosing methods from test outcomes compromises the final estimate.
- Interpret discrimination against constructed background labels under that design. Report spatial variation, environmental extrapolation and geographic limitations rather than treating one aggregate score as universal validity.

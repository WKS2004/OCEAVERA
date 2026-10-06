# Data management rules

Apply when assessing, acquiring, cleaning, integrating or sharing data. Follow [data governance](../../docs/data/data-storage-and-provenance.md).

- Consult authoritative publisher documentation at acquisition time. Capture the exact resource/layer, stable identifier, release, filters/query, retrieval date, citation, terms, coverage and content fingerprint where practical.
- Preserve original payloads in the raw data directory. Keep tracked manifests and dictionaries in [records](../../CONTRIBUTING.md#project-evidence-records), outside ignored data directories.
- Record transformations, exclusions, joins, before/after counts and generating artefacts. Distinguish observations, constructed target labels and model outputs.
- Assess taxonomy, coordinates, dates, repeats/duplicates, depth and sampling concentration from actual data before asserting feasibility or coverage.
- Align coordinate systems, resolution, marine mask, units, temporal statistic/period and depth context. Document extraction rules, unmatched/coastal cells and approximations; a climatology is not a contemporaneous observation.
- Review terms, attribution, permissions and ecological sensitivity before redistribution. Keep tokens and unrelated personal data out of records.
- OBIS/Bio-ORACLE are proposed core sources. OBIStherm is supporting only if justified. Candidate status is not proof of access or compatibility.

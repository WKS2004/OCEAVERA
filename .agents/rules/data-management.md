# Data management rules

Apply when assessing, acquiring, cleaning, integrating or sharing data. Follow [data governance](../../docs/data/data-storage-and-provenance.md).

- Consult authoritative publisher documentation at acquisition time. Capture the exact resource/layer, stable identifier, release, filters/query, retrieval date, citation, terms, coverage and content fingerprint where practical.
- Preserve each original payload unchanged in its publisher-delivered format. Follow the [storage-format convention](../../docs/data/data-storage-and-provenance.md#storage-choices-by-role): use GeoParquet for compatible derived spatial tables, Parquet for compatible non-spatial ML tables, and keep full environmental arrays in their source format rather than flattening whole rasters. Record the actual source and derived formats; examples do not establish a resource's packaging.
- Keep tracked manifests and dictionaries in `docs/records/` under the [record conventions](../../CONTRIBUTING.md#project-evidence-records), outside ignored data directories.
- Record transformations, exclusions, joins, before/after counts and generating artefacts. Distinguish observations, constructed target labels and model outputs.
- Assess taxonomy, coordinates, dates, repeats/duplicates, depth and sampling concentration from actual data before asserting feasibility or coverage.
- Align coordinate systems, resolution, marine mask, units, temporal statistic/period and depth context. Document extraction rules, unmatched/coastal cells and approximations; a climatology is not a contemporaneous observation.
- Review terms, attribution, permissions and ecological sensitivity before redistribution. Keep tokens and unrelated personal data out of records.
- Record the actual dataset/model artefact format in its manifest or metadata. Joblib is only conditional on a selected compatible model framework and must never be loaded from an untrusted source. COG and ONNX remain optional, unfinalised BLUEVERSE integration suggestions; do not make them OCEAVERA deliverables or dependencies.
- OBIS/Bio-ORACLE are proposed core sources. OBIStherm is supporting only if justified. Candidate status is not proof of access or compatibility.

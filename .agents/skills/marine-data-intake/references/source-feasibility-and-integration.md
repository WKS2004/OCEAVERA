# Source feasibility and integration review

Read when comparing resources, selecting a focal species or proposing an extraction method.

## Occurrence resources

Record the exact query/snapshot, taxonomic identity, contributing dataset identifiers, retrieval date, licence/citation requirements and quality filters. Retain underlying dataset provenance where records combine multiple contributors. Do not replace a verifiable resource record with an unexplained training-table filename.

Measure occurrence quantity, spatial spread, dates, coordinate quality, repeats and taxonomic consistency. Species feasibility depends on coverage, ecology and environmental compatibility as well as count. Published area-wide totals do not establish usable records for a focal species.

## Environmental resources

Check exact release/layer, units, coordinate system, resolution, temporal period/statistic, depth stratum, marine mask and no-data conventions against authoritative documentation at acquisition time. Do not copy layer specifications or availability claims from a discussion as current verified facts.

Assess surface/benthic suitability against the species' ecology. Historical observations matched to climatologies need a documented approximation. Record grid-cell identity where many points share environmental values, extraction rules, unmatched points and before/after counts.

## Feasibility outcome

Compare candidate species/boundaries/layers using measured evidence. Record the reasons for selection or rejection, unresolved approximations and permitted use. No fixed minimum record count, source version or join method is chosen by this reference.

For an acquired integrated dataset, complete the [machine-readable manifest](../../../../docs/templates/dataset-manifest.json), retaining source identities and the generating configuration.

## Format and storage

Preserve original resource files in the format actually supplied and record that format in the source manifest. CSV for occurrence downloads and NetCDF for environmental arrays are anticipated examples only; verify the selected resource packaging. Keep full multidimensional rasters in their source format and store extracted predictor values in derived tables. Prefer GeoParquet for compatible spatial tables and Parquet for compatible non-spatial modelling tables, recording the actual format/specification version and any justified exception. Do not introduce COG or ONNX into the OCEAVERA data workflow; both are optional, unfinalised suggestions for a later BLUEVERSE integration only. Follow [data storage and provenance](../../../../docs/data/data-storage-and-provenance.md) for the complete format and integration boundaries.

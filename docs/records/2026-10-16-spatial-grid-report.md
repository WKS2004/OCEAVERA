# Policy B marine filtering and spatial grid report

The current outputs are **water-centre candidates**, not proof that every positional-uncertainty footprint is marine. Policy B excludes invalid points/flags, exact `ON_LAND` and `MARINE_UNSURE` flags, and points outside the GSHHG water polygon. It retains qualifying points regardless of uncertainty footprint and records that uncertainty for sensitivity review.

- Policy B water-centre observations retained: **2,353**
- Known footprints fully inside water: **709**
- Known footprints crossing land/coast: **1,025**
- Known footprints extending beyond reference: **29**
- Unknown or invalid uncertainty: **590**
- Individual observations in the grid file: **2,353**
- Identifier-bearing species-rank records: **2,009**
- Distinct occupied cells: **362**
- Species/cell/period summary rows: **1,389**
- Marine source: GSHHG 2.3.7, Wessel and Smith; DOI 10.1029/96JB00104; full-resolution coastline; D-048 collection envelope

Counts are occurrence records, not animal abundance. Bio-ORACLE extraction success does not independently establish marine location. No species selection, feature selection, target creation, background sampling or model training is performed.

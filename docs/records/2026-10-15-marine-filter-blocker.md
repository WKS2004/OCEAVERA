# Marine filtering and grid-summary blocker

**Status: BLOCKED** — 9,681 temporally eligible point records await an independently verified marine-area source.

No local publisher-identified water polygon or independently validated land-sea mask was present. Bio-ORACLE's rectangular collection envelope, source marine flag, raster cell footprint, and terrain coastline/landmass layers are not accepted as independent proof that an observation is marine.

The collection rectangle and raster values do not distinguish all marine points from land points. The OBIS `marine` field can contradict that evidence and is not used alone. No marine or gridded output was published.

Next input: A versioned, documented polygon layer explicitly representing marine areas, with its publisher, identifier, licence, retrieval date, CRS and geographic scope recorded. The pipeline accepts it only through --marine-mask and --marine-source.

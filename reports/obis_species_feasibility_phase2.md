# OCEAVERA — Phase 2: Species and Environmental Feasibility Verification

**Audit date:** 10 October 2026
**Branch:** `pipeline/data-cleaning-obis`
**Status:** Evidence for a project decision; no focal species is approved.
**Scope:** Read-only analysis of the saved OBIS Area 230 occurrence snapshot and all locally downloaded Bio-ORACLE NetCDF files. No models were trained, pseudo-absences generated, raw or interim datasets modified, or existing source code changed. A temporary in-memory NetCDF reader was removed after analysis; no package or environment operation was performed.

## 1. Decision summary

**No candidate has sufficient evidence to proceed directly to background sampling or ML dataset construction.** Stenella longirostris remains the best candidate for another targeted QA decision, with Acanthurus lineatus a secondary candidate if reef-scale habitat data and more spatially distributed observations can be added. Those are conditional candidates, not approvals.

The taxonomy gap is real but cannot be closed by filling every missing `taxonRank`: **7,548 rows across 2,479 species/ID pairs** have both `species` and `speciesid` populated while `taxonRank` is blank. Identifier agreement helps triage the gap, but rank must be checked taxon by taxon. Exact, current taxonomic evidence supports restoring 3 Stenella rows and 14 Acanthurus rows to the Phase 1 counts. The 208 blank-rank Penaeus rows remain unresolved; even its 3 explicit-rank rows have a current identifier conflict.

All 356 local NetCDF files have a common 0.05° WGS84 grid. The selected surface temperature, salinity, chlorophyll, terrain and bathymetry layers share a 24,503-cell non-fill marine mask in the crop, and those three environmental variables have no additional missing cells in that mask. However, the crop is a rectangle based on EEZ extrema, not an EEZ or study-domain polygon. Nearest-cell matches do not confirm that the original occurrence coordinate is at sea.

## 2. Data and method

The occurrence input is the saved OBIS Area 230 snapshot, 23,934 rows × 230 columns, retrieved 8 October 2026. Its acquisition and fingerprint are documented in the tracked [Area 230 source record](../docs/records/2026-10-08-source-obis-area-230-api-csv.md); the earlier [Phase 1 audit](obis_species_feasibility.md) describes the source-validation check.

For the candidate comparisons, the common record screen is: `dropped=false`; `absence=false`; exact case-insensitive `marine=true`; finite legal coordinates; and no `NO_MATCH`, `NO_ACCEPTED_NAME`, `WORMS_ANNOTATION_REJECT_AMBIGUOUS`, or `WORMS_ANNOTATION_UNRESOLVABLE` flag. The strict taxonomy pass requires `taxonRank` species/subspecies plus populated `species` and `speciesid`. A blank rank is restored only when the local AphiaID and scientific-name LSID agree exactly with the species ID and the current authoritative taxon record confirms species rank. No `NO_DEPTH`, `ON_LAND`, missing-uncertainty, repeated-coordinate or repeated-cell rule is applied to the base taxon counts.

Each coordinate was assigned to its nearest raster-cell centre on the saved axes. A point was called a **valid marine raster match** only when the matched cell is non-fill in `landmass`, `bathymetry_mean`, `thetao_mean`, `so_mean` and `chl_mean` at both baseline time coordinates. This is a grid match, not a coast-corrected coordinate or a final domain test. Cell counts are occupancy counts, not independent samples.

The positional sensitivity rule retains a record only when numeric `coordinateUncertaintyInMeters` is at or below the stated radius. Missing values are excluded from every threshold and reported separately; they are never treated as accurate. Reported radii of 1, 5, 10, 25, 50 and 100 km span strict accuracy to broad stress checks. A 0.05° cell is about 5.6 km north-south and about 5.5 km east-west near Sri Lanka.

## 3. Taxonomic screening verification

### Dataset-wide rank gap

Among 17,510 rows with both `species` and `speciesid`, 7,548 have blank `taxonRank`, covering 2,479 name/ID pairs. Of those blank-rank rows, 7,459 have `AphiaID == speciesid`; 5,160 also have an exact WoRMS scientific-name LSID ending in that ID; 89 have neither identifier match. These are useful triage counts, **not** proof that all 2,479 pairs are species-level. OBIS documents `taxonRank`, `species`, `AphiaID` and the marine-environment flags as WoRMS-derived or WoRMS-matched fields, so the current rank and identifier must be checked for each candidate rather than inferred from a filled `species` field alone. [OBIS data field definitions](https://portal.obis.org/data/access/), [OBIS taxonomic-backbone description](https://obis.org/sources/worms/).

### Candidate count changes

Counts below use the common row screen above. “Phase 1 strict” is the earlier explicit-rank result. “Revised verified” adds only the rank-gap records whose IDs and current species rank are corroborated.

| Candidate | Phase 1 strict | Verified rank-gap additions | Revised taxonomically verified | Taxonomic evidence |
|---|---:|---:|---:|---|
| *Stenella longirostris* | 105 | 3 | **108** | All 108 rows use species/AphiaID 137109 and the matching WoRMS LSID. Current OBIS taxon page identifies 137109 as Species. |
| *Lepidochelys olivacea* | 107 | 0 | **107** | All rows have explicit species rank and matching AphiaID/LSID 220293. |
| *Chelonia mydas* | 183 | 0 | **183** | All rows have explicit species rank and matching AphiaID/LSID 137206. |
| *Acanthurus lineatus* | 75 | 14 | **89** | All 14 blank-rank rows have species/AphiaID 159582 and matching WoRMS LSID. Current WoRMS page confirms accepted species rank. |
| *Stomopneustes variolaris* | 69 | 0 | **69** | All rows say species rank and AphiaID 212440; 63 carry the matching LSID and six omit `scientificNameID`. Current WoRMS taxon record confirms the named species. |
| *Penaeus (Fenneropenaeus) indicus* | 3 | 0 | **0 reconciled** | 208/211 rows have blank rank and no LSID. The three explicit species-rank rows use ID/LSID 1809203. Current OBIS lists accepted *Penaeus (Fenneropenaeus) indicus* under WoRMS 377434. The discrepancy is unresolved, so none are counted as taxonomically reconciled. |

The rank-gap recovery for Stenella and Acanthurus is justified by concordant identifiers plus current species-level records, not by the fact that `species` is filled. Their totals rise by 3 and 14 respectively. Conversely, do not restore the 208 Penaeus records on the available evidence. OBIS currently lists the accepted name under WoRMS/AphiaID 377434, whereas this snapshot’s 211 rows use 1809203; 208 lack the source LSID, and the other three repeat 1809203. This could be stale or mismatched lineage metadata, but it has not been resolved against a live record for 1809203. [Current OBIS Penaeus taxon page](https://obis.org/taxon/377434).

## 4. Marine filtering logic

The raw snapshot contains 23,204 `marine=true`, 219 `marine=false` and 511 blank `marine` values. In the historical row-cleaning pass, filters were applied in this order: `dropped=false`, then `absence=false`, then remove only `marine=false`. That left 23,217 rows: 23,165 with `marine=true` and 52 with blank `marine`. The Phase 1 candidate screen was stricter: it required exact, case-insensitive `marine=true`, so blank marine values did not enter the species counts.

This historical row-filter result is not the current cleaner output. The current [`clean_obis_occurrences_csv.py`](../src/data_preparation/clean_obis_occurrences_csv.py) is the later column-completeness step: it preserves every source row and retains columns with at least 90% non-empty values. Its recorded result is 23,934 rows and 22 of 230 columns. It does not apply the historical row filters above. The Phase 2 candidate counts were recomputed from the saved raw snapshot using the explicit row screen in §2, not from the 22-column interim table.

`marine` is an OBIS/WoRMS **taxon-environment flag**, not a point-in-water check. OBIS separately defines `shoredistance` (negative means inland) and quality flags. Consequently, `marine=true` cannot establish that a coordinate is ocean, coastal, a nesting beach, or suitable for a marine raster cell. [OBIS field definitions](https://portal.obis.org/data/access/).

## 5. Bio-ORACLE NetCDF inspection

All 356 NetCDF payloads were read in memory using the available bundled Python runtime and a temporary standard-library reader for the classic NetCDF CDF-1 format. The pass covered 2,392 data variables; no data were exported or changed.

| Check | Result |
|---|---|
| File/grid format | All 356 are classic NetCDF CDF-1 and share the same axes. |
| Grid | 178 latitude × 165 longitude cells; latitude centres 2.575–11.425°N and longitude centres 77.025–85.225°E; 0.05° spacing; WGS84/EPSG:4326. |
| Crop | 29,370 total grid cells. The crop is a rectangle made from Sri Lanka EEZ extrema, not the irregular EEZ or an approved modelling boundary. |
| Time groups | 55 baseline products use coordinates 2000 and 2010; 300 future products use 2020, 2030, …, 2090; one terrain file is static with a 1970 time coordinate. No future slice is labelled 2100 even though the future dataset names span 2020–2100. |
| Fill value | All 2,392 variables use `_FillValue=-9999.9`. Most climate variables have 24,503 valid cells per time step (83.43% of the crop). One `kdpar_mean_range` baseline variable has one additional missing value; the static `coastline` variable is a narrow layer with 486 valid cells. |
| Selected terrain mask | `landmass` is 1.0 and `bathymetry_mean` is non-fill on 24,503 cells; the remaining crop cells are fill. `bathymetry_mean` ranges −4,545.944 to 0 m; 37 valid cells are 0 m. Inland spot-check coordinates are fill. This is an empirical data mask, not an independent marine polygon. |
| Selected baseline fields | `thetao_mean` (°C), `so_mean` (PSU) and `chl_mean` (mg m⁻³) each have exactly 24,503 valid cells at both time coordinates, identical to the terrain mask. Their value ranges are 27.49–29.42°C, 32.23–34.81 PSU and 0.110–1.081 mg m⁻³ respectively. |

The selected temperature and salinity files are labelled baseline 2000–2019; the chlorophyll file is labelled 2000–2018. The actual stored coordinates are 2000 and 2010, not annual observations. Do not infer a finer averaging window from those two coordinate labels alone. The inspected regional collection and its provenance are documented in the tracked [Bio-ORACLE source record](../docs/records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md); relevant layers include `thetao_baseline_2000_2019_depthsurf`, `so_baseline_2000_2019_depthsurf`, `chl_baseline_2000_2018_depthsurf`, and `terrain_characteristics`. Bio-ORACLE documents a 0.05° marine grid and decadal layers, but the local time coordinates and masks above were measured from the downloaded files. [Bio-ORACLE documentation](https://www.bio-oracle.org/documentation.php).

All candidate coordinates fall within this raster crop. Selected predictors are available for every cell classified as valid marine under the empirical mask. This establishes technical extractability only. The three selected environmental layers are surface layers; they do not directly characterize exposed reef structure, intertidal pools, turtle nesting beaches, or the full vertical habitat of a species. Occurrence dates across 1758–2026 also do not align automatically with one static or two-coordinate climatological baseline.

## 6. Candidate marine-cell and uncertainty comparison

“Valid marine observations” below means the original coordinate’s nearest centre has a non-fill cell in the selected terrain and predictor masks. It does not mean the original point is confirmed at sea. Approximate geographic spans use only records with a valid raster match. The top-five-cell share counts the percentage of valid raster-matched records in the five most occupied cells.

| Rank | Candidate | Taxonomically verified rows | Valid raster-matched observations / cells | Approx. N–S × E–W span | Source concentration; top-five cell share |
|---:|---|---:|---:|---:|---|
| 1 | *Stenella longirostris* | 108 | **102 / 34** | 590 × 331 km | 104/108 are iNaturalist; 4 dataset IDs overall; top five cells contain 63% of valid matches. |
| 2 | *Acanthurus lineatus* | 89 | **80 / 14** | 317 × 183 km | 73/89 are iNaturalist; 7 dataset IDs overall; top five cells contain 83%. |
| 3 | *Stomopneustes variolaris* | 69 | **46 / 16** | 141 × 176 km | 63/69 are iNaturalist; 6 additional records are preserved specimens; top five cells contain 67%. |
| 4 | *Chelonia mydas* | 183 | **119 / 65** | 668 × 774 km | 169/183 are iNaturalist; 14 are machine/telemetry records; top five cells contain 21%. |
| 5 | *Lepidochelys olivacea* | 107 | **82 / 60** | 779 × 773 km | 76/107 are iNaturalist; 31 are machine/telemetry records; top five cells contain 18%. |
| 6 | *Penaeus (Fenneropenaeus) indicus* | **0 reconciled** | Not counted | — | 211 source rows, but the identifier conflict and rank gap prevent a verified focal-species count. Only 2 of the 3 explicit-rank rows map to valid raster cells, as a diagnostic only. |

The precision sensitivity table reports **retained records / valid marine raster matches / occupied valid marine cells**. Missing uncertainty is excluded from each threshold and shown separately.

| Candidate | Missing uncertainty | ≤1 km | ≤5 km | ≤10 km | ≤25 km | ≤50 km | ≤100 km |
|---|---:|---:|---:|---:|---:|---:|---:|
| *Stenella longirostris* | 16 | 29 / 27 / 12 | 62 / 60 / 19 | 70 / 67 / 21 | 79 / 75 / 23 | 88 / 83 / 27 | 91 / 85 / 29 |
| *Acanthurus lineatus* | 23 | 54 / 51 / 7 | 62 / 56 / 8 | 63 / 57 / 8 | 63 / 57 / 8 | 66 / 59 / 10 | 66 / 59 / 10 |
| *Stomopneustes variolaris* | 13 | 42 / 28 / 13 | 52 / 35 / 13 | 56 / 36 / 14 | 56 / 36 / 14 | 56 / 36 / 14 | 56 / 36 / 14 |
| *Chelonia mydas* | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 167 / 104 / 50 | 167 / 104 / 50 |
| *Lepidochelys olivacea* | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 73 / 48 / 32 | 74 / 49 / 33 |

The turtle counts change abruptly only at 50 km because nearly all iNaturalist locations carry uncertainty around 31 km and the telemetry records are aggregated to one-degree cells with 111 km uncertainty. A 50 km allowance is far wider than the environmental grid and cannot validate a 0.05° cell assignment. With a threshold close to the raster cell width (≤5 km), the spinner dolphin has 19 occupied cells, the surgeonfish 8, and the urchin 13; the turtles have none. Those counts do not yet establish enough spatially independent cells for folds because the accessible area, spatial block size and sampling-bias treatment are not defined. The top-five concentration is especially strong for Acanthurus and Stomopneustes.

## 7. ON_LAND review

For every listed candidate, each OBIS `ON_LAND` row also has negative `shoredistance`, consistent with OBIS’s definition of that field. The table then compares those records with the much coarser 0.05° mask.

| Candidate | ON_LAND and negative shore-distance | Those mapping to valid raster cells | Those mapping to fill cells |
|---|---:|---:|---:|
| *Stenella longirostris* | 23 | 17 | 6 |
| *Lepidochelys olivacea* | 22 | 1 | 21 |
| *Chelonia mydas* | 67 | 5 | 62 |
| *Acanthurus lineatus* | 14 | 9 | 5 |
| *Stomopneustes variolaris* | 45 | 27 | 18 |

Interpretation is species- and record-context dependent:

- **Raster-valid but OBIS-land flagged:** a nearest cell can be water even when the original coordinate is inland. This is a coastline/resolution mismatch or coordinate error, not evidence that the flag is false. Spinner dolphins (17/23), surgeonfish (9/14), and urchins (27/45) have this pattern.
- **Land-flagged and raster fill:** this is consistent with an inland/shoreline point, but the ecological meaning differs. Turtle metadata includes hatchlings emerging/nesting, dead beach turtles, and released animals; those can be legitimate life-history observations but are not in-water presences. *Stomopneustes* records include tide-pool/rock-pool notes and habitats such as “coral/rocks/pools”; these can be legitimate intertidal observations, yet a coarse surface-ocean pixel cannot resolve the occupied rock pool. Some other land-flagged coordinates may be errors; the available records do not settle them.
- **Not land-flagged but raster fill:** four olive-ridley, two green-turtle, four surgeonfish and five urchin records fall in this category. A missing pixel is not a species absence and may reflect the nearest-cell coastline mask; retain source coordinates for domain review.

The source snapshot has no approved high-resolution marine boundary or coastline treatment for resolving these cases. Do not automatically delete all `ON_LAND` records or retain them just because a neighbouring Bio-ORACLE cell is valid. OBIS says `shoredistance` is based on OpenStreetMap and negative values indicate inland coordinates. [OBIS field definitions](https://portal.obis.org/data/access/), [OBIS data-quality flags](https://manual.obis.org/dataquality.html).

## 8. Species-specific ecological evidence

### 1. *Stenella longirostris* — best next-QA candidate

The local rows are all `HumanObservation`; 104 of 108 are iNaturalist, with sparse remarks and no comparable survey-effort field. Three rank-gap records were restored taxonomically; the revised set spans four dataset IDs. Metadata includes an “inaccurate location” remark and a record whose locality says Antarctica while the coordinates are in the Sri Lankan crop, so locality and coordinate provenance need review. There are 23 land flags, including six matched to fill cells; the other 17 only acquire a valid water pixel after snapping to the 0.05° grid.

External Sri Lankan studies verify both ecological contexts: an offshore cruise observed spinner dolphins as the dominant species by individual count, and a vessel survey in Trincomalee Bay reported them close to shore in the morning, moving farther offshore and returning toward the bay by dusk. These studies support marine use but also show that a single coastal/offshore label is insufficient. The local iNaturalist points are not standardized survey encounters, so a sightings model would need verified observation provenance and an explicit spatial/effort design. [Offshore Sri Lanka cetacean survey](https://journal.iwc.int/index.php/jcrm/article/view/576), [Trincomalee Bay and adjacent waters study](https://onlinelibrary.wiley.com/doi/10.1155/2014/819263).

### 2. *Acanthurus lineatus* — good marine taxon, weak current spatial support

The species identity is well supported after recovering 14 blank-rank rows. Locality metadata includes Kandakuliya Reef, Bar Reef Marine Sanctuary, Kalkudah Bay’s seaward reef side and other reef/coastal collection sites. The snapshot is still concentrated: 73/89 are iNaturalist, 23 uncertainty values are missing, and the five most occupied raster cells hold 83% of valid matches. WoRMS confirms the accepted marine species; a descriptive WoRMS habitat note, marked unreviewed, associates it with shallow, exposed seaward surge-zone reefs (often <3 m). The local area also has collected specimens and barcode records, not only sighting observations. [WoRMS species record](https://www.marinespecies.org/aphia.php?id=159582&p=taxdetails), [Australian Museum species profile](https://australian.museum/learn/animals/fishes/striped-surgeonfish-acanthurus-lineatus-linnaeus-1758/).

The relevant habitat is a narrow, shallow reef zone. A 5.5 km surface climatology plus broad bathymetry does not represent reef exposure, substrate, local depth or wave energy. Acanthurus is therefore a conditional data-acquisition candidate, not a suitable current 0.05° modelling dataset.

### 3. *Stomopneustes variolaris* — strong coastal evidence, wrong scale for these rasters

Local metadata gives six preserved specimens from Ambalangoda (1975) with habitat labels `coral/rocks/pools` or `rocks, coral`. Repeated 2022 iNaturalist rows share a single coordinate and tide-pool remark. In all, 45 rows are land-flagged, 27 still snap to a valid raster cell, and 18 map to fill. A Sri Lankan species account records this urchin at 0.1–5 m on subtidal rocks, rocky platforms, crevices, boulders and coral reefs; a local study also sampled it across rocky-shore intertidal/splash habitats. The exact tidal state and record duplication need review. [Sri Lankan echinoid species account](https://pmc.ncbi.nlm.nih.gov/articles/PMC6910863/), [Sri Lankan rocky-shore population study](https://agris.fao.org/search/en/providers/125309/records/6748d2207625988a37210553).

### 4–5. *Chelonia mydas* and *Lepidochelys olivacea* — marine animals, mixed life-history records

The source set combines iNaturalist observations with tracking datasets. Green turtle has 169 human observations and 14 machine/telemetry rows; olive ridley has 76 human observations and 31 telemetry rows. Remarks include nesting/hatchling, beach mortality, release, feeding and mating contexts. The tracking datasets explicitly say their locations are aggregated per species per one-degree cell, consistent with their ~111 km uncertainty. Green-turtle tracking research from Rekawa documents shallow coastal inter-nesting and residence areas as well as a long-distance oceanic foray; Sri Lankan sources also document turtle nesting beaches. Marine movements are real, but these OBIS records mix nest sites, beach and in-water observations, coarse aggregate telemetry and potentially rehabilitation events. [Green-turtle telemetry study](https://link.springer.com/article/10.1007/s00227-013-2194-8), [Sri Lankan sea-turtle nesting proceedings](https://repository.library.noaa.gov/view/noaa/3259/noaa_3259_DS1.pdf), [Sri Lanka tracking summary](https://iotn.org/iotn29-02-where-do-they-go-satellite-tracking-of-nesting-turtles-in-sri-lanka/).

The current snapshot supplies no turtle position with uncertainty ≤25 km, leaving zero records at ≤5 km. A specialized telemetry analysis could be viable from original animal-level fixes, but the current species-level aggregates are too coarse for these cells. Choose the life stage and movement question before considering these species again.

### 6. *Penaeus (Fenneropenaeus) indicus* — do not advance until reconciled

Most source rows are `PreservedSpecimen` records with no event date or uncertainty and a blank dataset name; localities include Negombo/Koggala/Kalpitiya lagoons, Bundala, Rakawa and coastal sites. FAO describes adults as marine but juveniles/subadults as using estuaries, backwaters and lagoons, so these localities may be biologically plausible while still representing different life stages and salinity regimes. The dataset does not identify those stages consistently, and the taxon ID is unresolved. Reconcile the source collection, current AphiaID/LSID and specimen life stage before counting any for modelling. [FAO species profile](https://www.fao.org/fishery/docs/CDrom/aquaculture/I1129m/file/en/en_indianwhiteprawn.htm), [current OBIS accepted-name page](https://obis.org/taxon/377434).

No local dataset field links any candidate to the project’s resilience objective. Candidate availability is not an ecological or stakeholder rationale for selecting an indicator species.

## 9. Ranked shortlist and conditional decision

| Rank | Candidate | Feasibility for spatially independent validation | Decision on background sampling / ML dataset construction |
|---:|---|---|---|
| 1 | *Stenella longirostris* | Weak/conditional: 34 valid cells overall, 19 at ≤5 km; 63% of valid points in five cells, and most records are one citizen-science source. Spatial blocks and accessible area remain undecided. | **Conditional GO for targeted record/domain QA only. NO-GO for background sampling or dataset construction now.** Reconsider if event locations, source effort and land/coastal records can be validated and enough separated cells remain. |
| 2 | *Acanthurus lineatus* | Weak: 14 cells overall, 8 at ≤5 km; 83% in the five leading cells and 73/89 from iNaturalist. | **Conditional GO only if adding reef-specific observations/layers is acceptable. NO-GO with the current environmental scale.** |
| 3 | *Stomopneustes variolaris* | Weak: 16 cells overall, 13 at ≤5 km, concentrated in the southwest; duplicate sightings and intertidal points complicate cells. | **NO-GO for the current Bio-ORACLE surface grid.** Reopen only with explicit intertidal/rocky-reef target data at finer scale. |
| 4 | *Chelonia mydas* | Not established: 65 cells overall but none with uncertainty ≤25 km; many land/nesting/coastal records and broad tracks. | **NO-GO with the present occurrence export.** Reopen with original animal-level tracking fixes or a clearly filtered observation-only question. |
| 5 | *Lepidochelys olivacea* | Not established: 60 cells overall but none with uncertainty ≤25 km; includes 1° tracking aggregates, nesting and beach observations. | **NO-GO with the present occurrence export.** Reopen with original telemetry fixes and explicit life-stage/habitat rules. |
| 6 | *Penaeus (Fenneropenaeus) indicus* | Not assessable: no reconciled observations; specimen locations may mix marine adults and estuarine juveniles. | **NO-GO until taxon IDs, collection provenance and life stages are reconciled.** |

This ranking prioritizes the next evidence to obtain; it does not approve a focal species. None currently meets the full evidence gate for background sampling or first dataset construction. Spatial validation remains unproven for all candidates because the study polygon, spatial block scale, and source-bias strategy have not been selected.

## 10. Remaining decisions before the first modelling dataset

1. **Ecological target:** choose the species and define whether the target is offshore sightings, reef fish occupancy, intertidal urchins, turtle foraging/migration, or another explicit habitat question. State the project link and relevant life stage.
2. **Analysis area:** approve a real marine study polygon/accessibility domain. The current EEZ-extrema rectangle is only an intake crop.
3. **Taxonomy and occurrence scope:** approve candidate IDs and treatment of the 2,479 rank-gap pairs. Resolve Penaeus 1809203 versus current accepted ID 377434. Confirm observation versus preserved-specimen inclusion, duplicates and occurrence-status semantics.
4. **Coastal/land rule:** decide how to handle OBIS `ON_LAND`, negative `shoredistance`, raster-fill cells, shoreline tolerance, tide pools, nesting beaches, stranded animals and near-coast points; use a suitable higher-resolution coastline or marine mask.
5. **Positional uncertainty:** select a scientifically justified radius and whether records with missing uncertainty can be recovered from source metadata. At present they are unknown, not precise.
6. **Environmental predictors and time:** choose depth layer and time baseline; confirm a baseline matches selected event years and species ecology. Obtain reef/intertidal variables if those habitats are the target; then decide variable filtering before any correlation-based selection.
7. **Source/effort and background:** define treatment of iNaturalist, tracking, museum specimens, sighting effort, repeated observations and spatial reporting bias. Only after that, approve accessible area and the presence-background sampling design. Do not treat unobserved cells as confirmed absences.
8. **Spatial validation:** set block size and a minimum number of occupied separated cells per fold after the target area and precision rule are fixed. Recheck counts with shared-cell and neighborhood grouping before a dataset is built.

## References

- [OBIS data access and field definitions](https://portal.obis.org/data/access/)
- [OBIS WoRMS taxonomic backbone](https://obis.org/sources/worms/)
- Candidate taxon records: [Stenella 137109](https://obis.org/taxon/137109), [Lepidochelys 220293](https://obis.org/taxon/220293), [Chelonia 137206](https://obis.org/taxon/137206), [Acanthurus 159582](https://www.marinespecies.org/aphia.php?id=159582&p=taxdetails), [Stomopneustes 212440](https://www.marinespecies.org/aphia.php?id=212440&p=taxdetails), [Penaeus accepted name 377434](https://obis.org/taxon/377434).
- [Bio-ORACLE documentation](https://www.bio-oracle.org/documentation.php)
- Sri Lankan ecology sources: [offshore cetacean survey](https://journal.iwc.int/index.php/jcrm/article/view/576), [Trincomalee cetacean survey](https://onlinelibrary.wiley.com/doi/10.1155/2014/819263), [green turtle telemetry](https://link.springer.com/article/10.1007/s00227-013-2194-8), [Sri Lankan turtle nesting proceedings](https://repository.library.noaa.gov/view/noaa/3259/noaa_3259_DS1.pdf), [Stomopneustes species account](https://pmc.ncbi.nlm.nih.gov/articles/PMC6910863/), [Stomopneustes rocky-shore study](https://agris.fao.org/search/en/providers/125309/records/6748d2207625988a37210553), [FAO Penaeus indicus profile](https://www.fao.org/fishery/docs/CDrom/aquaculture/I1129m/file/en/en_indianwhiteprawn.htm).

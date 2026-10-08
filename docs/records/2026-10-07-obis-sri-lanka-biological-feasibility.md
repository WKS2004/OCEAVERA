# OBIS biological data feasibility — Sri Lanka candidate

- **Date:** 7 October 2026
- **Status:** Preliminary feasibility evidence; Area 230 was later finalised as the OBIS collection scope under D-034; focal species remains open
- **Purpose:** Assess a bounded OBIS occurrence sample before the group selects a focal species and marine domain.
- **Contributor:** Sanuda Abeysinghe, with AI-assisted data-intake support recorded in the contributor log

## Query and area discovery

The initial proposal records Sri Lanka as a geographic preference, not a final boundary. The Flanders Marine Institute record for the Sri Lankan Exclusive Economic Zone (EEZ), MRGID 8346, reports a bounding envelope of longitude 77.0233–85.2329 and latitude 2.5665–11.4488. An OBIS checklist request using that rectangle returned an API-reported total of 10,418 checklist entries. The rectangle is only a discovery envelope: it includes land and waters beyond the EEZ polygon, and the returned list included birds and higher taxonomic ranks. It is not a measured count for the final marine domain.

The OBIS area endpoint returned 799 area records. The matches included OBIS area 230, “Sri Lanka” (type obis), area 10239, “South Coast of Sri Lanka” (type ebsa), and area 10255, “Sri Lankan side of Gulf of Mannar” (type ebsa). At the time of this feasibility assessment, Area 230 was used only as a provisional filter for the two candidate samples below. The user later finalised Area 230 as the scope for full biological collection in [D-034](2026-10-07-decision-obis-area-230.md). Its name and area type still do not establish that it represents the project's exact EEZ polygon or final modelling population.

The OBIS facet request for originalScientificName in area 230 returned these first ten values:

| Original scientific name | API record count |
| --- | ---: |
| Pelecanus philippensis | 507 |
| Egretta garzetta | 408 |
| Himantopus himantopus | 375 |
| Copepoda | 269 |
| Coenobita rugosus | 246 |
| Platalea leucorodia | 236 |
| Tringa totanus | 236 |
| Penaeus indicus | 211 |
| Phalacrocorax fuscicollis | 197 |
| Chelonia mydas | 183 |

These are publisher-reported facet counts for the submitted name strings, not quality-filtered presences or candidate-selection decisions. The first ten values include non-marine birds and a class-level name; counts alone do not establish ecological fit or usable coverage.

## Candidate feasibility samples

The two samples were chosen for a limited inspection because their name-level counts were relatively high and the returned occurrence rows were marked marine by OBIS. Neither taxon is selected as the focal species.

| Query name | OBIS-reported matches | Rows retained for inspection | Sample observations |
| --- | ---: | ---: | --- |
| Chelonia mydas | 183 | 10 | All 10 rows had coordinates and coordinate uncertainty values (31,362–173,627 m); all had NO_DEPTH, and 3 also had ON_LAND. The sample spans date-year values 2008, 2017–2018 and 2024–2026. It combines records from two contributing datasets. |
| Penaeus indicus | 211 | 10 | OBIS returned Penaeus (Fenneropenaeus) indicus with AphiaID 1809203; the sample did not include taxonRank or taxonID. All rows had a year value of 2009 but no exact event date or coordinate-uncertainty value; all had NO_DEPTH, and 6 had ON_LAND. Four coordinate groups recur across nine rows, but all occurrence identifiers are distinct. These repeated locations are not treated as duplicates. |

All 20 sampled rows had OBIS marine=true, even where the quality flags included ON_LAND; this conflict needs record-level review. The samples were the first ten rows returned by the API, not random or spatially representative samples. The API-reported totals are query counts at retrieval time and may change.

At intake, the original JSON response pages were saved unchanged in Git-ignored raw storage and inspected. They were removed from local storage on 7 October 2026 at the user's request. The acquisition-time SHA-256 values in the source records were checked against the payloads before removal; the raw pages are not currently retained. Separate source records retain their provenance and review summaries:

- [Chelonia mydas sample provenance](2026-10-07-source-obis-chelonia-mydas-feasibility.md)
- [Penaeus indicus sample provenance](2026-10-07-source-obis-penaeus-indicus-feasibility.md)

The checks above are descriptive. No record was cleaned, deduplicated, excluded or converted. In particular, a repeated coordinate does not prove duplicate sampling, and ON_LAND requires checking the source location and boundary before exclusion.

## Feasibility limits and subsequent decision

- The two samples below were feasibility-only and did not decide the focal species. After this assessment, the user finalised Area 230 as the collection domain for the complete OBIS intake; see [D-034](2026-10-07-decision-obis-area-230.md) and the [full acquisition source record](2026-10-07-source-obis-area-230-all-occurrences.md).
- Area 230 is an OBIS-defined area. The collection decision does not make it an exact Sri Lankan EEZ polygon or resolve the modelling domain, which remains subject to data-supported review.
- The 10-row samples do not establish the quality or coverage of all 183 or 211 API matches.
- Contributing source licences differ. Preserve each row’s source identity, citation and rights metadata; review the complete selected resource and its sharing terms before redistribution.
- Occurrence coordinates were present in the original raw pages. Those pages have since been removed from local storage; no coordinates are copied into this record.
- The subsequent complete Area 230 acquisition is recorded separately. No cleaned/integrated dataset, data dictionary, cleaning rule, target, background sample, environmental join or model result has been produced.
- Missing occurrences are not confirmed absences. No occurrence-probability or suitability claim follows from these counts.

The full Area 230 acquisition follows the user's collection-scope decision. Later work still needs to review focal-species relevance, source terms, taxonomy, coordinates, dates, repeats, depth and sampling concentration before selecting records for a modelling population or integrating environmental layers.

## Publisher references

- [OBIS occurrence API](https://api.obis.org/#/Occurrence/get_occurrence)
- [OBIS facet API](https://api.obis.org/#/Facet/get_facet)
- [OBIS manual: data access and citation](https://manual.obis.org/access)
- [OBIS manual: access FAQ and area-query guidance](https://manual.obis.org/FAQ.html)
- [Marine Regions: Sri Lankan EEZ, MRGID 8346](https://www.marineregions.org/gazetteer.php?id=8346&p=details)

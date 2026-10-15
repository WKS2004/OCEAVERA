# OCEAVERA OBIS Species Feasibility Audit

**Audit date:** 10 October 2026
**Branch:** `pipeline/data-cleaning-obis`
**Scope:** Read-only audit of the saved OBIS Area 230 snapshot and Bio-ORACLE intake. No model/target was built; no datasets, source code, configurations, environments, or packages were changed for this audit.
**Status:** Evidence for a later project decision, not an approved species or model.

> **Interim-storage update — 11 October 2026:** This audit records the files present on 10 October. Under [D-049](../docs/records/2026-10-11-decision-interim-one-current-dataset.md), the source-validation copy and experimental 90% completeness-screen CSV listed below are no longer retained in `data/interim/`; the current cleaned OBIS dataset and its path are documented in the [cleaning record](../docs/records/2026-10-11-obis-area-230-cleaning.md).

## 1. Executive Summary

The repository contains the fixed OBIS Area 230 snapshot: **23,934 occurrence records × 230 columns**, plus **356 Bio-ORACLE v3 NetCDF grids**. The OBIS records are presence-oriented. There are 50 rows marked absence, but no demonstrated systematic non-detection design; their occurrenceStatus is blank. Many other rows also have blank or identifier-like occurrenceStatus, so absence=false cannot make every row a confirmed presence.

A conservative screening filter (Section 4) leaves **9,813 rows across 1,272 species-name/OBIS-ID pairs**. It does not deduplicate observations, remove ON_LAND or NO_DEPTH flags, or enforce a coordinate-uncertainty threshold. This is not a model-ready count. Only 160 taxa have at least 10 screened rows; 49 have at least 30; 18 have at least 100.

**Provisional next-QA candidate:** Stenella longirostris, with Lepidochelys olivacea and Chelonia mydas as alternatives. Spinner dolphin has 105 screened records, 91 exact coordinates, 36 occupied 0.05° cells, and two dataset IDs; its median reported uncertainty is 2,240 m. However, 23 records are flagged ON_LAND, all 105 have NO_DEPTH, and source/effort bias is unresolved. Its resilience relevance is not established by repository evidence.

**Verdict: CONDITIONAL GO for further QA and environmental integration; NO-GO for training now.** Valid marine raster coverage, domain, ecology, background design, and spatially independent evaluation remain unverified. If later approved, use a justified presence-background approach; scores would express relative suitability, not calibrated occurrence probability.

## 2. Dataset and Repository Overview

### OBIS snapshot

| Item | Evidence |
|---|---|
| Snapshot | OBIS Area 230; obtained 8 October 2026 |
| Raw CSV | data/raw/obis/csv/area-230-20261008T055217394846Z.csv |
| Size / SHA-256 | 26,892,051 bytes / 16ec5ff96e57dc1e58baa33912d16fe7e9098c78759e750608611bf9a2dc0c43 |
| Shape | 23,934 × 230 |
| Raw JSON | 24 saved pages + manifest; all 23,934 OBIS ids unique |
| Source-validation copy present during this audit; later removed | data/interim/obis/source_validation/occurrences.csv |
| 90% completeness-screen output present during this audit; later removed | data/interim/obis/cleaning/occurrences.csv; 23,934 × 22, separate from audited 230-column source |
| Provenance | docs/records/2026-10-08-source-obis-area-230-api-csv.md |

The source has 23,327 rows with absence=false and dropped=false. The historical 23,217-row count additionally removes marine=false; it is not the current audit input or a model table. No OBIS/Bio-ORACLE merged table exists.

Related code: src/data_collection/01_obis_occurrences.py, 02_obis_json_to_csv.py, src/data_preparation/03_stage_obis_csv.py, 04_clean_obis_occurrences_csv.py. Related notebooks: notebooks/branch_work/01_pipeline_biological_data_collection.ipynb and 02_pipeline_environmental_data_collection.ipynb. Source, EDA, column-screen and cleaning records are in docs/records/.

### Bio-ORACLE and geographic extent

The repository has 356 NetCDF payloads and 713 JSON files in data/raw/bio_oracle; interim has 356 NetCDF and 358 JSON files. Intake records report 356 grids, 2,392 variable instances, 139 distinct variable codes, 55 baselines, six SSP scenarios and one static terrain layer.

D-048 crop: 77.023333°–85.232917°E, 2.566500°–11.448833°N. It is a rectangular intake extent derived from Sri Lanka EEZ bounds, not an EEZ polygon or approved model domain. No polygon file is present in the repository. Grids are 0.05° WGS84/EPSG:4326. Baseline labels include 2000 and 2010; future scenarios 2020–2090 by decade; static terrain label 1970. There is no annual environmental series.

### Audit method and limits

Counts were computed in memory from the saved 230-column CSV; non-empty means a nonblank string. Taxa are grouped by (speciesid, species), flags parsed as JSON arrays, and coordinates checked for finite/legal values. Grid cells use saved Bio-ORACLE resolution/origin but do not establish wet-cell validity.

The bundled Python runtime lacked a NetCDF reader (xarray, netCDF4, h5py) and geospatial reader. No packages were installed. Therefore local NetCDF arrays/masks were not opened: valid-cell percentages, exact ocean overlaps and extracted local raster values are unknown. OBIS-enriched sst/sss are profiled separately and do not substitute for the local raster join.

## 3. Taxonomic and Species Identification Results

| Field/check | Result |
|---|---:|
| scientificName | 23,475 nonblank; 4,307 distinct |
| originalScientificName | 23,855; 4,877 distinct |
| species | 17,510; 3,239 distinct |
| speciesid | 17,510; 3,240 distinct IDs |
| AphiaID / aphiaID | 23,475 each; equal on all jointly filled rows, no one-sided values |
| scientificNameID | 21,390 (89.37%) |
| taxonRank | blank 13,513 (56.5%); species 9,896; genus 370; family 73; subspecies 53; sub species 5; subgenus 7; order 7; phylum 4; class 2; subfamily 2; unranked 1; complex 1 |

Missingness in species and speciesid aligns: 6,424 rows lack both. Exact species-rank records with both fields: 9,843 rows / 1,312 name-ID pairs. Adding subspecies/sub species: 9,894 / 1,319 before quality exclusions. Each speciesid maps to one species string, but Acetabularia crenulata maps to IDs 368435 and 494919. Thirty-eight IDs map to multiple scientificName values. Retain the pair for counts and review the conflict.

Matched scientificName differs from provider originalScientificName in 3,743/23,475 paired rows (15.94%; 1,152 distinct pairs). One common example is Penaeus indicus to Penaeus (Fenneropenaeus) indicus (211 rows); this can reflect accepted-name matching, not necessarily error. taxonomicStatus is blank in 23,643 rows; valid 145, accepted 144, invalid 2. unaccepted has 2,714 filled values but 781 numeric-looking distinct strings, so was not interpreted as Boolean. Flags: NO_ACCEPTED_NAME 490; NO_MATCH 459; WORMS_ANNOTATION_REJECT_AMBIGUOUS 1; WORMS_ANNOTATION_UNRESOLVABLE 1.

Name matching does not establish species-level rank. Blank-rank, genus/family and records lacking the species-ID pair are excluded from the species screen. Taxonomic literature was not independently checked.

## 4. Species Frequency Analysis

### Screening rule

The 9,813 records meet all conditions:
1. taxonRank (case-insensitive) is species, subspecies or sub species;
2. species and speciesid are populated;
3. dropped=false and absence=false;
4. marine=true;
5. finite coordinates within legal latitude/longitude limits; and
6. none of NO_MATCH, NO_ACCEPTED_NAME, WORMS_ANNOTATION_REJECT_AMBIGUOUS or WORMS_ANNOTATION_UNRESOLVABLE in flags.

It does not require eventDate or occurrenceStatus=present, remove ON_LAND/NO_DEPTH, deduplicate rows or coordinates, or threshold coordinate uncertainty. Counts are screening records, not independent samples.

### Counts per taxon

| Screened records | Taxa |
|---:|---:|
| 1–9 | 1,112 |
| 10–29 | 111 |
| 30–49 | 18 |
| 50–99 | 13 |
| 100–249 | 15 |
| 250–499 | 2 |
| 500+ | 1 |
| **Total** | **1,272** |

At least 10: 160 taxa; at least 30: 49; at least 50: 31; at least 100: 18; at least 250: 3; at least 500: 1. No raster masking, spatial thinning, uncertainty filter or project-domain filter is applied.

### Top 25 taxa

Raw pair = all source rows for speciesid/species regardless of screening; cells are occupied 0.05° coordinate cells; exact dates count distinct exact calendar dates among screened rows.

| ID | Species | Raw | Screen | Coords | Exact days | Years | Datasets | 0.05° cells | Land flags | Median uncertainty m |
|---:|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 343936 | Pelecanus philippensis | 507 | 507 | 507 | 367 | 1981–2026 | 1 | 173 | 289 | 31,344 |
| 159115 | Egretta garzetta | 417 | 417 | 383 | 307 | 2005–2026 | 1 | 125 | 375 | 211 |
| 212609 | Himantopus himantopus | 375 | 375 | 325 | 273 | 2006–2026 | 1 | 84 | 365 | 247 |
| 208657 | Coenobita rugosus | 246 | 246 | 241 | 190 | 2008–2026 | 1 | 47 | 212 | 37 |
| 416678 | Platalea leucorodia | 243 | 243 | 214 | 192 | 2004–2026 | 1 | 63 | 233 | 568 |
| 158970 | Tringa totanus | 236 | 236 | 203 | 165 | 2004–2026 | 1 | 64 | 223 | 434 |
| 343945 | Phalacrocorax fuscicollis | 197 | 197 | 179 | 161 | 2007–2026 | 1 | 70 | 182 | 215 |
| 137206 | Chelonia mydas | 183 | 183 | 183 | 146 | 1996–2026 | 4 | 101 | 67 | 31,362 |
| 137135 | Chlidonias hybrida | 181 | 181 | 163 | 131 | 2011–2026 | 1 | 64 | 142 | 356 |
| 212603 | Actitis hypoleucos | 154 | 154 | 147 | 131 | 2003–2026 | 1 | 65 | 145 | 216 |
| 1492275 | Cocos nucifera | 153 | 153 | 145 | 123 | 1964–2026 | 1 | 71 | 143 | 15.5 |
| 742486 | Barringtonia asiatica | 143 | 143 | 143 | 125 | 2008–2026 | 1 | 38 | 138 | 15 |
| 212623 | Tringa stagnatilis | 137 | 137 | 117 | 100 | 2010–2026 | 1 | 40 | 134 | 602 |
| 232044 | Pluvialis fulva | 120 | 120 | 105 | 92 | 2011–2026 | 1 | 41 | 116 | 2,500 |
| 148798 | Gelochelidon nilotica | 116 | 116 | 114 | 94 | 2012–2026 | 1 | 54 | 103 | 500 |
| 344030 | Crocodylus porosus | 112 | 112 | 112 | 77 | 2007–2026 | 1 | 35 | 102 | 188 |
| 220293 | Lepidochelys olivacea | 107 | 107 | 102 | 70 | 1970–2026 | 3 | 81 | 22 | 31,368 |
| 137109 | Stenella longirostris | 108 | 105 | 91 | 81 | 2013–2026 | 2 | 36 | 23 | 2,240 |
| 207529 | Grapsus tenuicrustatus | 98 | 98 | 89 | 73 | 2010–2026 | 1 | 36 | 65 | 31 |
| 159040 | Numenius phaeopus | 98 | 98 | 95 | 88 | 2015–2026 | 1 | 58 | 74 | 61 |
| 148790 | Tachybaptus ruficollis | 97 | 97 | 85 | 81 | 2012–2026 | 1 | 36 | 96 | 154 |
| 212600 | Calidris minuta | 79 | 79 | 57 | 53 | 2004–2026 | 1 | 22 | 75 | 218 |
| 158968 | Tringa nebularia | 76 | 76 | 72 | 60 | 2012–2026 | 1 | 32 | 73 | 216 |
| 159582 | Acanthurus lineatus | 89 | 75 | 62 | 44 | 2005–2026 | 2 | 14 | 12 | 149 |
| 212440 | Stomopneustes variolaris | 69 | 69 | 54 | 53 | 1975–2026 | 2 | 27 | 45 | 214 |

Counts alone do not select a focal species. Cocos nucifera is a plant despite marine=true and has 143/153 ON_LAND flags. Penaeus (Fenneropenaeus) indicus has 211 source rows, but 208 have blank rank and only three exact species-rank rows.

## 5. Presence/Absence Analysis

| Evidence | Rows |
|---|---:|
| absence=false / true | 23,884 / 50 |
| dropped=false / true | 23,371 / 563 |
| both absence=false and dropped=false | 23,327 |
| Explicit occurrenceStatus=present (case-insensitive) | 8,564 |
| occurrenceStatus blank / absent | 7,149 / 0 |

Other filled occurrenceStatus values are largely taxon LSIDs: 8,170 WoRMS LSIDs and 51 other identifier strings. All 50 absence=true rows have blank occurrenceStatus. No systematic non-detection survey or comparable effort design was identified. Treat the dataset as presence-oriented; missing observations are not absences. Do not derive a binary target from absence=false/true or create pseudo-absences before defining accessible area, sampling bias and background design.

## 6. Spatial Distribution and Independence

All 23,934 coordinates are finite and in legal ranges; extent 2.9330–11.3167°N, 77.1330–85.0600°E. They are within D-048’s rectangle, not verified inside an EEZ polygon.

There are 7,362 unique exact coordinate pairs. Repeated pairs: 1,103 locations account for 17,675 records (16,572 beyond one per pair); one location has 936 records. No full rows are identical. OBIS id is populated and unique for all rows. occurrenceID is populated for 20,762 and unique on 20,704; 58 pairs repeat. Each pair shares coordinates, exact event date and scientific name but differs in dataset_id and taxonRank; retain for provenance review rather than silently deduplicating.

For 13,887 species-pair records with dropped=false, absence=false, marine=true, valid coordinates and nonblank eventDate, 490 species/location/date groups repeat (1,634 extra rows beyond one per group; maximum multiplicity 88).

coordinateUncertaintyInMeters is populated on 11,116/23,934 (46.45%): min 1 m, median 2,088 m, Q3 17,144 m, mean 81,597 m, max 2,753,412 m. Of the screened rows, 9,680/9,813 have NO_DEPTH and 6,137 carry ON_LAND; the screen retains both flags. The flags warrant investigation, not automatic deletion. A 0.05° cell is roughly 5.5 km; uncertainties can exceed cell width.

For top-taxa 0.05° cells, bounding box N–S × E–W (approx km), land flags and uncertainty coverage:

| Species | Cells | Bbox km | Land / screen | Uncertainty filled / screen |
|---|---:|---:|---:|---:|
| Pelecanus philippensis | 173 | 432×238 | 289/507 | 507/507 |
| Egretta garzetta | 125 | 433×230 | 375/417 | 330/417 |
| Himantopus himantopus | 84 | 418×239 | 365/375 | 275/375 |
| Coenobita rugosus | 47 | 325×206 | 212/246 | 185/246 |
| Platalea leucorodia | 63 | 419×231 | 233/243 | 186/243 |
| Tringa totanus | 64 | 406×235 | 223/236 | 171/236 |
| Phalacrocorax fuscicollis | 70 | 415×193 | 182/197 | 155/197 |
| Chelonia mydas | 101 | 668×774 | 67/183 | 183/183 |
| Chlidonias hybrida | 64 | 424×225 | 142/181 | 127/181 |
| Actitis hypoleucos | 65 | 414×229 | 145/154 | 119/154 |
| Cocos nucifera | 71 | 432×172 | 143/153 | 140/153 |
| Barringtonia asiatica | 38 | 415×234 | 138/143 | 115/143 |
| Tringa stagnatilis | 40 | 417×227 | 134/137 | 94/137 |
| Pluvialis fulva | 41 | 414×235 | 116/120 | 78/120 |
| Gelochelidon nilotica | 54 | 433×230 | 103/116 | 79/116 |
| Crocodylus porosus | 35 | 289×175 | 102/112 | 100/112 |
| Lepidochelys olivacea | 81 | 779×773 | 22/107 | 107/107 |
| Stenella longirostris | 36 | 565×331 | 23/105 | 92/105 |
| Grapsus tenuicrustatus | 36 | 310×225 | 65/98 | 79/98 |
| Numenius phaeopus | 58 | 433×205 | 74/98 | 76/98 |
| Tachybaptus ruficollis | 36 | 345×233 | 96/97 | 67/97 |
| Calidris minuta | 22 | 397×227 | 75/79 | 56/79 |
| Tringa nebularia | 32 | 420×200 | 73/76 | 50/76 |
| Acanthurus lineatus | 14 | 317×194 | 12/75 | 65/75 |
| Stomopneustes variolaris | 27 | 141×176 | 45/69 | 56/69 |

Cells are simple coordinate occupancy, not independent cells after uncertainty, land/sea mask, effort or clustering checks. Bboxes are descriptive, not habitat measures. Actual local raster validity was not checked. A verified domain and per-predictor masks are required before evaluating spatial separation or folds.

## 7. Temporal Coverage

eventDate is filled on 18,722 rows; date_year/date_start/date_end/date_mid on 18,656. Missing eventDate: 5,212; missing date_year: 5,278.

| Precision | Rows |
|---|---:|
| Exact day/datetime | 16,706 |
| Interval containing slash | 803 |
| Year only | 909 |
| Month only | 290 |
| Other/unparsed | 14 |
| Missing | 5,212 |

Parsed years span 1755–2026, 195 distinct years. Earliest eventDate: 1755-07-02T12:00:00Z; latest: 2026-07-20. Historical provenance needs review. Intervals and year/month-only values are not exact days. Year counts below use date_year and include broad dates; 2026 is partial through the latest observation date.

| Year:count | Year:count | Year:count | Year:count |
|---|---|---|---|
| 1755:2, 1758:36, 1766:4, 1775:56 | 1782:5, 1786:3, 1787:20, 1789:10 | 1790:8, 1791:8, 1792:6, 1793:8 | 1794:7, 1795:6, 1797:5, 1800:3 |
| 1801:36, 1802:4, 1803:8, 1815:1 | 1816:2, 1817:2, 1820:4, 1822:20 | 1824:6, 1825:22, 1828:13, 1829:22 | 1830:18, 1831:24, 1832:10, 1833:6 |
| 1835:26, 1836:4, 1837:6, 1838:2 | 1839:14, 1840:6, 1841:1, 1842:5 | 1843:2, 1844:11, 1845:4, 1846:5 | 1847:12, 1848:3, 1849:41, 1851:1 |
| 1852:25, 1853:8, 1854:7, 1855:4 | 1856:10, 1857:2, 1858:2, 1859:1 | 1860:3, 1861:3, 1863:5, 1864:6 | 1867:8, 1868:2, 1869:4, 1870:2 |
| 1872:8, 1873:2, 1874:2, 1875:1 | 1876:2, 1880:1, 1883:14, 1885:24 | 1886:4, 1887:6, 1888:11, 1889:2 | 1891:5, 1892:2, 1893:2, 1894:4 |
| 1895:3, 1898:1, 1899:44, 1900:1 | 1901:7, 1902:12, 1903:22, 1904:6 | 1905:7, 1906:2, 1908:3, 1909:6 | 1910:24, 1911:13, 1912:3, 1914:2 |
| 1915:2, 1917:2, 1918:2, 1920:16 | 1921:86, 1922:2, 1923:2, 1925:2 | 1926:4, 1927:4, 1928:2, 1929:195 | 1930:5, 1932:9, 1933:2, 1934:27 |
| 1935:1, 1936:5, 1937:7, 1938:8 | 1939:6, 1943:1, 1944:2, 1945:4 | 1946:7, 1949:1, 1950:93, 1951:24 | 1952:4, 1953:4, 1955:4, 1956:58 |
| 1957:100, 1959:18, 1962:400, 1963:849 | 1964:1,079, 1965:723, 1966:10, 1967:1 | 1968:64, 1969:348, 1970:533, 1971:922 | 1972:1,062, 1973:15, 1974:75, 1975:96 |
| 1976:3, 1977:25, 1978:41, 1979:40 | 1980:10, 1981:68, 1982:14, 1983:209 | 1984:3, 1985:27, 1986:21, 1987:215 | 1988:6, 1989:6, 1990:5, 1991:131 |
| 1992:11, 1993:22, 1994:91, 1995:7 | 1996:423, 1997:3, 1998:1, 1999:5 | 2000:13, 2001:6, 2002:29, 2003:3 | 2004:28, 2005:105, 2006:72, 2007:76 |
| 2008:74, 2009:50, 2010:87, 2011:35 | 2012:153, 2013:87, 2014:690, 2015:175 | 2016:236, 2017:205, 2018:340, 2019:587 | 2020:272, 2021:162, 2022:349, 2023:869 |
| 2024:1,404, 2025:2,394, 2026:1,016 |  |  |  |

Counts cluster heavily in 1962–65, 1970–72, 2014, 2019 and 2023–26. Changing dataset/archive contributions may explain some of this; not separated here. Bio-ORACLE baselines are climatologies, not annual conditions at occurrence dates.

## 8. Data Quality and Filtering Results

Sequential row counts (filters overlap):
| Stage | Remaining | Change |
|---|---:|---|
| Raw | 23,934 | — |
| dropped=false | 23,371 | Removed 563 |
| then absence=false | 23,327 | 44 additional; 6 absence rows overlapped dropped |
| then marine=true | 23,217 | 110 additional marine=false |
| valid finite/range coordinates | 23,217 | No further removal |

At 23,217, 23,165 have marine=true and 52 have marine blank. Raw counts of marine=false (219) and marine blank (511) overlap earlier filters.

basisOfRecord counts: HumanObservation 16,199; PreservedSpecimen 5,105; Occurrence 1,744; MATERIAL_SAMPLE 602; preservedspecimen 156; MachineObservation 112; LivingSpecimen 16. samplingProtocol: 956 rows/56 values. samplingEffort: 967 rows; % 598, # 338, #/l 31. eventID: 983 rows/115 values. dataset_id has 132 distinct values; datasetName populated in 10,713. Sampling fields are sparse and heterogeneous, not a comparable effort denominator.

Flag counts (overlap; not additive):
| Flag | Rows |
|---|---:|
| NO_DEPTH | 17,273 |
| ON_LAND | 8,225 |
| DEPTH_EXCEEDS_BATH | 696 |
| NO_ACCEPTED_NAME | 490 |
| NO_MATCH | 459 |
| NOT_MARINE | 104 |
| MARINE_UNSURE | 51 |
| WORMS_ANNOTATION_RESOLVABLE_LOSS | 48 |
| WORMS_ANNOTATION_RESOLVABLE | 20 |
| WORMS_ANNOTATION_UNRESOLVABLE | 1 |
| WORMS_ANNOTATION_REJECT_AMBIGUOUS | 1 |

OBIS describes flags as QC signals that may need review, not automatic deletion criteria; ON_LAND especially needs coordinate/spatial validation. The 6,137 flagged candidate rows are a substantial marine-grid concern and require investigation.

## 9. Environmental Data Compatibility

### OBIS attributes

| Field | Filled | Min | Mean / median | Max | Note |
|---|---:|---:|---:|---:|---|
| bathymetry | 23,934 (100%) | −255 | mean 1,184.04 | 4,378 | OBIS lookup; CSV lacks explicit units/sign metadata |
| shoredistance | 23,934 (100%) | −22,697 | mean 65,846.46 | 369,072 | OBIS docs: meters; negative values inland |
| sst | 20,117 (84.05%) | 28.17 | mean 28.6027 | 29.04 | Bio-ORACLE-derived enrichment; not date-specific |
| sss | 20,117 (84.05%) | 33.12 | mean 33.8934 | 34.90 | Bio-ORACLE-derived enrichment; not date-specific |
| depth | 6,661 (27.83%) | 0 | mean 211.27 | 4,215 | Occurrence depth |
| minimumDepthInMeters | 6,346 (26.51%) | 0 | mean 83.27 | 4,215 | Sparse depth range |
| maximumDepthInMeters | 5,614 (23.46%) | 0 | mean 301.06 | 4,215 | Sparse depth range |
| coordinateUncertaintyInMeters | 11,116 (46.45%) | 1 | median 2,088 | 2,753,412 | Missing > half; often larger than grid cell |

bathymetry, occurrence depth, and event min/max depths differ and must not be conflated. Verify field units and bathymetry sign against metadata before use. Candidate OBIS sst/sss coverage: Stenella 104/105; Lepidochelys 97/107; Chelonia 135/183; Acanthurus 75/75; Stomopneustes 65/69. Filled values vary but do not prove local raster coverage.

### Local Bio-ORACLE compatibility

Manifests provide variable codes, depth/time labels, CRS/grid and _FillValue=-9999.9 for 2,392 variable instances. Families include temperature, salinity, currents, nutrients, oxygen, chlorophyll/phytoplankton, ocean colour, optical variables, bathymetry and terrain. Temperature, salinity, chlorophyll and bathymetry are candidate predictor families only, pending ecology and mask checks. NetCDF values/masks were not readable in the available runtime; no package was installed. Valid marine cells, local predictor completeness, and per-candidate raster matches are unknown. Do not substitute OBIS sst/sss or coordinate-only cells for this missing validation.

## 10. Ranked Focal Species Shortlist

Ranking balances screen count, occupied cells, coordinate precision, taxonomic specificity, source spread and flags. It is provisional, not group approval.

| Rank | Candidate | Screen rows | Coords | Cells | Dates / years | Datasets | Uncertainty | Assessment |
|---:|---|---:|---:|---:|---|---:|---|---|
| 1 | Stenella longirostris | 105 | 91 | 36 | 81 days; 2013–26 | 2 | 92 filled; median 2,240 m | 23 ON_LAND, all NO_DEPTH; 104/105 sst/sss. Best location-quality balance; few cells and bias unresolved. |
| 2 | Lepidochelys olivacea | 107 | 102 | 81 | 70 days; 1970–26 | 3 | 107 filled; median 31,368 m; max 814,050 m | 22 ON_LAND, all NO_DEPTH; 97/107 sst/sss; many cells but uncertainty exceeds grid scale. |
| 3 | Chelonia mydas | 183 | 183 | 101 | 146 days; 1996–26 | 4 | 183 filled; median 31,362 m; max 229,214 m | 67 ON_LAND, all NO_DEPTH; 135/183 sst/sss; best raw support but uncertainty/flags. |
| 4 | Acanthurus lineatus | 75 | 62 | 14 | 44 days; 2005–26 | 2 | 65 filled; median 149 m | 12 ON_LAND, all NO_DEPTH; all sst/sss; 73/89 source rows iNaturalist. Few cells/source concentration. |
| 5 | Stomopneustes variolaris | 69 | 54 | 27 | 53 days; 1975–26 | 2 | 56 filled; median 214 m | 45 ON_LAND, all NO_DEPTH; 65/69 sst/sss. Flag share weakens candidate. |

Repository evidence does not establish any candidate’s ecological relevance to the resilience target. Marine flag and taxonomic identity do not prove indicator value; confirm with domain literature and project stakeholders.

## 11. ML Training Dataset Feasibility

Not yet justified for training: presence-oriented records, clustered/heterogeneous sampling, sparse effort metadata, uneven taxonomy, coordinate uncertainty, land flags, no verified domain, no raster-validity join, no background design and no spatial evaluation design.

If those checks pass, a cell-based presence-background workflow with explicit accessible area and bias strategy, uncertainty sensitivity and spatially separated evaluation is plausible. Unobserved locations are not absences; scores would be relative to the selected background, not calibrated occurrence probability. A baseline plus three alternatives is technically possible, but fairness cannot be promised until each has enough valid separated marine cells and comparable target/background evidence.

## 12. Risks and Limitations

1. Presence-only: no verified non-detection design.
2. Status mismatch: absence=false is not textual present.
3. Taxonomy: rank is blank for 56.5%; accepted/provider names and IDs need reconciliation.
4. Sampling bias: top taxa often derive from one dataset; effort fields sparse.
5. Reuse/clustering: repeated location/date/species groups inflate raw counts.
6. Uncertainty: missing on over half of records; candidate uncertainty can exceed cells.
7. Coastal/land mismatch: 8,225 ON_LAND flags; 6,137 remain in screen; no polygon/mask.
8. Depth: 17,273 NO_DEPTH; every screened shortlist record has this flag.
9. Time mismatch: centuries of clustered records versus climatological/decadal predictors.
10. Environmental gap: local NetCDF masks/values uninspected.
11. Ecological relevance and habitat scale not established.
12. Counts apply only to the 8 October 2026 snapshot.

## 13. Provisional Recommendation

Advance Stenella longirostris (ID 137109) only to the next QA gate: 105 screened records, 91 exact coordinates, 36 cells, 81 exact days (2013–26), two dataset IDs and lower median reported uncertainty (2,240 m) than turtle alternatives. It has 23 ON_LAND flags and NO_DEPTH on all rows. This is a practical data-quality candidate, not a claim that it is the best resilience indicator. Alternatives: Lepidochelys olivacea (81 cells, but 31,368 m median uncertainty) and Chelonia mydas (101 cells, same high median uncertainty and 67 land flags). No candidate is approved for model training.

## 14. Recommended Next Steps

1. Confirm which taxon group is relevant to the resilience question; review species ecology sources.
2. Verify accepted name/ID and original source records, including repeated occurrence IDs.
3. Use an approved marine-domain polygon to assess ON_LAND, uncertainty and coastal coordinates.
4. With an authorized readable NetCDF environment, inspect selected baseline layers and fill masks in memory; quantify valid wet cells, units/depth labels and predictor coverage.
5. Recount candidates under transparent spatial, uncertainty and raster rules; report sensitivity.
6. Quantify source/effort bias and spatial clustering; decide on thinning or bias-aware background.
7. Define accessible area and presence-background approach; do not infer absences.
8. Count valid separated cells before designing spatial folds.
9. Present evidence and unresolved choices for a recorded group decision before training.

## Decision Summary

| Item | Result |
|---|---|
| Provisional species | Stenella longirostris, ID 137109, QA only; not group-approved |
| Usable occurrence count | 9,813 screening rows / 1,272 taxa; primary candidate 105 rows, 91 coordinates, 36 coordinate cells |
| Independent usable cells | Unknown until marine mask, raster validity, uncertainty, bias and independence checks |
| Additional data | Marine-domain polygon; readable Bio-ORACLE arrays/masks; ecology evidence; source/effort and taxonomic review |
| Target | Presence-background only if justified; no confirmed absences; relative suitability, not occurrence probability |
| Project feasibility | Conditional go for QA/integration; no-go for training now |
| Open questions | Which species fits resilience scope? Which domain, bias and uncertainty rules are justified? Do sufficient valid separated cells remain? |

## References and provenance

Repository: docs/records/2026-10-08-source-obis-area-230-api-csv.md; docs/records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md; docs/records/2026-10-09-decision-bio-oracle-catalog-intake.md (D-047); docs/records/2026-10-09-decision-bio-oracle-sri-lanka-bbox.md (D-048); docs/records/2026-10-09-source-marine-regions-sri-lanka-eez-bounds.md. Earlier 7 October Penaeus and Chelonia feasibility records are small, preliminary samples, not representative full-snapshot analysis. Local Bio-ORACLE manifests remain source metadata.

Official docs: [OBIS data access and field descriptions](https://portal.obis.org/data/access/); [OBIS data quality flags](https://manual.obis.org/dataquality.html); [OBIS QC overview](https://manual.obis.org/data_qc.html); [Bio-ORACLE documentation](https://www.bio-oracle.org/documentation.php).

# OCEAVERA — Exploratory Data Analysis (Sections A–F)

**Status:** Descriptive EDA completed on the frozen candidate table. This is not a target, species, predictor or modelling approval.

## Input and population

- Source: `data/interim/pseudo_absence/presence_background_candidates.parquet` (9,412,505 bytes)
- SHA-256: `234177bf3641856cdd10b425f2da957a27210f876d31092ba715a53cee7a429f` (identical after execution)
- Shape/CRS/geometry: **4,706 × 527**, EPSG:4326, Point
- Environmental definitions: **382**; all were retained in the input.
- Preliminary species-level eligible subset: **3,458 rows** (1,729 positives, 1,729 sampled backgrounds).

A positive is a recorded OBIS occurrence. A background row is a sampled marine cell and is **not** a verified absence. Repeated records may share a grid cell.

## Period and class counts

| population | analysis_period | presence_background_label | rows |
| --- | --- | --- | --- |
| complete_population | 2000-2009 | 0 | 376 |
| complete_population | 2000-2009 | 1 | 376 |
| complete_population | 2010-2019 | 0 | 596 |
| complete_population | 2010-2019 | 1 | 596 |
| complete_population | 2020-2026 | 0 | 1381 |
| complete_population | 2020-2026 | 1 | 1381 |
| eligible_species_subset | 2000-2009 | 0 | 161 |
| eligible_species_subset | 2000-2009 | 1 | 161 |
| eligible_species_subset | 2010-2019 | 0 | 443 |
| eligible_species_subset | 2010-2019 | 1 | 443 |
| eligible_species_subset | 2020-2026 | 0 | 1125 |
| eligible_species_subset | 2020-2026 | 1 | 1125 |

## Taxa and environmental completeness

- Positive taxon keys: **614** (eligible-positive taxon keys: **441**).
- Distinct positive grid cells: **362**; distinct cell-periods: **480**.
- Repeated positive taxon/cell/period groups: **331**, covering **1,107** records (776 beyond one per group).
- Blank string values occur **99,424** times across 92 source/metadata columns; null and blank counts remain separate.
- Environmental fields fully populated in complete population: **0 / 382**; completely empty: **2**.
- Eligible subset fully populated features: **303 / 382**; infinities found: **0**.

### Taxonomic eligibility reasons

| presence_background_label | ml_eligibility_reason | rows |
| --- | --- | --- |
| 0 | missing_core_environment | 27 |
| 0 | preliminary_species_core_eligible | 1729 |
| 0 | source_cell_centre_not_marine | 80 |
| 0 | source_cell_centre_not_marine;missing_core_environment | 173 |
| 0 | unverified_species_rank | 267 |
| 0 | unverified_species_rank;missing_core_environment | 6 |
| 0 | unverified_species_rank;source_cell_centre_not_marine | 6 |
| 0 | unverified_species_rank;source_cell_centre_not_marine;missing_core_environment | 65 |
| 1 | missing_core_environment | 27 |
| 1 | preliminary_species_core_eligible | 1729 |
| 1 | source_cell_centre_not_marine | 80 |
| 1 | source_cell_centre_not_marine;missing_core_environment | 173 |
| 1 | unverified_species_rank | 267 |
| 1 | unverified_species_rank;missing_core_environment | 6 |
| 1 | unverified_species_rank;source_cell_centre_not_marine | 6 |
| 1 | unverified_species_rank;source_cell_centre_not_marine;missing_core_environment | 65 |

### Species with broad eligible cell support for review

| target_taxon_key | reported_name | eligible_source_records | eligible_distinct_cells | eligible_cell_periods | active_periods |
| --- | --- | --- | --- | --- | --- |
| AphiaID:137206 | Chelonia mydas | 110 | 61 | 71 | 3 |
| AphiaID:343936 | Pelecanus philippensis | 190 | 59 | 81 | 2 |
| AphiaID:220293 | Lepidochelys olivacea | 80 | 59 | 63 | 2 |
| AphiaID:137109 | Stenella longirostris | 79 | 29 | 35 | 3 |
| AphiaID:137207 | Eretmochelys imbricata | 23 | 17 | 18 | 3 |
| AphiaID:137135 | Chlidonias hybrida | 20 | 10 | 10 | 2 |
| AphiaID:159115 | Egretta garzetta | 12 | 10 | 10 | 3 |
| AphiaID:567792 | Onychoprion anaethetus | 15 | 9 | 9 | 2 |
| AphiaID:137090 | Balaenoptera musculus | 11 | 9 | 9 | 3 |
| AphiaID:254983 | Tursiops aduncus | 19 | 8 | 9 | 3 |

These are candidates for group review, not an automatic focal-species choice. Some taxa and records may need ecological, taxonomic and observation-quality assessment.

### Taxon overview (first 15 by eligible record support)

| target_taxon_key | reported_name | original_records | distinct_occupied_cells | eligible_source_records | eligible_distinct_cells | active_periods |
| --- | --- | --- | --- | --- | --- | --- |
| AphiaID:343936 | Pelecanus philippensis | 211 | 71 | 190 | 59 | 2 |
| AphiaID:137206 | Chelonia mydas | 114 | 65 | 110 | 61 | 3 |
| AphiaID:220293 | Lepidochelys olivacea | 83 | 62 | 80 | 59 | 2 |
| AphiaID:137109 | Stenella longirostris | 82 | 32 | 79 | 29 | 3 |
| AphiaID:137207 | Eretmochelys imbricata | 24 | 18 | 23 | 17 | 3 |
| AphiaID:219628 | Acanthurus leucosternon | 22 | 7 | 22 | 7 | 3 |
| AphiaID:137135 | Chlidonias hybrida | 36 | 17 | 20 | 10 | 2 |
| AphiaID:254983 | Tursiops aduncus | 24 | 13 | 19 | 8 | 3 |
| AphiaID:219882 | Melichthys indicus | 18 | 5 | 17 | 4 | 3 |
| AphiaID:159582 | Acanthurus lineatus | 21 | 8 | 16 | 6 | 3 |
| AphiaID:273333 | Chaetodon decussatus | 16 | 6 | 16 | 6 | 3 |
| AphiaID:273914 | Siganus javus | 19 | 11 | 15 | 7 | 2 |
| AphiaID:212606 | Sterna bergii | 17 | 9 | 15 | 8 | 2 |
| AphiaID:567792 | Onychoprion anaethetus | 15 | 9 | 15 | 9 | 2 |
| AphiaID:137136 | Chlidonias leucopterus | 16 | 7 | 15 | 6 | 2 |

## Core environment

Values below are descriptive; units follow source/catalogue conventions. In particular, the oxygen unit notation requires interpretation.

| population | label | feature | n | median | mean | q25 | q75 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| complete_population | 0 | bio_oracle__thetao_mean__depthsurf | 2353 | 29.05377101335928 | 28.998957988603475 | 28.860507456247387 | 29.18026199868728 |
| complete_population | 0 | bio_oracle__so_mean__depthsurf | 2353 | 34.12231140348357 | 33.99168526828917 | 33.54961226565196 | 34.4014740480167 |
| complete_population | 0 | bio_oracle__o2_mean__depthsurf | 2353 | 200.5970786024218 | 200.7357423886736 | 200.0510079262801 | 201.37747454924488 |
| complete_population | 0 | bio_oracle__chl_mean__depthsurf | 2353 | 0.1363398472133075 | 0.1692386893966844 | 0.1278160516682024 | 0.1650759522383309 |
| complete_population | 0 | bio_oracle__ph_mean__depthsurf | 2353 | 8.030829730547339 | 8.035177074641343 | 8.0265694472735 | 8.041898519582627 |
| complete_population | 0 | bio_oracle__bathymetry_mean__benthic | 2353 | -3771.611083984375 | -3311.950467540561 | -4147.5 | -3174.75 |
| complete_population | 1 | bio_oracle__thetao_mean__depthsurf | 2082 | 28.83789008300181 | 28.84512560028925 | 28.58374728806698 | 29.099781714697528 |
| complete_population | 1 | bio_oracle__so_mean__depthsurf | 2082 | 33.85095631337939 | 33.68542415132127 | 33.25660728949061 | 33.96404097797454 |
| complete_population | 1 | bio_oracle__o2_mean__depthsurf | 2082 | 202.10693231077803 | 201.9437516204232 | 202.0215429843423 | 202.57895153369165 |
| complete_population | 1 | bio_oracle__chl_mean__depthsurf | 2082 | 0.2703917021091242 | 0.2515352701624006 | 0.1849159219555895 | 0.2934726085155755 |
| complete_population | 1 | bio_oracle__ph_mean__depthsurf | 2082 | 8.034917055100173 | 8.035917300396282 | 8.026828579552875 | 8.041038405442013 |
| complete_population | 1 | bio_oracle__bathymetry_mean__benthic | 2082 | -15.88888931274414 | -325.8648067581665 | -68.11111450195312 | -7.0 |
| eligible_species_subset | 0 | bio_oracle__thetao_mean__depthsurf | 1729 | 29.085204584748688 | 29.023804547559106 | 28.89502977463847 | 29.191283744931823 |
| eligible_species_subset | 0 | bio_oracle__so_mean__depthsurf | 1729 | 34.13453690149004 | 33.9965156665894 | 33.548281571649426 | 34.40276437976717 |
| eligible_species_subset | 0 | bio_oracle__o2_mean__depthsurf | 1729 | 200.54166504551588 | 200.6641159296953 | 199.96588365585043 | 201.31014307830424 |
| eligible_species_subset | 0 | bio_oracle__chl_mean__depthsurf | 1729 | 0.1361356116084944 | 0.1677868403327348 | 0.1273973773523253 | 0.1657501172377104 |
| eligible_species_subset | 0 | bio_oracle__ph_mean__depthsurf | 1729 | 8.029707700075246 | 8.033204184747348 | 8.02617155527455 | 8.039877933075768 |
| eligible_species_subset | 0 | bio_oracle__bathymetry_mean__benthic | 1729 | -3772.0556640625 | -3326.904843737722 | -4161.52783203125 | -3183.638916015625 |
| eligible_species_subset | 1 | bio_oracle__thetao_mean__depthsurf | 1729 | 28.83789008300181 | 28.84126455143832 | 28.572756906173243 | 29.099781714697528 |
| eligible_species_subset | 1 | bio_oracle__so_mean__depthsurf | 1729 | 33.852661141396474 | 33.712417507974415 | 33.647879457139055 | 33.96404097797454 |
| eligible_species_subset | 1 | bio_oracle__o2_mean__depthsurf | 1729 | 202.0736964631219 | 201.93197961312245 | 202.01175348816827 | 202.57895153369165 |
| eligible_species_subset | 1 | bio_oracle__chl_mean__depthsurf | 1729 | 0.2708744153652111 | 0.2554000866531762 | 0.2206403050448877 | 0.2926034818819104 |
| eligible_species_subset | 1 | bio_oracle__ph_mean__depthsurf | 1729 | 8.030430667615523 | 8.033963351198954 | 8.026706397940089 | 8.040579047231942 |
| eligible_species_subset | 1 | bio_oracle__bathymetry_mean__benthic | 1729 | -14.527777671813965 | -239.3490131167817 | -59.44444274902344 | -7.166666507720947 |

### Six-core complete rows

- Complete population: **4,435**
- Eligible subset: **3,458**
- Of full-population positives, **2,082 / 2,353** have all six core values; backgrounds: **2,353 / 2,353**.
- This asymmetry reflects the candidate construction's six-core completeness rule for sampled backgrounds and must be considered before interpreting class contrasts or choosing preprocessing.
- IQR flags are descriptive only; no values were removed. Median depth and nearshore contrasts require review as potential sampling-domain confounding.

## Correlation screening

- Distinct cell-period profiles: `{"complete_population": 2833, "eligible_species_subset": 2073}`
- Features with period-specific source quarantines in the accepted catalogue: **7**; affected feature-period definitions: **14**.
- High-correlation candidate pairs at |Spearman ρ| ≥ 0.95: **3,602 rows** across cohorts/periods.

### Highest-correlation candidate pairs

| population | period | feature_a | feature_b | spearman_rho | paired_valid_profiles |
| --- | --- | --- | --- | --- | --- |
| complete_population | 2010-2019 | bio_oracle__po4_max__depthsurf | bio_oracle__po4_range__depthsurf | 0.9999978272026776 | 752 |
| eligible_species_subset | 2010-2019 | bio_oracle__po4_max__depthsurf | bio_oracle__po4_range__depthsurf | 0.9999976886972548 | 577 |
| complete_population | 2000-2009 | bio_oracle__no3_max__depthsurf | bio_oracle__no3_range__depthsurf | 0.9999942027561202 | 443 |
| complete_population | 2010-2019 | bio_oracle__no3_max__depthsurf | bio_oracle__no3_range__depthsurf | 0.9999924093184448 | 752 |
| eligible_species_subset | 2010-2019 | bio_oracle__no3_max__depthsurf | bio_oracle__no3_range__depthsurf | 0.9999904424508104 | 577 |
| complete_population | 2000-2009 | bio_oracle__po4_max__depthsurf | bio_oracle__po4_range__depthsurf | 0.9999901998972508 | 443 |
| eligible_species_subset | 2000-2009 | bio_oracle__po4_max__depthsurf | bio_oracle__po4_range__depthsurf | 0.9999880565046764 | 182 |
| eligible_species_subset | 2000-2009 | bio_oracle__no3_max__depthsurf | bio_oracle__no3_range__depthsurf | 0.9999860659221224 | 182 |
| complete_population | 2020-2026 | bio_oracle__no3_max__depthsurf | bio_oracle__no3_range__depthsurf | 0.9999558128084656 | 1580 |
| eligible_species_subset | 2020-2026 | bio_oracle__no3_max__depthsurf | bio_oracle__no3_range__depthsurf | 0.9999533063604572 | 1314 |
| complete_population | 2010-2019 | bio_oracle__mlotst_max__depthsurf | bio_oracle__mlotst_range__depthsurf | 0.999746121295224 | 752 |
| eligible_species_subset | 2010-2019 | bio_oracle__mlotst_max__depthsurf | bio_oracle__mlotst_range__depthsurf | 0.9997322012030414 | 577 |

These are redundancy prompts, not causal relationships or feature-removal decisions. Repeated cells and period-specific environmental slices constrain interpretation.

### Feature-selection investigation candidates

1. Review highly correlated max/range and related summary-statistic pairs within each environmental family, period and raster-cell support.
2. Compare depth and coast-distance contrasts under a scientifically justified accessible marine domain before treating bathymetry or location as predictive signal.
3. Resolve or retain quarantine/missingness treatment for the affected feature-period definitions, and exclude IDs, provenance, target-construction and quality fields from predictor candidates unless a leakage-safe use is justified.

These steps identify what to investigate next; they do not remove or approve features.

## Spatial and sampling diagnostics

- Same-taxon, same-period background-to-nearest-recorded-point distance: median **334.20 km**, p90 **574.01 km** (n=2,353).
- Maximum observed source records in a taxon/cell/period: **36**.
- Coast-distance summaries use raster-cell centres and GSHHG 2.3.7 in a local projected CRS. They are descriptive nearshore/offshore diagnostics; the shoreline is from 2017 and not metre-accuracy current truth.

### Coastline-distance and bathymetry by class/period

| population | period | label | unique_cells | median_distance_to_coast_km | q25_distance_to_coast_km | q75_distance_to_coast_km | median_bathymetry_m |
| --- | --- | --- | --- | --- | --- | --- | --- |
| complete_population | 2000-2009 | 0 | 376 | 239.14889755144753 | 112.16469441008411 | 354.5549829593482 | -3806.1527099609375 |
| complete_population | 2000-2009 | 1 | 70 | 51.56287823157003 | 14.4138513127279 | 148.10317321787207 | -2345.77783203125 |
| complete_population | 2010-2019 | 0 | 596 | 225.18972878321108 | 114.1310772967258 | 332.28541715755927 | -3766.625 |
| complete_population | 2010-2019 | 1 | 171 | 7.596845606401737 | 1.9610942810537246 | 29.670191426609996 | -59.95833206176758 |
| complete_population | 2020-2026 | 0 | 1381 | 225.89970661478486 | 112.49404311454786 | 332.31855718146056 | -3761.25 |
| complete_population | 2020-2026 | 1 | 239 | 3.4226993897961724 | 1.0792654283054965 | 10.061392702003015 | -26.33333396911621 |
| eligible_species_subset | 2000-2009 | 0 | 161 | 260.5901457041961 | 116.98018583766351 | 360.7944509086777 | -3861.97216796875 |
| eligible_species_subset | 2000-2009 | 1 | 21 | 80.68342551740531 | 8.57050962698823 | 209.57314972146898 | -3633.0 |
| eligible_species_subset | 2010-2019 | 0 | 443 | 212.63406765344004 | 110.44673889893178 | 332.59234476047664 | -3761.888916015625 |
| eligible_species_subset | 2010-2019 | 1 | 134 | 8.40580480343257 | 2.959358722425618 | 19.97088990758187 | -57.31944465637207 |
| eligible_species_subset | 2020-2026 | 0 | 1125 | 226.04852006254436 | 113.71566319698707 | 334.07104085770317 | -3766.916748046875 |
| eligible_species_subset | 2020-2026 | 1 | 189 | 5.766224408881186 | 1.7882738616684772 | 11.07877065297166 | -26.33333396911621 |

## Source quarantines and interpretation limits

- The accepted feature catalogue records **7 feature definitions** with quarantined period(s); **14 feature-period definitions** are affected. All **382** columns remain present, including quarantined definitions.
- 2020–2026 environmental assignment uses SSP245 2020 projected data; it is not an annual measurement.
- A 1:1 sample class ratio does not represent prevalence. Environmental separation does not establish biological absence or causal habitat preference.
- Do not treat repeated occurrence records as independent cells, interpret maps as suitability, or include identifiers/lineage/quality fields as predictors without leakage review.

## Evidence artefacts

- **16 CSV tables**: [`reports/eda/tables/`](../../reports/eda/tables/)
- **8 figures**: [`reports/eda/figures/`](../../reports/eda/figures/)
- Machine-readable summary: [`2026-10-16-eda-summary.json`](2026-10-16-eda-summary.json)
- Insight log: [`2026-10-16-eda-insight-log.md`](2026-10-16-eda-insight-log.md)

## Next evidence gate

Review candidate species using independent occupied-cell support, agree an accessible marine background domain and a cell-grouped spatial validation design, then justify any feature handling within training folds. No species was selected automatically. No splitting, imputation, scaling, feature deletion or model training occurred.

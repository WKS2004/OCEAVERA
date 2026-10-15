# OBIS–Bio-ORACLE source variable catalog

Catalog generated from the cleaned Bio-ORACLE manifest and the actual selected NetCDF metadata. Product titles establish declared scenario and depth; the NetCDF time coordinate establishes the selected slice.

- Cleaned source products inventoried: **356**
- Products selected for integration: **106** (55 baseline, 50 SSP245, one static terrain product)
- Distinct NetCDF variable names: **139**
- Output feature columns: **382**
- Future scenario selected for 2020–2026: **SSP245**, using actual time coordinate 2020.
- Baseline slices: actual time coordinates 2000 and 2010.
- Static terrain is recorded as benthic/static from the NetCDF title; its 1970 time label is not treated as an observation year.

## Feature columns by depth

| Depth declared in NetCDF title | Feature columns |
| --- | ---: |
| benthic | 10 |
| depthmax | 81 |
| depthmean | 81 |
| depthmin | 81 |
| depthsurf | 129 |

## Feature inventory

| Output column | NetCDF variable | Depth | Units | Baseline slices | SSP245 slice |
| --- | --- | --- | --- | --- | --- |
| `bio_oracle__area__benthic` | `area` | benthic | m2 | — | — |
| `bio_oracle__aspect__benthic` | `aspect` | benthic | degree | — | — |
| `bio_oracle__bathymetry_max__benthic` | `bathymetry_max` | benthic | m | — | — |
| `bio_oracle__bathymetry_mean__benthic` | `bathymetry_mean` | benthic | m | — | — |
| `bio_oracle__bathymetry_min__benthic` | `bathymetry_min` | benthic | m | — | — |
| `bio_oracle__chl_ltmax__depthmax` | `chl_ltmax` | depthmax | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_ltmax__depthmean` | `chl_ltmax` | depthmean | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_ltmax__depthmin` | `chl_ltmax` | depthmin | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_ltmax__depthsurf` | `chl_ltmax` | depthsurf | mg m-3 | 2000, 2010 | 2020 |
| `bio_oracle__chl_ltmin__depthmax` | `chl_ltmin` | depthmax | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_ltmin__depthmean` | `chl_ltmin` | depthmean | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_ltmin__depthmin` | `chl_ltmin` | depthmin | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_ltmin__depthsurf` | `chl_ltmin` | depthsurf | mg m-3 | 2000, 2010 | 2020 |
| `bio_oracle__chl_max__depthmax` | `chl_max` | depthmax | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_max__depthmean` | `chl_max` | depthmean | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_max__depthmin` | `chl_max` | depthmin | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_max__depthsurf` | `chl_max` | depthsurf | mg m-3 | 2000, 2010 | 2020 |
| `bio_oracle__chl_mean__depthmax` | `chl_mean` | depthmax | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_mean__depthmean` | `chl_mean` | depthmean | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_mean__depthmin` | `chl_mean` | depthmin | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_mean__depthsurf` | `chl_mean` | depthsurf | mg m-3 | 2000, 2010 | 2020 |
| `bio_oracle__chl_min__depthmax` | `chl_min` | depthmax | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_min__depthmean` | `chl_min` | depthmean | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_min__depthmin` | `chl_min` | depthmin | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_min__depthsurf` | `chl_min` | depthsurf | mg m-3 | 2000, 2010 | 2020 |
| `bio_oracle__chl_range__depthmax` | `chl_range` | depthmax | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_range__depthmean` | `chl_range` | depthmean | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_range__depthmin` | `chl_range` | depthmin | mg m-3 | 2000, 2010 | — |
| `bio_oracle__chl_range__depthsurf` | `chl_range` | depthsurf | mg m-3 | 2000, 2010 | 2020 |
| `bio_oracle__chl_sd__depthsurf` | `chl_sd` | depthsurf | mg m-3 | — | 2020 |
| `bio_oracle__clt_ltmax__depthsurf` | `clt_ltmax` | depthsurf | (0 - 1) | 2000, 2010 | 2020 |
| `bio_oracle__clt_ltmin__depthsurf` | `clt_ltmin` | depthsurf | (0 - 1) | 2000, 2010 | 2020 |
| `bio_oracle__clt_max__depthsurf` | `clt_max` | depthsurf | (0 - 1) | 2000, 2010 | 2020 |
| `bio_oracle__clt_mean__depthsurf` | `clt_mean` | depthsurf | (0 - 1) | 2000, 2010 | 2020 |
| `bio_oracle__clt_min__depthsurf` | `clt_min` | depthsurf | (0 - 1) | 2000, 2010 | 2020 |
| `bio_oracle__clt_range__depthsurf` | `clt_range` | depthsurf | (0 - 1) | 2000, 2010 | 2020 |
| `bio_oracle__clt_sd__depthsurf` | `clt_sd` | depthsurf | 1 | — | 2020 |
| `bio_oracle__coastline__benthic` | `coastline` | benthic | 1 | — | — |
| `bio_oracle__dfe_ltmax__depthmax` | `dfe_ltmax` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_ltmax__depthmean` | `dfe_ltmax` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_ltmax__depthmin` | `dfe_ltmax` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_ltmax__depthsurf` | `dfe_ltmax` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_ltmin__depthmax` | `dfe_ltmin` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_ltmin__depthmean` | `dfe_ltmin` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_ltmin__depthmin` | `dfe_ltmin` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_ltmin__depthsurf` | `dfe_ltmin` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_max__depthmax` | `dfe_max` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_max__depthmean` | `dfe_max` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_max__depthmin` | `dfe_max` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_max__depthsurf` | `dfe_max` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_mean__depthmax` | `dfe_mean` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_mean__depthmean` | `dfe_mean` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_mean__depthmin` | `dfe_mean` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_mean__depthsurf` | `dfe_mean` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_min__depthmax` | `dfe_min` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_min__depthmean` | `dfe_min` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_min__depthmin` | `dfe_min` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_min__depthsurf` | `dfe_min` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_range__depthmax` | `dfe_range` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_range__depthmean` | `dfe_range` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_range__depthmin` | `dfe_range` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_range__depthsurf` | `dfe_range` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__dfe_sd__depthmax` | `dfe_sd` | depthmax | MMol' 'M-3 | — | 2020 |
| `bio_oracle__dfe_sd__depthmean` | `dfe_sd` | depthmean | MMol' 'M-3 | — | 2020 |
| `bio_oracle__dfe_sd__depthmin` | `dfe_sd` | depthmin | MMol' 'M-3 | — | 2020 |
| `bio_oracle__dfe_sd__depthsurf` | `dfe_sd` | depthsurf | MMol' 'M-3 | — | 2020 |
| `bio_oracle__kdpar_mean_ltmax__depthsurf` | `kdpar_mean_ltmax` | depthsurf | m-1 | 2000, 2010 | — |
| `bio_oracle__kdpar_mean_ltmin__depthsurf` | `kdpar_mean_ltmin` | depthsurf | m-1 | 2000, 2010 | — |
| `bio_oracle__kdpar_mean_max__depthsurf` | `kdpar_mean_max` | depthsurf | m-1 | 2000, 2010 | — |
| `bio_oracle__kdpar_mean_mean__depthsurf` | `kdpar_mean_mean` | depthsurf | m-1 | 2000, 2010 | — |
| `bio_oracle__kdpar_mean_min__depthsurf` | `kdpar_mean_min` | depthsurf | m-1 | 2000, 2010 | — |
| `bio_oracle__kdpar_mean_range__depthsurf` | `kdpar_mean_range` | depthsurf | m-1 | 2000, 2010 | — |
| `bio_oracle__landmass__benthic` | `landmass` | benthic | 1 | — | — |
| `bio_oracle__mlotst_ltmax__depthsurf` | `mlotst_ltmax` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__mlotst_ltmin__depthsurf` | `mlotst_ltmin` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__mlotst_max__depthsurf` | `mlotst_max` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__mlotst_mean__depthsurf` | `mlotst_mean` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__mlotst_min__depthsurf` | `mlotst_min` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__mlotst_range__depthsurf` | `mlotst_range` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__mlotst_sd__depthsurf` | `mlotst_sd` | depthsurf | m | — | 2020 |
| `bio_oracle__no3_ltmax__depthmax` | `no3_ltmax` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_ltmax__depthmean` | `no3_ltmax` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_ltmax__depthmin` | `no3_ltmax` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_ltmax__depthsurf` | `no3_ltmax` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_ltmin__depthmax` | `no3_ltmin` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_ltmin__depthmean` | `no3_ltmin` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_ltmin__depthmin` | `no3_ltmin` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_ltmin__depthsurf` | `no3_ltmin` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_max__depthmax` | `no3_max` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_max__depthmean` | `no3_max` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_max__depthmin` | `no3_max` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_max__depthsurf` | `no3_max` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_mean__depthmax` | `no3_mean` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_mean__depthmean` | `no3_mean` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_mean__depthmin` | `no3_mean` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_mean__depthsurf` | `no3_mean` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_min__depthmax` | `no3_min` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_min__depthmean` | `no3_min` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_min__depthmin` | `no3_min` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_min__depthsurf` | `no3_min` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_range__depthmax` | `no3_range` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_range__depthmean` | `no3_range` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_range__depthmin` | `no3_range` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_range__depthsurf` | `no3_range` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__no3_sd__depthmax` | `no3_sd` | depthmax | MMol' 'M-3 | — | 2020 |
| `bio_oracle__no3_sd__depthmean` | `no3_sd` | depthmean | MMol' 'M-3 | — | 2020 |
| `bio_oracle__no3_sd__depthmin` | `no3_sd` | depthmin | MMol' 'M-3 | — | 2020 |
| `bio_oracle__no3_sd__depthsurf` | `no3_sd` | depthsurf | MMol' 'M-3 | — | 2020 |
| `bio_oracle__o2_ltmax__depthmax` | `o2_ltmax` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_ltmax__depthmean` | `o2_ltmax` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_ltmax__depthmin` | `o2_ltmax` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_ltmax__depthsurf` | `o2_ltmax` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_ltmin__depthmax` | `o2_ltmin` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_ltmin__depthmean` | `o2_ltmin` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_ltmin__depthmin` | `o2_ltmin` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_ltmin__depthsurf` | `o2_ltmin` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_max__depthmax` | `o2_max` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_max__depthmean` | `o2_max` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_max__depthmin` | `o2_max` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_max__depthsurf` | `o2_max` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_mean__depthmax` | `o2_mean` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_mean__depthmean` | `o2_mean` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_mean__depthmin` | `o2_mean` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_mean__depthsurf` | `o2_mean` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_min__depthmax` | `o2_min` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_min__depthmean` | `o2_min` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_min__depthmin` | `o2_min` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_min__depthsurf` | `o2_min` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_range__depthmax` | `o2_range` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_range__depthmean` | `o2_range` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_range__depthmin` | `o2_range` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_range__depthsurf` | `o2_range` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__o2_sd__depthmax` | `o2_sd` | depthmax | MMol' 'M-3 | — | 2020 |
| `bio_oracle__o2_sd__depthmean` | `o2_sd` | depthmean | MMol' 'M-3 | — | 2020 |
| `bio_oracle__o2_sd__depthmin` | `o2_sd` | depthmin | MMol' 'M-3 | — | 2020 |
| `bio_oracle__o2_sd__depthsurf` | `o2_sd` | depthsurf | MMol' 'M-3 | — | 2020 |
| `bio_oracle__par_mean_ltmax__depthsurf` | `par_mean_ltmax` | depthsurf | einstein/m2/day | 2000, 2010 | — |
| `bio_oracle__par_mean_ltmin__depthsurf` | `par_mean_ltmin` | depthsurf | einstein/m2/day | 2000, 2010 | — |
| `bio_oracle__par_mean_max__depthsurf` | `par_mean_max` | depthsurf | einstein/m2/day | 2000, 2010 | — |
| `bio_oracle__par_mean_mean__depthsurf` | `par_mean_mean` | depthsurf | einstein/m2/day | 2000, 2010 | — |
| `bio_oracle__par_mean_min__depthsurf` | `par_mean_min` | depthsurf | einstein/m2/day | 2000, 2010 | — |
| `bio_oracle__par_mean_range__depthsurf` | `par_mean_range` | depthsurf | einstein/m2/day | 2000, 2010 | — |
| `bio_oracle__ph_ltmax__depthmax` | `ph_ltmax` | depthmax | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_ltmax__depthmean` | `ph_ltmax` | depthmean | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_ltmax__depthmin` | `ph_ltmax` | depthmin | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_ltmax__depthsurf` | `ph_ltmax` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_ltmin__depthmax` | `ph_ltmin` | depthmax | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_ltmin__depthmean` | `ph_ltmin` | depthmean | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_ltmin__depthmin` | `ph_ltmin` | depthmin | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_ltmin__depthsurf` | `ph_ltmin` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_max__depthmax` | `ph_max` | depthmax | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_max__depthmean` | `ph_max` | depthmean | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_max__depthmin` | `ph_max` | depthmin | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_max__depthsurf` | `ph_max` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_mean__depthmax` | `ph_mean` | depthmax | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_mean__depthmean` | `ph_mean` | depthmean | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_mean__depthmin` | `ph_mean` | depthmin | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_mean__depthsurf` | `ph_mean` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_min__depthmax` | `ph_min` | depthmax | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_min__depthmean` | `ph_min` | depthmean | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_min__depthmin` | `ph_min` | depthmin | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_min__depthsurf` | `ph_min` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_range__depthmax` | `ph_range` | depthmax | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_range__depthmean` | `ph_range` | depthmean | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_range__depthmin` | `ph_range` | depthmin | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_range__depthsurf` | `ph_range` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__ph_sd__depthmax` | `ph_sd` | depthmax | 1 | — | 2020 |
| `bio_oracle__ph_sd__depthmean` | `ph_sd` | depthmean | 1 | — | 2020 |
| `bio_oracle__ph_sd__depthmin` | `ph_sd` | depthmin | 1 | — | 2020 |
| `bio_oracle__ph_sd__depthsurf` | `ph_sd` | depthsurf | 1 | — | 2020 |
| `bio_oracle__phyc_ltmax__depthmax` | `phyc_ltmax` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_ltmax__depthmean` | `phyc_ltmax` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_ltmax__depthmin` | `phyc_ltmax` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_ltmax__depthsurf` | `phyc_ltmax` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_ltmin__depthmax` | `phyc_ltmin` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_ltmin__depthmean` | `phyc_ltmin` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_ltmin__depthmin` | `phyc_ltmin` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_ltmin__depthsurf` | `phyc_ltmin` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_max__depthmax` | `phyc_max` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_max__depthmean` | `phyc_max` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_max__depthmin` | `phyc_max` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_max__depthsurf` | `phyc_max` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_mean__depthmax` | `phyc_mean` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_mean__depthmean` | `phyc_mean` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_mean__depthmin` | `phyc_mean` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_mean__depthsurf` | `phyc_mean` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_min__depthmax` | `phyc_min` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_min__depthmean` | `phyc_min` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_min__depthmin` | `phyc_min` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_min__depthsurf` | `phyc_min` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_range__depthmax` | `phyc_range` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_range__depthmean` | `phyc_range` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_range__depthmin` | `phyc_range` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_range__depthsurf` | `phyc_range` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__phyc_sd__depthmax` | `phyc_sd` | depthmax | MMol' 'M-3 | — | 2020 |
| `bio_oracle__phyc_sd__depthmean` | `phyc_sd` | depthmean | MMol' 'M-3 | — | 2020 |
| `bio_oracle__phyc_sd__depthmin` | `phyc_sd` | depthmin | MMol' 'M-3 | — | 2020 |
| `bio_oracle__phyc_sd__depthsurf` | `phyc_sd` | depthsurf | MMol' 'M-3 | — | 2020 |
| `bio_oracle__po4_ltmax__depthmax` | `po4_ltmax` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_ltmax__depthmean` | `po4_ltmax` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_ltmax__depthmin` | `po4_ltmax` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_ltmax__depthsurf` | `po4_ltmax` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_ltmin__depthmax` | `po4_ltmin` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_ltmin__depthmean` | `po4_ltmin` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_ltmin__depthmin` | `po4_ltmin` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_ltmin__depthsurf` | `po4_ltmin` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_max__depthmax` | `po4_max` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_max__depthmean` | `po4_max` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_max__depthmin` | `po4_max` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_max__depthsurf` | `po4_max` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_mean__depthmax` | `po4_mean` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_mean__depthmean` | `po4_mean` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_mean__depthmin` | `po4_mean` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_mean__depthsurf` | `po4_mean` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_min__depthmax` | `po4_min` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_min__depthmean` | `po4_min` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_min__depthmin` | `po4_min` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_min__depthsurf` | `po4_min` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_range__depthmax` | `po4_range` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_range__depthmean` | `po4_range` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_range__depthmin` | `po4_range` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_range__depthsurf` | `po4_range` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__po4_sd__depthmax` | `po4_sd` | depthmax | MMol' 'M-3 | — | 2020 |
| `bio_oracle__po4_sd__depthmean` | `po4_sd` | depthmean | MMol' 'M-3 | — | 2020 |
| `bio_oracle__po4_sd__depthmin` | `po4_sd` | depthmin | MMol' 'M-3 | — | 2020 |
| `bio_oracle__po4_sd__depthsurf` | `po4_sd` | depthsurf | MMol' 'M-3 | — | 2020 |
| `bio_oracle__si_ltmax__depthmax` | `si_ltmax` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_ltmax__depthmean` | `si_ltmax` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_ltmax__depthmin` | `si_ltmax` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_ltmax__depthsurf` | `si_ltmax` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_ltmin__depthmax` | `si_ltmin` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_ltmin__depthmean` | `si_ltmin` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_ltmin__depthmin` | `si_ltmin` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_ltmin__depthsurf` | `si_ltmin` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_max__depthmax` | `si_max` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_max__depthmean` | `si_max` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_max__depthmin` | `si_max` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_max__depthsurf` | `si_max` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_mean__depthmax` | `si_mean` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_mean__depthmean` | `si_mean` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_mean__depthmin` | `si_mean` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_mean__depthsurf` | `si_mean` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_min__depthmax` | `si_min` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_min__depthmean` | `si_min` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_min__depthmin` | `si_min` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_min__depthsurf` | `si_min` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_range__depthmax` | `si_range` | depthmax | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_range__depthmean` | `si_range` | depthmean | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_range__depthmin` | `si_range` | depthmin | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_range__depthsurf` | `si_range` | depthsurf | MMol' 'M-3 | 2000, 2010 | 2020 |
| `bio_oracle__si_sd__depthmax` | `si_sd` | depthmax | MMol' 'M-3 | — | 2020 |
| `bio_oracle__si_sd__depthmean` | `si_sd` | depthmean | MMol' 'M-3 | — | 2020 |
| `bio_oracle__si_sd__depthmin` | `si_sd` | depthmin | MMol' 'M-3 | — | 2020 |
| `bio_oracle__si_sd__depthsurf` | `si_sd` | depthsurf | MMol' 'M-3 | — | 2020 |
| `bio_oracle__siconc_ltmax__depthsurf` | `siconc_ltmax` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__siconc_ltmin__depthsurf` | `siconc_ltmin` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__siconc_max__depthsurf` | `siconc_max` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__siconc_mean__depthsurf` | `siconc_mean` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__siconc_min__depthsurf` | `siconc_min` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__siconc_range__depthsurf` | `siconc_range` | depthsurf | 1 | 2000, 2010 | 2020 |
| `bio_oracle__siconc_sd__depthsurf` | `siconc_sd` | depthsurf | 1 | — | 2020 |
| `bio_oracle__sithick_ltmax__depthsurf` | `sithick_ltmax` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__sithick_ltmin__depthsurf` | `sithick_ltmin` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__sithick_max__depthsurf` | `sithick_max` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__sithick_mean__depthsurf` | `sithick_mean` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__sithick_min__depthsurf` | `sithick_min` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__sithick_range__depthsurf` | `sithick_range` | depthsurf | m | 2000, 2010 | 2020 |
| `bio_oracle__sithick_sd__depthsurf` | `sithick_sd` | depthsurf | m | — | 2020 |
| `bio_oracle__slope__benthic` | `slope` | benthic | degree | — | — |
| `bio_oracle__so_ltmax__depthmax` | `so_ltmax` | depthmax | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_ltmax__depthmean` | `so_ltmax` | depthmean | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_ltmax__depthmin` | `so_ltmax` | depthmin | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_ltmax__depthsurf` | `so_ltmax` | depthsurf | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_ltmin__depthmax` | `so_ltmin` | depthmax | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_ltmin__depthmean` | `so_ltmin` | depthmean | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_ltmin__depthmin` | `so_ltmin` | depthmin | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_ltmin__depthsurf` | `so_ltmin` | depthsurf | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_max__depthmax` | `so_max` | depthmax | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_max__depthmean` | `so_max` | depthmean | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_max__depthmin` | `so_max` | depthmin | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_max__depthsurf` | `so_max` | depthsurf | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_mean__depthmax` | `so_mean` | depthmax | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_mean__depthmean` | `so_mean` | depthmean | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_mean__depthmin` | `so_mean` | depthmin | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_mean__depthsurf` | `so_mean` | depthsurf | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_min__depthmax` | `so_min` | depthmax | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_min__depthmean` | `so_min` | depthmean | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_min__depthmin` | `so_min` | depthmin | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_min__depthsurf` | `so_min` | depthsurf | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_range__depthmax` | `so_range` | depthmax | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_range__depthmean` | `so_range` | depthmean | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_range__depthmin` | `so_range` | depthmin | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_range__depthsurf` | `so_range` | depthsurf | PSU | 2000, 2010 | 2020 |
| `bio_oracle__so_sd__depthmax` | `so_sd` | depthmax | 1e-3 | — | 2020 |
| `bio_oracle__so_sd__depthmean` | `so_sd` | depthmean | 1e-3 | — | 2020 |
| `bio_oracle__so_sd__depthmin` | `so_sd` | depthmin | 1e-3 | — | 2020 |
| `bio_oracle__so_sd__depthsurf` | `so_sd` | depthsurf | 1e-3 | — | 2020 |
| `bio_oracle__swd_ltmax__depthmax` | `swd_ltmax` | depthmax | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_ltmax__depthmean` | `swd_ltmax` | depthmean | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_ltmax__depthmin` | `swd_ltmax` | depthmin | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_ltmax__depthsurf` | `swd_ltmax` | depthsurf | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_ltmin__depthmax` | `swd_ltmin` | depthmax | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_ltmin__depthmean` | `swd_ltmin` | depthmean | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_ltmin__depthmin` | `swd_ltmin` | depthmin | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_ltmin__depthsurf` | `swd_ltmin` | depthsurf | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_max__depthmax` | `swd_max` | depthmax | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_max__depthmean` | `swd_max` | depthmean | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_max__depthmin` | `swd_max` | depthmin | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_max__depthsurf` | `swd_max` | depthsurf | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_mean__depthmax` | `swd_mean` | depthmax | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_mean__depthmean` | `swd_mean` | depthmean | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_mean__depthmin` | `swd_mean` | depthmin | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_mean__depthsurf` | `swd_mean` | depthsurf | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_min__depthmax` | `swd_min` | depthmax | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_min__depthmean` | `swd_min` | depthmean | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_min__depthmin` | `swd_min` | depthmin | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_min__depthsurf` | `swd_min` | depthsurf | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_range__depthmax` | `swd_range` | depthmax | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_range__depthmean` | `swd_range` | depthmean | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_range__depthmin` | `swd_range` | depthmin | degree | 2000, 2010 | 2020 |
| `bio_oracle__swd_range__depthsurf` | `swd_range` | depthsurf | degree | 2000, 2010 | 2020 |
| `bio_oracle__sws_ltmax__depthmax` | `sws_ltmax` | depthmax | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_ltmax__depthmean` | `sws_ltmax` | depthmean | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_ltmax__depthmin` | `sws_ltmax` | depthmin | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_ltmax__depthsurf` | `sws_ltmax` | depthsurf | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_ltmin__depthmax` | `sws_ltmin` | depthmax | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_ltmin__depthmean` | `sws_ltmin` | depthmean | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_ltmin__depthmin` | `sws_ltmin` | depthmin | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_ltmin__depthsurf` | `sws_ltmin` | depthsurf | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_max__depthmax` | `sws_max` | depthmax | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_max__depthmean` | `sws_max` | depthmean | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_max__depthmin` | `sws_max` | depthmin | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_max__depthsurf` | `sws_max` | depthsurf | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_mean__depthmax` | `sws_mean` | depthmax | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_mean__depthmean` | `sws_mean` | depthmean | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_mean__depthmin` | `sws_mean` | depthmin | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_mean__depthsurf` | `sws_mean` | depthsurf | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_min__depthmax` | `sws_min` | depthmax | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_min__depthmean` | `sws_min` | depthmean | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_min__depthmin` | `sws_min` | depthmin | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_min__depthsurf` | `sws_min` | depthsurf | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_range__depthmax` | `sws_range` | depthmax | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_range__depthmean` | `sws_range` | depthmean | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_range__depthmin` | `sws_range` | depthmin | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__sws_range__depthsurf` | `sws_range` | depthsurf | m s**-1 | 2000, 2010 | 2020 |
| `bio_oracle__tas_ltmax__depthsurf` | `tas_ltmax` | depthsurf | K | 2000, 2010 | 2020 |
| `bio_oracle__tas_ltmin__depthsurf` | `tas_ltmin` | depthsurf | K | 2000, 2010 | 2020 |
| `bio_oracle__tas_max__depthsurf` | `tas_max` | depthsurf | K | 2000, 2010 | 2020 |
| `bio_oracle__tas_mean__depthsurf` | `tas_mean` | depthsurf | K | 2000, 2010 | 2020 |
| `bio_oracle__tas_min__depthsurf` | `tas_min` | depthsurf | K | 2000, 2010 | 2020 |
| `bio_oracle__tas_range__depthsurf` | `tas_range` | depthsurf | K | 2000, 2010 | 2020 |
| `bio_oracle__tas_sd__depthsurf` | `tas_sd` | depthsurf | degree_C | — | 2020 |
| `bio_oracle__terrain_ruggedness_index__benthic` | `terrain_ruggedness_index` | benthic | 1 | — | — |
| `bio_oracle__thetao_ltmax__depthmax` | `thetao_ltmax` | depthmax | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_ltmax__depthmean` | `thetao_ltmax` | depthmean | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_ltmax__depthmin` | `thetao_ltmax` | depthmin | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_ltmax__depthsurf` | `thetao_ltmax` | depthsurf | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_ltmin__depthmax` | `thetao_ltmin` | depthmax | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_ltmin__depthmean` | `thetao_ltmin` | depthmean | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_ltmin__depthmin` | `thetao_ltmin` | depthmin | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_ltmin__depthsurf` | `thetao_ltmin` | depthsurf | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_max__depthmax` | `thetao_max` | depthmax | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_max__depthmean` | `thetao_max` | depthmean | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_max__depthmin` | `thetao_max` | depthmin | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_max__depthsurf` | `thetao_max` | depthsurf | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_mean__depthmax` | `thetao_mean` | depthmax | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_mean__depthmean` | `thetao_mean` | depthmean | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_mean__depthmin` | `thetao_mean` | depthmin | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_mean__depthsurf` | `thetao_mean` | depthsurf | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_min__depthmax` | `thetao_min` | depthmax | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_min__depthmean` | `thetao_min` | depthmean | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_min__depthmin` | `thetao_min` | depthmin | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_min__depthsurf` | `thetao_min` | depthsurf | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_range__depthmax` | `thetao_range` | depthmax | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_range__depthmean` | `thetao_range` | depthmean | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_range__depthmin` | `thetao_range` | depthmin | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_range__depthsurf` | `thetao_range` | depthsurf | degree_C | 2000, 2010 | 2020 |
| `bio_oracle__thetao_sd__depthmax` | `thetao_sd` | depthmax | degree_C | — | 2020 |
| `bio_oracle__thetao_sd__depthmean` | `thetao_sd` | depthmean | degree_C | — | 2020 |
| `bio_oracle__thetao_sd__depthmin` | `thetao_sd` | depthmin | degree_C | — | 2020 |
| `bio_oracle__thetao_sd__depthsurf` | `thetao_sd` | depthsurf | degree_C | — | 2020 |
| `bio_oracle__topographic_position_index__benthic` | `topographic_position_index` | benthic | 1 | — | — |

The machine-readable record includes all 356 product identities, source checksums, variable metadata, and selected time coordinates. Environmental feature columns remain null when the matching depth/statistic/scenario counterpart is not supplied.
A selected product carrying `review_required` remains flagged because the cleaning review concerns the unresolved marine mask and a masked source cell. The missing value remains null; the candidate non-fill domain is not interpreted as a marine mask.

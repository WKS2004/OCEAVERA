# Decision D-053 — Complete integration with source quarantines and GSHHG verification

> **Historical marine-policy status:** D-053's strict uncertainty-footprint exclusions produced the archived strict-policy counts and outputs. [D-054](2026-10-16-decision-policy-b-marine-water-centre.md) supersedes that rule for current marine/grid outputs. D-053's source integration, temporal correction, GSHHG provenance and environmental quarantines remain in force.

- **Date:** 16 October 2026
- **Status:** Implemented at the user's explicit request. Pipeline execution is complete; scientific acceptance is conditional on the documented source limitations and later group review.
- **Purpose:** Correct confirmed integration/date defects and complete the existing two-script processing architecture.
- **Supersedes:** [D-052](2026-10-16-decision-integration-filtering-corrections.md) for current output interpretation. [Pre-completion evidence](2026-10-16-pre-completion-evidence.json) preserves the preceding reports and code.

## Evidence and options

Original and cleaned selected NetCDF products are byte-identical. Baseline absolute air temperatures declare Kelvin but contain Celsius-like values; original temperature ranges have a negative offset; future cloud-fraction standard deviations have unresolved scale/statistic semantics. Guessing corrected measurements was rejected. Preserve sources and feature definitions, publish affected values as null, and document per-period quarantine reasons. SSP245 absolute Celsius values remain unchanged. No earlier cleaning stage is rewritten.

OBIS numeric date_start/date_mid/date_end are interpreted as epoch milliseconds regardless of magnitude. Year/date_year remain year fields. The correction resolves 266 false ambiguities and rejects one year=0 placeholder; 22 genuinely conflicting date records remain archived and excluded. The retained 9,681 observation identities are unchanged.

## Geographical policy and scope

Use official GSHHG 2.3.7 full-resolution L1 outer coastlines, inspect L2-L4 and retain enclosed inland waters as excluded. Subtract land from D-048's established collection rectangle. This authorises processing in the existing envelope; it neither clips to Sri Lanka's EEZ nor establishes a final modelling domain. Prepare the source once and validate the reusable GeoPackage against tracked provenance on ordinary runs. A missing/invalid source remains an explicit blocker.

Exclude exact ON_LAND/MARINE_UNSURE tags, invalid coordinates/flags and non-water centres. Test positive known uncertainties with WGS84 geodesic footprints. Exclude known footprints intersecting land/coast or extending beyond the reference. Retain unknown uncertainty explicitly as point-coordinate verification only; never infer zero uncertainty. Report the stricter known-confidence subset separately.

## Executed outputs and limits

The full table has 23,371 rows and 382 feature definitions; temporal output has 9,681 rows. Marine and individual grid outputs each have 1,299 rows, including 709 known-confidence footprints and 590 unknown-uncertainty points. The 667 summary rows represent 1,006 species-rank records across species/cell/period keys; 293 non-groupable records remain in the individual file. Counts are recorded observations, not abundance.

All five datasets were interim GeoParquet 1.1.0, EPSG:4326 and ZSTD under the former strict rule. No species choice, target construction, preprocessing or model was introduced. See the [historical technical report](2026-10-16-integration-final-technical-report.md), [machine summary](2026-10-16-integration-final-technical-report.json), [source provenance](2026-10-16-gshhg-marine-reference.json), [independent environmental verification](2026-10-16-independent-environmental-verification.md) and [archived strict spatial report](2026-10-16-spatial-grid-report-strict-policy.md). Current marine results are in [D-054](2026-10-16-decision-policy-b-marine-water-centre.md).

Attribution follows the user's established instruction: integration/cleaning corrections to Adithya Gunawardana (AdithyaGunawardana), spatial integration/reference/grid work to Ushan Srinuka (Ushan-Srinuka). Retained agent work does not establish human acceptance.

# Project overview and scope

| Field | Value |
| --- | --- |
| Project | OCEAVERA - Marine Habitat Intelligence |
| Course | IT3091 Machine Learning |
| Group | 2026-AI-45 |
| Document status | Working baseline from the initial group submission |
| Proposal date | 17 September 2026 |

## 1. Purpose

OCEAVERA is the proposed marine machine-learning workstream associated with BLUEVERSE, a broader project framed around coastal tourism and marine resilience. The assignment will develop and evaluate a bounded species-distribution capability that could later contribute biodiversity information to BLUEVERSE.

## 2. Problem context

Marine species occurrence varies with environmental conditions. The group proposes combining historical occurrence observations with marine environmental data to investigate spatial patterns for a selected species.

**Proposed research question**

Given the marine environmental conditions at a location, can historical observations support an estimate of that location's relative suitability for a selected marine species?

## 3. Decision context

- **Primary lens:** Marine Resilience.
- **Secondary lens:** Coastal Tourism, as a potential BLUEVERSE application context.
- **Stakeholder and decision:** not yet specified. The project must identify who would use the output, which decision it could inform, and what practical value it provides.
- **Track:** the initial proposal selects Industry Explorer to investigate a real marine-data problem within the BLUEVERSE context. Prior approval is required; no approval record is present in the repository.

Marine Resilience is the primary lens because the target concerns species distribution and habitat conditions. Coastal Tourism supplies a possible later application for biodiversity information within BLUEVERSE; it is coherent only where it strengthens that marine decision context.

The secondary lens does not create a second ML task in the current scope.

## 4. Proposed analytical scope

### Included

- Choose one focal species, or a small number only when data and scope justify it.
- Define a manageable marine study area; Sri Lanka is the initial preference, but no exact modelling boundary is set. OBIS Area 230 is finalised for biological collection under [D-034](decision-register.md). The current API JSON and CSV collection method follows [D-036](decision-register.md); it does not make Area 230 the final modelling domain or the exact EEZ polygon.
- Assess OBIS species occurrences and candidate Bio-ORACLE environmental layers.
- Construct a spatially integrated dataset and justify its target and background or pseudo-absence design.
- Establish a simple baseline and compare it with at least three alternative methods.
- Evaluate, interpret, and communicate the model's limits; produce a spatial suitability output if supported by the data.

### Excluded from the current assignment proposal

- Real-time prediction or operational deployment.
- Future-climate projection.
- A complete BLUEVERSE platform implementation.
- Additional marine models outside the selected species-distribution task.

## 5. Data and unit of analysis

| Element | Initial proposal | Decision still required |
| --- | --- | --- |
| Biological source | OBIS marine occurrence records | Focal taxon, downstream modelling-population filters, temporal coverage, quality rules, sampling bias, citation, and data-use terms |
| Environmental source | Bio-ORACLE marine data layers | Exact layer/version, units, resolution, time period, depth context, missingness, and matching method |
| Unit of analysis | Marine spatial observation or location with environmental variables and occurrence or constructed target | Point or grid cell, spatial resolution, study boundary, marine mask, and repeated-record handling |
| Target | Species occurrence or constructed presence/background label | Meaning of a positive and comparison sample; treatment of records that were not observed |
| Output | Occurrence score or habitat-suitability representation | Intended user, geographic domain, uncertainty communication, and whether probability calibration is supportable |

The initial full OBIS collection uses all records for Area 230, including absence and dropped records, before any focal-species or record-selection decision. The current API JSON and CSV acquisition is recorded in the [Area 230 source record](../records/2026-10-08-source-obis-area-230-api-csv.md). This does not decide which records form a later modelling population.

The proposal lists these candidate feature families, subject to actual layer availability and compatibility:

| Family | Candidate variables |
| --- | --- |
| Physical | Temperature, salinity, water velocity, bathymetry, seabed/topographic characteristics |
| Chemical | Dissolved oxygen, pH, nitrate, phosphate, silicate |
| Biological/productivity | Chlorophyll, primary productivity, related indicators |

OBIStherm is a possible supporting source only if it improves the primary task. It is not part of the core OBIS/Bio-ORACLE architecture. No source coverage count, species suitability, or layer compatibility has been verified in this repository.

### Storage convention

Preserve each acquired source in its publisher-delivered format. Use GeoParquet for compatible derived spatial tables and Parquet for compatible non-spatial modelling tables; retain complete environmental arrays in their source format and extract only the selected location-level covariates into modelling tables. Record actual formats and versions in manifests. Under [D-038](../records/2026-10-08-decision-phase-specific-derived-data-paths.md), timestamps may identify raw snapshots; the OBIS raw-to-interim handoff accepts a selected source path, then each interim phase uses a stable source-specific folder and fixed path. Bio-ORACLE's folder pattern is documented only; no Bio-ORACLE code is included in this branch. See [data storage and provenance](../data/data-storage-and-provenance.md) for details. COG and ONNX are optional, unfinalised future BLUEVERSE integration suggestions only; they are not OCEAVERA requirements or selected formats.

The proposal's intended output is estimated species occurrence probability, potentially represented as habitat suitability. The working research question uses relative-suitability language until target and observation-process evidence supports a stronger interpretation; this qualification preserves the proposed task while making its limits explicit.

## 6. Interpretation and technical constraints

1. An unrecorded occurrence is not automatically a confirmed absence. Background or pseudo-absence design is a central modelling decision.
2. Under a presence/background design, scores depend on the comparison-sample design and observation process. Use relative-suitability language unless the design supports occurrence probabilities. Calibration against background labels alone does not establish true occurrence probability.
3. Spatial dependence, repeated locations, observation bias, and leakage can make evaluation optimistic. The validation strategy must reflect the final sampling and geographic design.
4. Biological and environmental records need compatible spatial, temporal, and depth contexts. Record the assumptions and exclusions used to match them.
5. Predictive associations do not establish ecological causation. Report domain limits and uncertainty with the results.

## 7. Project-level completion criteria

The completed assignment should provide:

- A defined stakeholder context, decision need, study region, species, row meaning, target, and intended output.
- Traceable data acquisition, a data dictionary, documented quality decisions, and reproducible preparation.
- A justified baseline and at least three alternative methods, compared with suitable metrics.
- A leakage-aware evaluation plan, with spatial validation considered and probability calibration assessed when relevant.
- An evidence-based recommendation, practical value, limitations, and responsible interpretation.
- Reproducible code/notebook outputs and the logs and AI-use declaration required by the descriptor.

These are completion criteria, not claims about work already performed.

## 8. Open framing questions

- What stakeholder and decision make this Industry Explorer problem practically useful?
- What evidence confirms approval of the selected track and scope?
- Which species and marine boundary are feasible given occurrence coverage and record quality?
- Which environmental layers can be matched to the biological records in space, time, and depth?
- Which background design and spatial validation strategy are defensible for the final target?
- Which ML framework and scientific packages can run reproducibly on the accepted Python 3.14 baseline?

## 9. Shared participation and accountability

The proposal expects all four members to contribute to practical ML work and understand the full pipeline. No member is intended to hold only administrative, documentation, or presentation duties. Species selection, study boundary, features, target sampling, validation, comparison, and interpretation are shared technical decisions.

At the user's explicit request, the [responsibility overview and linked detailed files](member-responsibilities.md) preserve every proposed member activity, shared responsibility and pipeline role from Sections 6.1–6.7 of the initial submission. Sanuda leads biological data/targets/baseline; Ushan environmental data/integration/features; Adithya EDA/preprocessing/intermediate models; Wanshaja training/validation/evaluation/interpretation. Feature engineering is jointly primary for Ushan and Adithya; candidate training for Adithya and Wanshaja. The proposal-based allocation is now the finalised working contribution plan; responsibility changes require recorded evidence and authorisation. The [contributor mapping](ai-team-members.md) identifies the four members; [activity logs](../README.md#contribution-records) record actual work separately from planned ownership. The proposal declares ChatGPT and DeepSeek assistance during preparation; that declaration does not establish verification of later repository changes. Use the [AI-use record](ai-usage-log-template.md) to document actual assistance and review.

## 10. Document basis and maintenance

This overview preserves the shared direction of the initial project proposal and the obligations captured in the [assessment map](../../PROJECT_REQUIREMENTS.md). It records a planning baseline, not verified approval, data feasibility, or completed results. Material changes belong in the [decision register](decision-register.md); current readiness belongs in the [status review](repository-readiness-and-alignment.md).

# ML workflow and evidence gates

This is a shared analytical workflow, with primary ownership and shared participation defined by the [member responsibility plan](../project/member-responsibilities.md). It is not a fixed modelling recipe. The current phase is recorded in the [status review](../project/repository-readiness-and-alignment.md). The authorized OBIS cleaning and Bio-ORACLE structural/numerical scan are recorded; subsequent analytical stages remain pending until requested.

## Workflow

```mermaid
flowchart TD
    A[Frame decision context, lenses, task and scope] --> B[Record track approval status and required evidence]
    B --> C[Identify candidate resources and acquire a bounded feasibility sample]
    C --> D{Coverage and quality support a manageable task?}
    D -- No --> A
    D -- Yes --> E[Select focal species, marine boundary and compatible layers]
    E --> F[Acquire final inputs and record provenance]
    F --> G[Validate the selected OBIS raw CSV and clean to one current interim dataset]
    G --> H[Check quality and align space, time and depth]
    H --> I[Define row meaning, target and background sampling]
    I --> J[Define validation partitions and metric rationale]
    J --> K[Explore training data and document insights]
    K --> L[Fit preprocessing and feature steps within training partitions]
    L --> M[Fit baseline and at least three justified alternatives]
    M --> N[Compare validation results and select approach]
    N --> O[Evaluate held-out performance and interpretation limits]
    O --> P[Prepare supported suitability outputs and uncertainty]
    P --> Q[Make recommendation and assemble reproducible evidence]
    K -. Quality evidence may change data choices .-> E
    N -. Documented design revision .-> I
```

The interim retention policy is [D-049](../records/2026-10-11-decision-interim-one-current-dataset.md);
D-038 remains the historical source-intake path decision. Each data family
has only one current stage directory. OBIS currently uses
`data/interim/obis/cleaning/` for the source-validation manifest, cleaned CSV
and JSON reports; validation does not create a sibling folder. Bio-ORACLE now
uses `data/interim/bio_oracle/cleaning/`, with a manifest and structural/
numerical summary that reference unchanged raw NetCDF products. The prior
source-validation bundle was rechecked in full before cleaning replaced it;
that state can be regenerated from the raw run and staging script. Other
dataset states can be regenerated from preserved raw sources and scripts.
The Bio-ORACLE source-validation state is one logical bundle of NetCDF layers
and receipts, replaced as a whole after successful validation. Under
[D-047](../records/2026-10-09-decision-bio-oracle-catalog-intake.md)
and [D-048](../records/2026-10-09-decision-bio-oracle-sri-lanka-bbox.md),
the Bio-ORACLE collector inventories all regional v3 grids and supports
all-variable NetCDF retrieval over explicit bounds and the requested 2000–2100
window. The current ERDDAP axes expose baseline coordinates at 2000/2010 and
SSP coordinates at 2020–2090, with no separate 2100 coordinate in these layers.
Bio-ORACLE documents decadal, not annual, data: the 2090 SSP label reaches the
end of the final decade at 2100. Its catalogue-level baseline includes a
2010–2020 decade, but exact coverage through 2020 for each downloaded baseline
layer remains unresolved because titles vary and the time-axis metadata only
labels 2000/2010. D-048's named preset selects the rectangle made from the Marine Regions
EEZ polygon's coordinate extrema; it does not apply the EEZ polygon or a marine
mask. Catalogue and payload retrieval outcomes are recorded in the dated
intake record. The current cleaning record documents 356 readable products
and 2,392 variable instances, with one product flagged for a single missing
value. It reports a candidate spatial domain without assigning land/water
meaning to undocumented `landmass` values. It does not create corrected
rasters, integrate sources or make the data modelling-ready.
The earlier D-046 test payload
was deleted at the user's request.
See [data storage and provenance](../data/data-storage-and-provenance.md)
for the current and planned path patterns.

Limited feasibility investigation may inform framing and the approval request. It does not establish approval or stakeholder engagement. Prior approval must be evidenced before claiming an approved Industry Explorer project.

Non-outcome quality checks can cover the acquired data. Exploratory work that influences feature choice or model design must respect validation boundaries. After a design revision, maintain a genuinely held-out evaluation; do not repeatedly inspect test results to tune the pipeline.

## Evidence gates

| Gate | Evidence needed | Record or form | Current state |
| --- | --- | --- | --- |
| Framing and track | Verifiable context/decision, lenses and rationale, scope, success criteria, approval evidence | [Framing](../templates/problem-framing-canvas.md); [decisions](../project/decision-register.md) | Shared proposal direction present; decision context and approval pending |
| Data feasibility and path handoff | Exact resources, permissions/terms, counts/coverage, candidate species/area, spatial-temporal-depth compatibility, reproducible source paths | [Manifest](../templates/data-source-record.md); [dictionary](../templates/data-dictionary.md); [D-049 interim retention policy](../records/2026-10-11-decision-interim-one-current-dataset.md); [current OBIS cleaning record](../records/2026-10-11-obis-area-230-cleaning.md); [historical column-screen record](../records/2026-10-10-obis-area-230-column-screening.md); [OBIS EDA record](../records/2026-10-10-obis-area-230-eda.md); [D-047 catalogue-intake decision](../records/2026-10-09-decision-bio-oracle-catalog-intake.md); [D-048 collection rectangle](../records/2026-10-09-decision-bio-oracle-sri-lanka-bbox.md); [Bio-ORACLE cleaning record](../records/2026-10-11-bio-oracle-cleaning.md); [historical source record](../records/2026-10-09-source-bio-oracle-oceantemperature.md) | OBIS acquisition, manifest-based raw-source validation, column cleaning and conservative row cleaning are implemented. The one current OBIS interim CSV has 23,371 rows and 112 columns after field-specific sentinel handling; the 10% completeness rule protects essential fields, and row exclusions and retained status flags are recorded. The 90% screen and earlier row-filter output are historical. Focal species, final domain, contributing terms and environmental integration remain under review. Bio-ORACLE acquisition and structural/numerical cleaning are implemented for 356 products and 2,392 variable instances; 355 products are validated/reused and one needs review for one fill value. Focal species, final domain, layer suitability and environmental integration remain open. |
| Target and validation | Row meaning, positive/background definitions, sampling/bias rationale, splits, leakage controls, metrics | [Evaluation design](../templates/validation-and-evaluation-plan.md); [decisions](../project/decision-register.md) | Pending |
| Preparation and methods | Observed EDA, justified feature steps, baseline plus at least three alternatives, consistent comparison protocol | [EDA](../templates/eda-insight-log.md); [features](../templates/preprocessing-and-feature-decisions.md); [comparison](../templates/model-comparison.md) | Pending |
| Recommendation and handover | Evidence-linked value, uncertainty/domain limits, reproducible code/notebook, consistent report outputs and deliverables | [Recommendation](../templates/recommendations-and-limitations.md); [assessment checklist](../../PROJECT_REQUIREMENTS.md) | Pending |

Use evidence to revisit a gate when appropriate. Gate completion is a documented judgement, not a box inferred from a directory or blank form.

## Data and model artefact formats

Retain raw inputs as supplied. Use GeoParquet for compatible derived spatial records and Parquet for compatible non-spatial ML tables; keep environmental grid responses in NetCDF and place extracted location-level predictors in the integrated table. Record actual source and derived formats, specification versions, and any justified departures in the source records and dataset manifest. Under D-049, keep one current dataset per family. Where stage directories are used, retain exactly one active stage directory directly beneath the family path and replace it only after the full new result passes validation; a single-table family may use its fixed destination. OBIS currently has only `data/interim/obis/cleaning/`; Bio-ORACLE has only `data/interim/bio_oracle/cleaning/`, whose manifest maps 356 byte-verified interim NetCDF products to their raw sources and whose summary records the full scan. The integrated table has a fixed planned destination and does not yet exist. Earlier states remain reproducible from raw inputs and scripts. The first OBIS handoff accepts a selected raw CSV path and writes `source_validation_manifest.json` inside the `cleaning/` directory. The D-047 Bio-ORACLE collector inventories regional v3 products and requests all data variables with per-layer query manifests; D-048 sets the collection rectangle from the Marine Regions EEZ extent. The current catalogue selected 356 grids and 2,392 variables; actual time coverage and acquisition status are recorded in the [dated intake record](../records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md). The Bio-ORACLE handoff, [`stage_bio_oracle_layers.py`](../../src/data_preparation/stage_bio_oracle_layers.py), accepts a selected complete run manifest and copies its NetCDF payloads and receipts unchanged after structural and integrity checks; it can regenerate the earlier source-validation stage by replacing the current stage. Its `--dry-run` option checks run and receipt metadata, file sizes and available space without writing files; if a prior interim stage exists, it also verifies that stage payload hashes before replacement. The [cleaning script](../../src/data_preparation/clean_bio_oracle_layers.py) fully scans NetCDF structure and arrays, and publishes byte-for-byte NetCDF copies in the interim stage; it modifies no values unless a verified correction is justified. One marine-domain fill value remains under review. The rectangle does not apply a polygon mask. Environmental integration remains pending. The workflow does not select a modelling library or fix model serialization; record the chosen format and environment for each actual model artefact. COG and ONNX are optional, unfinalised future BLUEVERSE integration suggestions only.

## Ownership and handovers

| Stage | Working primary ownership | Required collaboration |
| --- | --- | --- |
| Framing, feasibility selection and final technical choices | All four shared | Species, domain, features, target, methods, validation and final selection remain group decisions |
| Biological data, occurrence quality and target/background inputs | Sanuda | Ushan/Adithya support; Wanshaja review |
| Environmental preparation and spatial integration | Ushan | Sanuda/Adithya support; Wanshaja review |
| Integrated quality, EDA and preprocessing | Adithya | All four participate; source-specific cleaning stays with Sanuda/Ushan |
| Feature engineering | Ushan and Adithya | Sanuda/Wanshaja participate |
| Baseline | Sanuda primary/shared | All four participate under the agreed protocol |
| Candidate training | Adithya and Wanshaja | Sanuda/Ushan participate; record particular candidate implementation ownership when methods are agreed |
| Validation and evaluation | Wanshaja | All four participate; agree partitions before design-informing EDA and learned transformations |
| Interpretation and habitat-suitability output | Wanshaja primary/shared | All four review final selection, output meaning and limitations |
| Final evidence, report, demo and reproducible handover | All four shared | Each supplies their actual technical evidence; each prepares their own individual learning report |

Follow the [handover duties](../project/member-contributions/shared-responsibilities-and-evidence.md#handover-and-final-submission-duties). Source data and integration must retain identifiers/versions for target, partition and feature lineage. Propagate a data/preprocessing change to the baseline and every comparison run. Review each gate using evidence rather than assuming a primary member's planned task is finished.

## Execution planning

Python 3.14 is the project baseline under [D-039](../records/2026-10-08-decision-python-3-14-baseline.md), and the `OCEAVERA` Conda setup is documented in the [root README](../../README.md#create-the-conda-environment). This repository does not store a Python environment. Jupyter Notebook and `ipykernel` are pinned in the root [`requirements.txt`](../../requirements.txt) for opening and running Python notebooks; they do not select the ML framework or scientific package stack. Those scientific dependencies and experiment configuration remain undecided; confirm selected libraries support the baseline before implementation. When a package is added or changed, update the manifest with its selected exact version and revise the setup instructions in the same change. An agent must obtain explicit prior user authorisation before creating, modifying or removing an environment or installing, upgrading or removing packages; documenting setup commands or updating the manifest is not permission to perform those operations.

The [complete responsibility matrix](../project/member-responsibilities.md#complete-pipeline-responsibility-matrix) establishes the finalised working member roles, subject to recorded changes. No calendar deadline is established here. Agree milestones against confirmed course dates and the approved scope; the Industry Explorer bonus requires manageable scope within seven weeks.

## Later BLUEVERSE handover

If the evaluated output is suitable for later integration, document its schema, geographic/environmental domain, target meaning, uncertainty, data-use conditions, and generation method. A reviewed analytical artefact is the proposed handover; operational deployment remains outside the current assignment scope.

The integration discussion proposes PostgreSQL/PostGIS for operational spatial records and JSON/GeoJSON at API boundaries, with large analytical assets stored separately and referenced from the application database. Confirm the receiving BLUEVERSE interface and approvals before implementation. COG and ONNX remain optional, unfinalised future BLUEVERSE integration suggestions; they are not required OCEAVERA outputs.

Complete [model metadata](../templates/model-metadata.json) only for an actual trained artefact. Tie any acceptance claim to the dataset, reproducible environment, comparison protocol, evaluation evidence and limitations. A notebook or anonymous model file alone does not establish an accepted integration output.

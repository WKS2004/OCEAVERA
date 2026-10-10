# OCEAVERA

![OCEAVERA — Marine Habitat Intelligence](assets/oceavera-brand-banner.png)

IT3091 Machine Learning · Group 2026-AI-45

OCEAVERA is the proposed marine intelligence component of BLUEVERSE. The project will investigate species distribution and habitat suitability by combining marine occurrence observations with environmental data. Marine Resilience is the primary decision lens; Coastal Tourism is the supporting application context.

## Project question

Given the marine environmental conditions at a location, can historical observations support an estimate of that location's relative suitability for a selected marine species?

The proposed biological source is OBIS, complemented by Bio-ORACLE environmental layers. The focal species, exact study boundary and compatible source resources will be selected from feasibility evidence. An unrecorded occurrence is not confirmed absence; presence/background model scores require a justified interpretation.

## Current stage

The [readiness review](docs/project/repository-readiness-and-alignment.md) records current evidence and unresolved choices; the [decision register](docs/project/decision-register.md) preserves planning positions and accepted conventions.

**In place**

- The shared repository foundation and member responsibility plan.
- The unrestricted Area 230 JSON/CSV acquisition method and its recorded validation evidence under D-036.
- An OBIS-only raw-to-interim handoff that accepts a selected CSV and stages a byte-preserving copy in a stable source-phase folder.
- The first catalog-wide Bio-ORACLE v3 intake and a later partial manual snapshot were deleted at the user's request. The final Python collector run under D-047/D-048 completed all 356 regional grids and 2,392 variables (4,017,532,960 payload bytes); every payload passed byte-count, SHA-256 and NetCDF-signature checks, with zero failed or pending layers. The [regional source record](docs/records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md) preserves all run histories and the audit. The retrieved source axes exposed baseline coordinates at 2000/2010 and SSP coordinates at 2020–2090; there is no separate 2100 snapshot.
- Bio-ORACLE provides decade summaries, not annual values. Its publisher-level present-day product spans 2000–2020, split into 2000–2010 and 2010–2020 decades; whether every baseline layer includes the full period through 2020 is unresolved because layer titles end in 2018, 2019 or 2020 while retrieved time metadata labels only 2000/2010. SSP labels run from 2020 through 2090, with the final decade reaching the 2100 horizon but no separate 2100 timestamp. See the [source record](docs/records/2026-10-09-source-bio-oracle-sri-lanka-catalog.md).
- The [branch work notebook](notebooks/branch_work/pipeline_biological_data_collection.ipynb), which documents the branch and runs its offline CSV demonstration in memory.

**Pending**

Scientific cleaning, environmental compatibility review and integration, analytical notebooks, model implementation and model results.

**Open choices and evidence**

The focal species, modelling boundary, compatible environmental resources, ML framework and experiment environment remain unresolved. Industry Explorer is the proposed track; approval and the stakeholder decision context are not evidenced. Python 3.14 is the project baseline.

## Data and model artefacts

The working convention preserves raw source responses, uses timestamps for raw acquisition snapshots, and places each interim transformation in a stable phase subfolder under its source. The OBIS handoff accepts a selected run-specific CSV path; the Bio-ORACLE collector inventories the catalogue, requests all variables within explicit bounds and records its query beside each raw NetCDF response. The earlier complete and partial Bio-ORACLE snapshots were deleted at the user's request; the latest local snapshot contains all 356 planned layers and passed transfer-integrity checks. Source compatibility, spatial/temporal alignment and final predictor selection remain subject to review. GeoParquet is used for compatible derived spatial tables and Parquet for compatible non-spatial ML tables. Actual resource formats, model serialization and experiment environment remain to be verified or selected during authorised work. The [data storage and provenance guide](docs/data/data-storage-and-provenance.md) defines the full conventions. COG and ONNX remain optional, unfinalised suggestions for a future BLUEVERSE integration; neither is an OCEAVERA requirement.

## Start here

| Document | Purpose |
| --- | --- |
| [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) | Project obligations, evidence requirements, rubric and submission checklist |
| [`.python-version`](.python-version) | Shared Python 3.14 baseline used by Conda setup and repository CI |
| [requirements.txt](requirements.txt) | Shared, exactly pinned third-party packages for project code, notebooks and required tooling; includes Jupyter Notebook and its Python kernel |
| [Project overview and scope](docs/project/project-overview-and-scope.md) | Research context, boundaries and interpretation limits |
| [Member responsibilities](docs/project/member-responsibilities.md) | General division and pipeline matrix, with links to four detailed member files and shared duties |
| [ML workflow and evidence gates](docs/ml/ml-workflow-and-evidence-gates.md) | Planned analytical sequence and progression conditions |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Change workflow, scientific records, contribution logging and review |
| [AGENTS.md](AGENTS.md) | Instructions and guidance routing for repository agents |
| [Documentation index](docs/README.md) | Maintained knowledge, contribution records and evidence locations |
| [LICENSE.md](LICENSE.md) | All-rights-reserved policy and third-party material boundaries |

## Member responsibilities

The [responsibility overview](docs/project/member-responsibilities.md) summarises the initial proposal's division and links each member's detailed duties. The contribution plan is finalised for the current scope, with shared participation and recorded change control.

| Member | Primary technical area |
| --- | --- |
| [Sanuda Abeysinghe](docs/project/member-contributions/sanuda-abeysinghe.md) | Biological data, target construction and baseline modelling |
| [Ushan Srinuka](docs/project/member-contributions/ushan-srinuka.md) | Environmental data, spatial integration and feature engineering |
| [Adithya Gunawardana](docs/project/member-contributions/adithya-gunawardana.md) | EDA, preprocessing and intermediate model development |
| [Wanshaja Sooriyabandara](docs/project/member-contributions/wanshaja-sooriyabandara.md) | Candidate training, validation, evaluation and interpretation |

Feature engineering is jointly led by Ushan and Adithya; candidate training by Adithya and Wanshaja. All four participate technically across the pipeline and share final decisions. The allocation records expected work, not completed contributions or permission to begin implementation.

## Repository structure

| Path | Contents and navigation |
| --- | --- |
| `assets/` | Visual assets used by the project README and documentation |
| [`.agents/`](.agents/README.md) | Agent rules, skills, routing and structural validation |
| [`.github/workflows/`](docs/project/github-workflows.md) | Repository CI and maintenance automation |
| [`data/`](data/README.md) | Raw, interim and processed data; payloads are excluded from Git by default |
| [`docs/`](docs/README.md) | Canonical project knowledge, templates, dated records and contributor logs |
| [`notebooks/`](notebooks/README.md) | Branch work notebooks and future reproducible analysis |
| [`src/data_collection/`](src/README.md) | OBIS Area 230 retrieval, JSON-to-CSV conversion and catalog-wide Bio-ORACLE regional intake |
| [`src/data_preparation/`](src/README.md) | OBIS raw-CSV validation and interim staging |
| [`outputs/`](outputs/README.md) | Future reviewed figures, maps and evaluation artefacts |
| [`reports/`](reports/README.md) | Future group report and submission material |

Scientific records belong in `docs/records/`; factual contributor activity belongs in `docs/ai-contribution/`. Their conventions are maintained in [contributor guidance](CONTRIBUTING.md#project-evidence-records) and the [AI-usage template](docs/project/ai-usage-log-template.md). Exact contributor identities are maintained in the [team mapping](docs/project/ai-team-members.md).

## Repository checks

[Repository checks](.github/workflows/ci.yml) runs the structural helper and syntax-compiles the OBIS and Bio-ORACLE intake plus OBIS handoff scripts on pull requests, pushes to every branch and manual dispatch. It does not run the scripts or download dataset records. See [GitHub workflows](docs/project/github-workflows.md) for operation, failure handling and prerequisites for later scientific checks. The hosted maintenance interpreter does not select the ML runtime; passing these checks does not establish scientific or submission readiness.

For documentation and agent-resource changes, run the structural helper from the repository root with Python 3.10 or later:

```text
python .agents/scripts/validate_agent_resources.py
git diff --check
```

The helper uses the standard library and checks maintained resource formats, local files and section links, text conventions and contribution-record structure. It does not evaluate models or execute behavioural agent evaluations. See the [agent guide](.agents/README.md) for registry maintenance.

## Python dependencies

Python 3.14 is the project baseline, recorded in [`.python-version`](.python-version).
The current OBIS and Bio-ORACLE intake scripts use the standard library and
remain compatible with Python 3.10 or later. Jupyter Notebook and `ipykernel`
are pinned in the root [`requirements.txt`](requirements.txt) as notebook
tooling, not as the ML or scientific stack. No Python environment is stored in
this repository. The following commands document user-led setup; agents need
explicit authorisation in the current task before environment or package
operations:

```text
python -m pip install -r requirements.txt
```

### Create the Conda environment

From the repository root, create and activate the `OCEAVERA` environment with
the baseline interpreter, then install the shared requirements:

These are user-led setup instructions. Before an agent creates or changes an
environment, or installs, upgrades or removes packages, it must first receive
your explicit authorisation in the current task. Editing this manifest or
documenting setup commands does not provide that authorisation.

```text
conda create --name OCEAVERA python=3.14 pip
conda activate OCEAVERA
python --version
python -m pip install -r requirements.txt
```

The version check should report Python 3.14.x. Installing the requirements adds
the pinned Jupyter Notebook interface and Python kernel; the OBIS intake scripts
still use only the standard library. To open the branch notebook from the
repository root, run:

```text
jupyter notebook notebooks/branch_work/pipeline_biological_data_collection.ipynb
```

The branch notebook uses native Markdown cells for its title, contributor table, scope and data context, followed by concise executable Python Code cells. Run the Code cells in order. The default mode does not access the network, and notebook data work remains in memory rather than writing dataset files.
The future ML framework and scientific dependency stack remain open. Conda
must be installed and initialised for the shell before running these commands.

Whenever project code, notebooks or required tooling add, remove or change a
third-party Python package, update `requirements.txt` with the selected exact
version pin and update the relevant setup instructions in the same change.
Do not add standard-library modules or speculative future ML packages. The
[contributor dependency policy](CONTRIBUTING.md#python-dependencies) is
authoritative.

ML setup and execution instructions will accompany the agreed implementation environment when that stage is authorised.

## Licence

**All rights reserved; no public reuse grant.** Original project material belongs to the contributing members of group 2026-AI-45. Academic affiliation does not grant institutional ownership. See [LICENSE.md](LICENSE.md). Third-party datasets, dependencies and other materials retain their own terms and attribution requirements.

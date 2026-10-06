# OCEAVERA

**Marine Habitat Intelligence**

IT3091 Machine Learning · Group 2026-AI-45

OCEAVERA is the proposed marine intelligence component of BLUEVERSE. The project will investigate species distribution and habitat suitability by combining marine occurrence observations with environmental data. Marine Resilience is the primary decision lens; Coastal Tourism is the supporting application context.

## Project question

Given the marine environmental conditions at a location, can historical observations support an estimate of that location's relative suitability for a selected marine species?

The proposed biological source is OBIS, complemented by Bio-ORACLE environmental layers. The focal species, exact study boundary and compatible source resources will be selected from feasibility evidence. An unrecorded occurrence is not confirmed absence; presence/background model scores require a justified interpretation.

## Current stage

**Finalised shared foundation.** Project context, requirements, evidence conventions, agent guidance and the finalised member responsibility plan are established for the next authorised stage. Data acquisition, analysis notebooks, ML implementation and model results are pending. The runtime has not been selected. Industry Explorer is the proposed track; approval and the stakeholder decision context remain unevidenced.

The [readiness review](docs/project/repository-readiness-and-alignment.md) records current evidence and unresolved choices. The [decision register](docs/project/decision-register.md) preserves planning positions and accepted conventions.

## Start here

| Document | Purpose |
| --- | --- |
| [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) | Project obligations, evidence requirements, rubric and submission checklist |
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

## Working areas

| Location | Purpose |
| --- | --- |
| [docs/](docs/README.md) | Canonical project knowledge, blank forms and dated records |
| [data/](data/README.md) | Raw, intermediate and processed data; payloads excluded from Git by default |
| [notebooks/](notebooks/README.md) | Future reproducible exploration and analysis |
| [src/](src/README.md) | Future reusable implementation |
| [outputs/](outputs/README.md) | Future generated figures, maps and evaluation artefacts |
| [reports/](reports/README.md) | Future report and submission material |
| [.agents/](.agents/README.md) | Focused rules, skills, task routing and structural validation |
| [GitHub CI](.github/workflows/ci.yml) | Automated checks of documentation, agent resources and contribution-record structure |

Scientific records belong in `docs/records/`; factual contributor activity belongs in `docs/ai-contribution/`. Their conventions are maintained in [contributor guidance](CONTRIBUTING.md#project-evidence-records) and the [AI-usage template](docs/project/ai-usage-log-template.md). Exact contributor identities are maintained in the [team mapping](docs/project/ai-team-members.md).

## Repository checks

[Repository checks](.github/workflows/ci.yml) runs the structural helper on pull requests, pushes to `main` and manual dispatch. See [GitHub workflows](docs/project/github-workflows.md) for operation, failure handling and prerequisites for later scientific checks. The hosted maintenance interpreter does not select the ML runtime; a passing structural check does not establish scientific or submission readiness.

For documentation and agent-resource changes, run the structural helper from the repository root with Python 3.10 or later:

```text
python .agents/scripts/validate_agent_resources.py
git diff --check
```

The helper uses the standard library and checks maintained resource formats, local files and section links, text conventions and contribution-record structure. It does not evaluate models or execute behavioural agent evaluations. See the [agent guide](.agents/README.md) for registry maintenance.

ML setup and execution instructions will accompany the agreed implementation environment when that stage is authorised.

## Licence

**All rights reserved; no public reuse grant.** Original project material belongs to the contributing members of group 2026-AI-45. Academic affiliation does not grant institutional ownership. See [LICENSE.md](LICENSE.md). Third-party datasets, dependencies and other materials retain their own terms and attribution requirements.

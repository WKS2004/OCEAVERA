# GitHub workflows

## Current automation

[Repository checks](../../.github/workflows/ci.yml) runs the existing [structural helper](../../.agents/scripts/validate_agent_resources.py) on pull requests, pushes to `main` and manual dispatch. It checks the complete maintained text inventory on each run. It has no path filters or optional jobs that silently pass when required files are missing.

| Setting | Current choice |
| --- | --- |
| Workflow name | Repository checks |
| Job name | Repository structure and records |
| Runner | GitHub-hosted Ubuntu 24.04 |
| Maintenance interpreter | Python 3.12; standard library only |
| Time limit | Five minutes |
| Repository token | Read access to repository contents; checkout credentials are not persisted |
| Dependencies | Official checkout and Python setup actions pinned to full commit SHAs, with release comments |
| Concurrent runs | New runs cancel older runs for the same pull request; event types and branch refs have separate groups |

Python here supports repository maintenance. The scientific runtime, ML dependencies and reproducible experiment environment remain undecided.

## What the check establishes

The helper fails on inconsistent skill/rule inventory, stale generated routing, invalid maintained skill metadata, unresolved local file or Markdown section links, malformed JSON, text-format violations and invalid contributor-record structure. It checks exact account/name mapping, required entry fields, dates and timezone notation. CI runs in check mode and does not regenerate routing or edit records.

These are structural checks. They do not authenticate a contributor, prove an activity, scan every possible personal-data format, validate general YAML syntax, check external URLs, execute skill evaluations, assess scientific correctness or establish human acceptance. Member privacy still requires the review in [CONTRIBUTING.md](../../CONTRIBUTING.md#member-privacy).

## Local use and failure handling

From the repository root, use Python 3.10 or later:

```text
python -B .agents/scripts/validate_agent_resources.py
git diff --check
```

Read the failed step's diagnostic, correct the referenced file and rerun the helper before submitting a change. If the skill registry was intentionally changed, follow the [routing regeneration procedure](../../.agents/README.md#validate-and-maintain), review the generated diff and commit the intended routing update with that change. CI should continue to check the committed view.

Workflow edits also require a YAML/Actions syntax review because the structural helper is not a general workflow parser. An available `actionlint` installation can check the workflow locally:

```text
actionlint .github/workflows/ci.yml
```

After the workflow is committed and pushed to GitHub, inspect its first hosted run. Manual dispatch requires the workflow on the default branch and Actions enabled. A file in the worktree is not evidence of a passing hosted run. The stable job name above can support a later required-check policy; no branch protection or repository settings are configured by these files.

## Scope selected from the workflow analysis

The supplied workflow analysis was reviewed against actual repository contents. The current implementation has one useful CI workflow: the maintained structural helper already has a defined command and failure conditions. The remaining proposed checks depend on executable work and contracts that do not yet exist.

| Automation area | Prerequisites for introduction |
| --- | --- |
| Source quality and unit checks | Agreed scientific environment, executable modules and relevant checks authorised with their implementation |
| Notebook execution | Actual notebooks, a reproducible environment, bounded execution and a shareable small input; execute a copy and review output privacy before publishing artefacts |
| Data validation | Actual dataset/manifest contracts, source fingerprints and recorded taxonomic, spatial, temporal, target and leakage policies; blank templates are not dataset evidence |
| Pipeline smoke checks | Implemented preprocessing, training and evaluation entry points plus a small deterministic fixture; assess expected behaviour without downloading full source datasets on each pull request |
| Experiment reproduction | A recorded experiment, pinned environment and retrievable, permitted data snapshot; use explicit manual or narrowly scoped triggers for expensive execution |
| Model packaging | An accepted model with preprocessing, feature schema, metadata, checksum, limitations and evaluation evidence; establish versioning and distribution rights first |
| BLUEVERSE integration checks | An authorised integration surface and actual inference contract, with agreed analytical handover and scope |

Introduce these checks as their prerequisites are met. Full training, scheduled acquisition/retraining, deployment and automatic model publication require separate scope and evidence decisions. Preserve the [ML evidence gates](../ml/ml-workflow-and-evidence-gates.md); a green structural check does not advance them.

## Maintenance and official references

Review upstream release notes before changing an action pin. Update the full SHA and matching release comment together, confirm the commit belongs to the official action repository, review supported runner requirements and inspect the next hosted run. No Actions update bot has been configured.

- [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) defines event, permission and concurrency behaviour.
- [GitHub secure use guidance](https://docs.github.com/en/actions/reference/security/secure-use) supports minimal permissions, reviewed action pins and ordinary pull-request execution without privileged triggers.
- [Checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) and [Python setup v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0) identify the pinned action releases.
- [actionlint](https://github.com/rhysd/actionlint) documents the optional local Actions syntax checker.

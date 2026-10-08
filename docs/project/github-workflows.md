# GitHub workflows

## Current automation

[Repository checks](../../.github/workflows/ci.yml) runs the existing [structural helper](../../.agents/scripts/validate_agent_resources.py) on pull requests, pushes to `main` and manual dispatch. It checks the complete maintained text inventory on each run. It has no path filters or optional jobs that silently pass when required files are missing.

[Development backup maintenance](../../.github/workflows/dev-backup.yml) keeps `dev-backup` at the exact commit on `dev` after pushes to either branch. If the backup branch contains commits absent from `dev`, it first preserves that history on a timestamped rescue branch. The source `dev` branch is not present in the current OCEAVERA checkout; the workflow will not run until a push to `dev` or `dev-backup` occurs.

[Lowercase branch policy](../../.github/workflows/branch-policy.yml) runs when GitHub reports a newly created reference. It ignores tag creations. For a branch, the only rule is that its name must already be lowercase; a name containing uppercase letters is deleted through the GitHub API. Lowercase names are accepted without a list of permitted names or branch patterns. This allows the timestamped rescue branches created by development backup maintenance. Existing branches are not checked retroactively.

| Setting | Current choice |
| --- | --- |
| Workflow name | Repository checks |
| Job name | Repository structure and records |
| Runner | GitHub-hosted Ubuntu 24.04 |
| Maintenance interpreter | Python 3.14 from the root `.python-version` file; standard library only |
| Time limit | Five minutes |
| Repository token | Read access to repository contents; checkout credentials are not persisted |
| Dependencies | Official checkout and Python setup actions pinned to full commit SHAs, with release comments |
| Concurrent runs | New runs cancel older runs for the same pull request; event types and branch refs have separate groups |

The CI job reads the project interpreter from `.python-version` using the
official setup-python action's `python-version-file` input. Update the shared
version file when changing the baseline so local Conda setup and CI stay aligned.

| Backup setting | Current choice |
| --- | --- |
| Workflow name | Maintain development backup |
| Trigger | Push to `dev` or `dev-backup` |
| Source and mirror | `dev` → `dev-backup` |
| Runner and time limit | GitHub-hosted Ubuntu 24.04; ten minutes |
| Permissions | `contents: write` so the workflow can create rescue branches and update the mirror |
| History handling | Fetch full history; timestamped `dev-backup-mistaken-commits/<actor>/<time>` rescue branch before reset |
| Synchronisation | `--force-with-lease` against the previously read backup commit; concurrent runs are serialised and not cancelled |
| Checkout action | Official checkout release pinned to a full commit SHA; credentials persist for the required pushes |

| Branch policy setting | Current choice |
| --- | --- |
| Workflow name | Lowercase branch policy |
| Trigger | GitHub `create` event; only branch creations are evaluated |
| Rule | `branch === branch.toLowerCase()`; no name list, prefixes or branch-pattern rules |
| Action | Delete an uppercase branch reference, then fail the workflow run |
| Permissions | `contents: write` for the GitHub reference deletion API |
| Action pin | Official GitHub Script v9.0.0 release pinned to its full commit SHA |

Commit this workflow to the default branch before relying on it for new branch creations. GitHub repository permissions and branch rules must permit the Actions token to delete the created branch. GitHub rejects attempts to delete the default branch, so keep the configured default branch lowercase. Uppercase branches already present when the workflow is enabled are not deleted by its creation-only trigger.

The development backup workflow needs GitHub Actions to have repository content write permission. Any repository branch/rule controls must also allow that token to create the rescue branch and update `dev-backup`, including the force update. The workflow reports a failed push and stops before resetting the backup when these operations are rejected. This checkout contains no `dev` or `dev-backup` branch, so the workflow file alone does not establish that backup protection is active.

For each push to either branch, the workflow reads the current `dev` and `dev-backup` commits. It creates a missing backup directly from `dev`, or exits when both commits already match. If `dev-backup` contains commits that are absent from `dev`, it first creates `dev-backup-mistaken-commits/<actor>/<Asia-Colombo timestamp>` from `dev`, merges in the backup history while preferring backup content for conflicts, and pushes that rescue branch. If the merge cannot complete, it records both histories in an explicit merge commit. Only after that preservation step succeeds does it update `dev-backup` to the exact `dev` commit using the previously observed backup SHA as a force-with-lease guard. A backup that is merely behind `dev` is synchronised without creating a rescue branch.

Python 3.14 is the project baseline and the interpreter used by repository maintenance CI. The current scripts and helper remain compatible with Python 3.10 or later. ML frameworks, scientific dependencies and reproducible experiment configuration remain undecided.

## What the check establishes

The helper fails on inconsistent skill/rule inventory, stale generated routing, invalid maintained skill metadata, unresolved local file or Markdown section links, malformed JSON, text-format violations and invalid contributor-record structure. It skips byte-preserved `data/raw/` payloads while checking tracked records and code. It checks exact account/name mapping, required entry fields, dates and timezone notation. CI runs in check mode and does not regenerate routing or edit records.

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

The supplied workflow analysis was reviewed against actual repository contents. Repository checks run the maintained structural helper, development backup maintenance follows the established project backup policy, and the branch policy enforces lowercase only. The remaining proposed scientific checks depend on executable work and contracts that do not yet exist.

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
- [Branch creation events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#create) and [deleting a Git reference](https://docs.github.com/en/rest/git/refs#delete-a-reference) describe the branch trigger and API operation.
- [GitHub Script v9.0.0](https://github.com/actions/github-script/releases/tag/v9.0.0) identifies the pinned official script action release.
- [actionlint](https://github.com/rhysd/actionlint) documents the optional local Actions syntax checker.

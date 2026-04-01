# GitHub Actions Workflows

Monorepo CI/CD for busylight-core and busylight-cli (busylight-for-humans).

## Architecture

```
PR / push to main
  └─ ci.yml
       ├─ detect-changes (path filters)
       ├─ test-core (if core changed)
       ├─ test-cli  (if cli or core changed)
       └─ lint      (if anything changed)

Tag: busylight-core/vX.Y.Z
  └─ release-core.yaml
       ├─ test (core matrix)
       ├─ build
       ├─ publish (PyPI) ──────┐
       ├─ github-release ──────┼─ deploy-docs
       └─ check-cli-compat    │  (repository_dispatch)

Tag: busylight-cli/vX.Y.Z
  └─ release-cli.yaml
       ├─ test (cli matrix)
       ├─ build
       ├─ publish (PyPI) ──┐
       └─ github-release ──┴─ deploy-docs
```

## Workflows

### ci.yml

Runs on every PR and push to main. Uses path filters to detect which
packages changed and only runs the relevant test matrices. CLI tests
also run when core changes (since CLI depends on core).

Jobs: detect-changes, get-python-versions, test-core, test-cli, lint.

### release-core.yaml

Triggered by tags matching `busylight-core/v*`. Full test matrix,
build, publish to PyPI, GitHub release with per-package changelog,
docs deployment, and CLI compatibility check.

The compatibility check runs CLI tests against the newly published
core version and warns if they fail.

### release-cli.yaml

Triggered by tags matching `busylight-cli/v*`. Same structure as
core release but for the CLI package.

### docs.yml

Deploys documentation to GitHub Pages. Triggered by repository
dispatch from release workflows or manual workflow dispatch.

### auto-merge.yml

Squash-merges PRs when JnyJny comments "LGTM".

## Tag Convention

- Core releases: `busylight-core/vX.Y.Z`
- CLI releases: `busylight-cli/vX.Y.Z`

Tags are created by `poe publish_patch|publish_minor|publish_major`
in the respective package directory.

## Release Flow

1. `cd packages/busylight-core` (or `packages/busylight`)
2. `poe publish_patch` (or `publish_minor` / `publish_major`)
   - Preflight: verifies main branch + clean tree
   - Bumps version in pyproject.toml
   - Commits, tags with package prefix, pushes
3. GitHub Actions picks up the tag and runs the release workflow
4. Package is tested, built, published to PyPI
5. GitHub release created with changelog
6. Docs deployed

## Python Version Configuration

Test matrix versions are configured in busylight-core's pyproject.toml:

```toml
[tool.busylight_core.ci]
test-python-versions = ["3.11", "3.12", "3.13"]
```

Both packages share this configuration. Fallback: `["3.11", "3.12", "3.13"]`.

## Requirements

- PyPI trusted publisher configured for each package
- Environments: `pypi-core` and `pypi-cli` matching trusted publisher setup
- `GH_PAT` secret for changelog commits and auto-merge
- GitHub Pages enabled (auto-enabled by docs workflow)

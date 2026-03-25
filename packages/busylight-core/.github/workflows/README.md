# GitHub Actions Workflows

This directory contains optimized CI/CD workflows for testing, building,
publishing, and documentation deployment.

## Workflow Architecture

The release workflow follows an efficient pipeline structure:

```
test (matrix) → build → [publish, github-release] (parallel) → docs
                ↓              ↓           ↓                     ↑
          [artifacts]    (cached artifacts) (cached artifacts)  └─(both complete)
```

## Workflows

### ci.yml
Continuous integration for every push to main and every PR targeting main.

**Jobs:**
1. **test** - Matrix testing (Ubuntu, macOS, Windows x Python versions):
   - Unit tests: `pytest tests/`
   - Doc tests: `pytest --markdown-docs docs/` (validates all Python code blocks in documentation against the real API using mock USB hardware from `docs/conftest.py`)
2. **lint** - Ruff check and format verification

**CI coverage by scenario:**

| Scenario | Workflow | Unit Tests | Doc Tests | Timing |
|----------|----------|-----------|-----------|--------|
| Push to main | ci.yml | Yes | Yes | Post-hoc |
| PR to main | ci.yml | Yes | Yes | Pre-merge (gate with branch protection) |
| Tag push (release) | release.yaml | Yes | Yes | Pre-publish |
| Push to testing | release.yaml | Yes | Yes | Post-hoc |

**Note:** For PRs, CI results are advisory unless branch protection is enabled on main with required status checks. With branch protection, failing doc tests block the merge.

### release.yaml
Main CI/CD pipeline triggered on version tags (e.g., `v1.2.3`).

**Stages:**
1. **get-python-versions** - Extracts Python test versions from pyproject.toml
2. **test** - Matrix testing across OS/Python versions (Ubuntu, macOS, Windows × extracted versions)
3. **build** - Single package build, uploads artifacts for reuse
4. **publish** - Publishes to PyPI using cached artifacts (parallel with github-release)
5. **github-release** - Creates GitHub release with changelog (parallel with publish)
6. **deploy-docs** - Triggers documentation deployment after successful release

**Key optimizations:**
- Package built once and reused via artifact caching
- Parallel execution of publish and release jobs
- Consolidated changelog generation
- Dynamic Python version matrix from pyproject.toml
- ~3x faster than sequential builds

### docs.yml
Documentation deployment workflow.

**Triggers:**
- Repository dispatch after successful releases
- Manual workflow dispatch for ad-hoc builds

**Process:**
- Builds MkDocs documentation
- Deploys to GitHub Pages only after successful PyPI publish and GitHub release

## Workflow Communication

The two workflows communicate via GitHub's repository dispatch mechanism:

1. **release.yaml** → **docs.yml**: After successful publish and GitHub release, the `deploy-docs` job sends a `repository_dispatch` event with type `release-complete`
2. **docs.yml** listens for this event and automatically builds/deploys documentation
3. This ensures documentation is only rebuilt for actual releases, not every code change

**Manual Override**: The docs workflow can also be triggered manually via `workflow_dispatch` for ad-hoc documentation updates without doing a release.

## Python Version Configuration

The test matrix Python versions are configured in `pyproject.toml`:

```toml
[tool.busylight_core.ci]
test-python-versions = ["3.11", "3.12", "3.13"]
```

**Benefits:**
- Single source of truth for Python test versions
- Automatic CI updates when versions change
- Graceful fallback to default versions if config missing

**Fallback:** If the configuration section is missing, the workflow defaults to `["3.11", "3.12", "3.13"]`.

## Requirements

The workflows require:
- PyPI project with [trusted publisher][trusted-publisher] configured
- Environment named "pypi" matching PyPI trusted publisher setup
- GitHub Pages for documentation deployment (automatically enabled by docs workflow)

<!-- End Links -->
[pypi]: https://pypi.org
[trusted-publisher]: https://docs.pypi.org/trusted-publishers/

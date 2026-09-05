## [busylight-cli/v1.0.2] - 2026-09-05

### 🐛 Bug Fixes

- Correct uv.lock path in _add task for monorepo layout
- Resolve busylight lint backlog, two real bugs, dead code removal (#810)

### 💼 Other

- *(deps)* Bump fastapi from 0.138.1 to 0.138.2
- *(deps)* Bump fastapi from 0.138.2 to 0.139.0
- *(deps-dev)* Bump coverage from 7.14.3 to 7.15.0
- *(deps)* Bump uvicorn from 0.49.0 to 0.50.2
- *(deps)* Bump uvicorn from 0.50.2 to 0.51.0
- *(deps-dev)* Bump anyio from 4.14.1 to 4.14.2
- *(deps-dev)* Bump coverage from 7.15.0 to 7.15.1
- *(deps-dev)* Bump coverage from 7.15.1 to 7.15.2
- *(deps)* Bump fastapi from 0.139.0 to 0.139.1
- *(deps)* Bump typer from 0.26.8 to 0.27.0
- *(deps)* Bump fastapi from 0.139.1 to 0.139.2
- *(deps-dev)* Bump mkdocs-material from 9.7.6 to 9.7.7
- *(deps)* Bump fastapi from 0.139.2 to 0.140.1
- *(deps)* Bump fastapi from 0.140.1 to 0.140.9
- *(deps)* Bump uvicorn from 0.51.0 to 0.52.0
- *(deps)* Bump fastapi from 0.140.9 to 0.140.13
- *(deps)* Bump fastapi from 0.140.13 to 0.141.1
- *(deps)* Bump uvicorn from 0.52.0 to 0.52.1
- Harmonize ruff config between packages, track lint backlog (#809)
- *(deps-dev)* Bump coverage from 7.15.2 to 7.15.3 (#806)
- *(deps)* Bump typer from 0.27.0 to 0.27.1 (#808)
- *(deps-dev)* Bump coverage from 7.15.3 to 7.15.4 (#813)
- *(deps)* Bump uvicorn from 0.52.1 to 0.52.3 (#816)
- *(deps)* Bump mkdocs-git-revision-date-localized-plugin (#817)
- *(deps)* Bump uvicorn from 0.52.3 to 0.52.4 (#818)
- *(deps)* Bump typer from 0.27.1 to 0.27.2 (#820)
- *(deps-dev)* Bump coverage from 7.15.4 to 7.16.0 (#822)

### 📚 Documentation

- *(cli)* Update CHANGELOG
## [busylight-cli/v1.0.1] - 2026-06-20

### 📚 Documentation

- *(cli)* Update CHANGELOG
## [busylight-cli/v1.0.0] - 2026-04-03

### 🚀 Features

- Add per-package deptry dependency verification to CI (#706)
- CI fail-fast gating and post-test light teardown (#709)

### 🐛 Bug Fixes

- *(ci)* Suppress pre-existing lint issues, add INP001 to test ignores
- Remove unused imports in CLI package (F401)
- Add CLI ruff config, fix formatting, clean unused imports
- Update image and link paths for monorepo structure
- *(docs)* Use img tag for hero image to fix GitHub rendering
- Remove dead importlib_metadata fallback (#707)

### 📚 Documentation

- *(cli)* Add device caption under hero image
- Harmonize READMEs across root, core, and CLI
## [busylight-core/v2.2.0] - 2026-04-01

### 🐛 Bug Fixes

- Updated and unified contribution and agent docs
- Update copyright to 2022-2026, symlink package LICENSE files
- Enable pytest from workspace root

### 💼 Other

- Consolidate .github, deps, and remove scaffolding

### ⚙️ Miscellaneous Tasks

- Monorepo CI/CD workflows with per-package releases
- Update git-cliff tag patterns for monorepo convention

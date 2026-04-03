## [busylight-core/v2.3.0] - 2026-04-03

### 🚀 Features

- Add per-package deptry dependency verification to CI (#706)
- CI fail-fast gating and post-test light teardown (#709)

### 🐛 Bug Fixes

- *(ci)* Suppress pre-existing lint issues, add INP001 to test ignores
- Update image and link paths for monorepo structure
- Light.vendor() IndexError on classes outside vendor hierarchy (#690)
- Correct Blynclight BitField offsets and move state policy to _on (#708)

### 📚 Documentation

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

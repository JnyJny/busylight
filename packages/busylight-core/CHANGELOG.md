## [busylight-core/v2.5.0] - 2026-10-13

### 🚀 Features

- Add support for VT DND devices (#831)

### 🐛 Bug Fixes

- Restore initial value in Word.clear() (#834)
- Use inspect.iscoroutinefunction instead of deprecated asyncio alias (#836)
- Break VT DND write_strategy reference cycle (#848)

### 🚜 Refactor

- Restructure VT DND support to match vendor patterns (#835)
- VT DND flash modes, reset state, and command interval (#849)
## [busylight-core/v2.4.1] - 2026-09-05

### 🐛 Bug Fixes

- Correct uv.lock path in _add task for monorepo layout
- Resolve busylight lint backlog, two real bugs, dead code removal (#810)

### 📚 Documentation

- *(core)* Update CHANGELOG
- Trim derivable/duplicated content from root CLAUDE.md (#807)

### 💼 Other

- Harmonize ruff config between packages, track lint backlog (#809)
## [busylight-core/v2.4.0] - 2026-04-03

### 📚 Documentation

- *(core)* Update CHANGELOG

### 🚜 Refactor

- Extract BlynclightProtocol mixins for cross-vendor protocol sharing (#711)
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

### ⚙️ Miscellaneous Tasks

- Monorepo CI/CD workflows with per-package releases
- Update git-cliff tag patterns for monorepo convention

### 💼 Other

- Consolidate .github, deps, and remove scaffolding

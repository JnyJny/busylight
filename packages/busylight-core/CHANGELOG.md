# CHANGELOG

All notable changes to this project will be documented in this file.

## [2.2.0](https://github.com/JnyJny/busylight-core/releases/tag/v2.2.0) - 2026-03-25

### Bug Fixes

- Dropped base python version from 3.12 to 3.11 ([29ccd98](https://github.com/JnyJny/busylight-core/commit/29ccd9851fcac91bca116d0d9e59c08341c1c66c))
## [2.1.1](https://github.com/JnyJny/busylight-core/releases/tag/v2.1.1) - 2026-03-25

### Bug Fixes

- Add interrupt parameter to light on method ([92a985d](https://github.com/JnyJny/busylight-core/commit/92a985dd1d478ec0840b385639e7d565bc0d6e07))

### Documentation

- fix dangling cross-reference in contributing.md ([87bac4a](https://github.com/JnyJny/busylight-core/commit/87bac4a9530b2b554652f1794dbe90713c7e0032))

### Other

- Updated uv.lock with latest dependencies. ([d75a029](https://github.com/JnyJny/busylight-core/commit/d75a029fa33d30712e74f8ed42c3dcf1590e6f70))
## [2.1.0](https://github.com/JnyJny/busylight-core/releases/tag/v2.1.0) - 2026-03-24

### Bug Fixes

- cancel pre-existing tasks in Light.on() via Template Method (#59) ([06d7cd2](https://github.com/JnyJny/busylight-core/commit/06d7cd205b8a1c9a1ed0cbfd9c648d710a51424d))
- use uv sync for git-cliff in release workflow ([7350ca0](https://github.com/JnyJny/busylight-core/commit/7350ca0d7c13e36bd1aa82a7c052960e42815179))
- use GH_PAT for release changelog push ([af63027](https://github.com/JnyJny/busylight-core/commit/af63027b4f4ebb49e35d90ce509997e10ffde158))
## [2.0.1](https://github.com/JnyJny/busylight-core/releases/tag/v2.0.1) - 2026-03-15

### Bug Fixes

- use GH_PAT for auto-merge workflow permissions ([3099e9d](https://github.com/JnyJny/busylight-core/commit/3099e9dc355902ee7b65aaa30aff534b2a6eb93d))
- add preflight checks to publish tasks ([2c039b5](https://github.com/JnyJny/busylight-core/commit/2c039b52bb47ef06f862391174d5e0a0e7fb4209))

### Other

- add scratch file names to .gitignore ([ff0b596](https://github.com/JnyJny/busylight-core/commit/ff0b596f847f86e869bda19cc7a5f06724c423b6))

### Refactor

- modernize type annotations with Self and Callable (#57) ([2df1ff6](https://github.com/JnyJny/busylight-core/commit/2df1ff67277ffdbd45b9b490ad39298f4c01fd90))
## [1.0.1](https://github.com/JnyJny/busylight-core/releases/tag/v1.0.1) - 2026-03-15

### Features

- replace changelog generation with git-cliff (#55) ([8c7635c](https://github.com/JnyJny/busylight-core/commit/8c7635c7c9af40c88fc5a93e27f56c67e2953f0d))
## [0.15.4](https://github.com/JnyJny/busylight-core/releases/tag/v0.15.4) - 2026-03-14

### Bug Fixes

- mark blyncusb doc code block as notest ([8a118d7](https://github.com/JnyJny/busylight-core/commit/8a118d79ac39c1fe31941ba59e6711825d410f84))
- set testpaths so bare pytest runs unit tests only ([07d71fa](https://github.com/JnyJny/busylight-core/commit/07d71fad226e98e183b989fcdd568b7cf357c57d))
- IndexError in button_on method addressed. ([32319a6](https://github.com/JnyJny/busylight-core/commit/32319a6e534dd257d6f5dd8f71c4934cee840943))
- Luxafor Flag on method could barf on incorrect led specification. ([98802bc](https://github.com/JnyJny/busylight-core/commit/98802bc2f3b37a14c585f820c27d169d60b81aac))
- resolve CI failures - lint rules, libusb dependency, format ([2c6c8bb](https://github.com/JnyJny/busylight-core/commit/2c6c8bb09873c5b700c74029857936578988c625))
- Changed path encoding order in Light.at_path ([19b5637](https://github.com/JnyJny/busylight-core/commit/19b5637364a4847f3aad83f59d67a9070df83e59))

### Documentation

- sync doc test guidance across CLAUDE.md, CONTRIBUTING.md, docs/, and release workflow (#44) ([03f5fd7](https://github.com/JnyJny/busylight-core/commit/03f5fd78ecce70c2b6367300575ff2a5639a5384))
- rewrite documentation to match actual API (fixes #43) ([27a8e16](https://github.com/JnyJny/busylight-core/commit/27a8e16ff4f1b0d0013bc59c9a880ddec67091ee))

### Features

- add support for early Blynclight models (VID 0x1130) (#52) ([498a80b](https://github.com/JnyJny/busylight-core/commit/498a80b48d0ee67af4b3deaa421557d511f29c4a))
- add poe doc-test task, update all references ([4f74ff3](https://github.com/JnyJny/busylight-core/commit/4f74ff30483a85c204d7ea8f4a1cce3ca603dab5))
- add executable doc tests with pytest-markdown-docs (#44) ([f0d553e](https://github.com/JnyJny/busylight-core/commit/f0d553ecee2baf6a58afcf6a34995c507f930c17))

### Other

- Luxafor Mute is_button method does not work. ([8d47268](https://github.com/JnyJny/busylight-core/commit/8d47268dfda947b9bfe532a66ad8976782b67716))
- nope, needed libusb too. Added back into test workflows. ([be4d483](https://github.com/JnyJny/busylight-core/commit/be4d483bdf60e1bb90aadd6488e105bb314812f9))
- libudev.h supplied by libudev-dev and not libusb. ([bfc77c6](https://github.com/JnyJny/busylight-core/commit/bfc77c6e9d5a019b88f2f5dc47edd34789f87191))
- Remove hallucinated section from README ([9d5ba2c](https://github.com/JnyJny/busylight-core/commit/9d5ba2ce588be8239e7e02dbc2c688d3a645bf1d))
- Updated tests ([bd35a7c](https://github.com/JnyJny/busylight-core/commit/bd35a7c6a6805690a0b35b5fecb283557b810b82))
- Updated pyproject.toml ([9c42260](https://github.com/JnyJny/busylight-core/commit/9c4226078d749deaf96791262a7010d7a63be5e9))

### Styling

- remove underscore prefixes from docs/conftest.py ([42c7d70](https://github.com/JnyJny/busylight-core/commit/42c7d7006753f661fb2815d8d2188262cc4bacce))
## [0.15.3](https://github.com/JnyJny/busylight-core/releases/tag/v0.15.3) - 2025-11-22

### Bug Fixes

- busylight_core.hardware.Hardware ([ab3b0d9](https://github.com/JnyJny/busylight-core/commit/ab3b0d99ed462fb772142d4c89add74ee76a64d9))

### Features

- Acquire Light instances using path specifier. ([6551ae3](https://github.com/JnyJny/busylight-core/commit/6551ae3561aad0e8ce706bad8f11cbc6f4bfccc3))
- busylight_core.light.Light.nleds property ([e2cf8c8](https://github.com/JnyJny/busylight-core/commit/e2cf8c8ee90037b6c2c766fde97bc33793a9ebf1))

### Refactor

- Cleanup: ([162d83c](https://github.com/JnyJny/busylight-core/commit/162d83c613d3931f9655a35271d516e60237a13c))
## [0.15.2](https://github.com/JnyJny/busylight-core/releases/tag/v0.15.2) - 2025-09-21

### Bug Fixes

- refactor Kuando keepalive to instance method and update tests ([6704451](https://github.com/JnyJny/busylight-core/commit/6704451abbc83c4b81eb25e1a88e6de90b0836af))
- TaskableMixin mock detection and vendor test ([c7386bf](https://github.com/JnyJny/busylight-core/commit/c7386bffe60fcb935b39d15d2065cf0843b0999d))
## [0.15.1](https://github.com/JnyJny/busylight-core/releases/tag/v0.15.1) - 2025-08-12

### Documentation

- Updated README.md examples. ([c0d7633](https://github.com/JnyJny/busylight-core/commit/c0d7633ca1249f9eca1f881fdc00cc4795e13b0d))

### Features

- added as_dict method to Harwdare ([d430726](https://github.com/JnyJny/busylight-core/commit/d430726708ed76f3093de6e47cfae6766d6c39b0))
- Added __str__ to Light ([b9c973a](https://github.com/JnyJny/busylight-core/commit/b9c973a5334c565371cbdac17e49a1d0a6cbeae1))
## [0.15.0](https://github.com/JnyJny/busylight-core/releases/tag/v0.15.0) - 2025-07-31

### Bug Fixes

- add missing interval parameter for periodic keepalive ([4aa03f0](https://github.com/JnyJny/busylight-core/commit/4aa03f005173ba76d9b65860a5602a2db0c7faa0))
- Some serial devices have None for vendor or product IDs ([665cb26](https://github.com/JnyJny/busylight-core/commit/665cb266c1b9968199c13a13d253054dfe763c68))
- accidently commited working file ([a9a089d](https://github.com/JnyJny/busylight-core/commit/a9a089d45060fe2b3df342c71fd6d259b0ce0e84))

### Documentation

- remove unnecessary Kuando-specific section from CLAUDE.md ([b6c590f](https://github.com/JnyJny/busylight-core/commit/b6c590fa299ee41915412d0bf4bdfc9d2136a332))
- remove keepalive mentions from user documentation ([1fcfd94](https://github.com/JnyJny/busylight-core/commit/1fcfd9408d7ceb3a514830e7a11e1837392a9a53))
- update documentation for TaskableMixin and Kuando keepalive ([d552aac](https://github.com/JnyJny/busylight-core/commit/d552aacecdb41c1ecdbe4c763edc383fb868342d))
- update issue templates with correct version commands ([7bfeca3](https://github.com/JnyJny/busylight-core/commit/7bfeca37bf71b9265eb87b886eee80cf91774d22))
- add Implementation links to vendor API reference navigation ([d6c77a9](https://github.com/JnyJny/busylight-core/commit/d6c77a92374d39c1bab8731339eb8377739e668d))
- restructure API reference documentation ([603e01a](https://github.com/JnyJny/busylight-core/commit/603e01a606b1d37f55fc3a4b2e0a00da661cff40))

### Features

- add threading fallback for TaskableMixin ([663ba9a](https://github.com/JnyJny/busylight-core/commit/663ba9ad1d38a97a9e840cf883e6130fa7bd248d))
- add new device support request issue template ([7778b86](https://github.com/JnyJny/busylight-core/commit/7778b86dd6af4fb20fbf4a82e5b5d57adc4a9957))

### Other

- add version attribute validation tests ([86c6ac1](https://github.com/JnyJny/busylight-core/commit/86c6ac1b211721532098d0de1d0fb8f761887a5d))

### Refactor

- simplify Kuando keepalive implementation ([f5695ed](https://github.com/JnyJny/busylight-core/commit/f5695ede2669fef298d4d28776f9f39e7c4dcdff))
- restructure vendor implementations into logical modules ([25b16d7](https://github.com/JnyJny/busylight-core/commit/25b16d7ee5a565146f9921f678f505dd5ef8886e))

### Styling

- ruff formatting cleanup ([662176c](https://github.com/JnyJny/busylight-core/commit/662176c27863dd97456f419f3645d52b85ad36a5))
## [0.14.1](https://github.com/JnyJny/busylight-core/releases/tag/v0.14.1) - 2025-07-25

### Bug Fixes

- Use consistent busylight_core naming in tool section ([83b21b2](https://github.com/JnyJny/busylight-core/commit/83b21b295bb0f511780043013bb5dc5ec01d863c))

### Documentation

- update all documentation for vendor Lights classes ([b676a52](https://github.com/JnyJny/busylight-core/commit/b676a52e13d399e3f42eab25fb8b7fcf53a915b1))
- Broken link in README.md ([c693c38](https://github.com/JnyJny/busylight-core/commit/c693c38a2b9981df399a725f11af15cdad487952))
- Consolidated development info in CONTRIBUTING.md ([3054ab3](https://github.com/JnyJny/busylight-core/commit/3054ab34d50b53ffbf2efb1d0eaae99fe02c0129))
- Removed mute from Kuando in vendor/device table. ([86ea9e0](https://github.com/JnyJny/busylight-core/commit/86ea9e0c0246823c30f1655d145231b9dae93d12))
- Wordsmithing the README ([b6ae056](https://github.com/JnyJny/busylight-core/commit/b6ae0563174fd41dc30b2cc02040f774eef0a049))
- Fixed doc URLs in README. s/advanced-features/features/ ([c5fa708](https://github.com/JnyJny/busylight-core/commit/c5fa708fb596990620503a008f5af78b9c5ae8ff))
- fix documentation links in README ([41703a6](https://github.com/JnyJny/busylight-core/commit/41703a65ac75a85f79b61845c4ec52b1974eb8da))
- comprehensive documentation improvements and API reference enhancement ([652ce8a](https://github.com/JnyJny/busylight-core/commit/652ce8a522e0b29ce4e687a1de26a3c5991d7d84))
- removed nonfunctional fix for footnote rendering. ([444f36c](https://github.com/JnyJny/busylight-core/commit/444f36c5e662666148bcb18a1a57ddafb3cbfcc0))
- Update CONTRIBUTING.md for optimized release workflow ([b0bcf28](https://github.com/JnyJny/busylight-core/commit/b0bcf28b96ce93673dc6aafd33cbdd503ef85b36))
- Document optimized release workflow in CLAUDE.md ([0ad1067](https://github.com/JnyJny/busylight-core/commit/0ad1067b01204e66f69c357f6eb3861f0a45730a))
- Document Python version configuration in workflows README ([21b5aeb](https://github.com/JnyJny/busylight-core/commit/21b5aeb24402e6dacdfb472463cf3523a7ef9231))
- Document workflow communication mechanism in README ([fa02ff6](https://github.com/JnyJny/busylight-core/commit/fa02ff63d33133a9d7a8ed4f12b393c54f524b83))
- Add GitHub Pages setup link to workflows README ([e3ae0d4](https://github.com/JnyJny/busylight-core/commit/e3ae0d468f64342b9ad70d565d9e1d05f5973127))
- Remove irrelevant Jinja formatting section from workflows README ([840d11b](https://github.com/JnyJny/busylight-core/commit/840d11b929cef7996dcee53d4b33f69f7ebbdd15))
- Update workflows README to reflect optimized architecture ([ca8c844](https://github.com/JnyJny/busylight-core/commit/ca8c84485d3cc1742e496a436dbb1b9089d6165d))
- Optimize CLAUDE.md for token efficiency and objectivity ([98f0627](https://github.com/JnyJny/busylight-core/commit/98f06275c5a954b088e3765a917c140a0b08cfca))
- Standardize exception variable names from 'e' to 'error' ([5d6ff49](https://github.com/JnyJny/busylight-core/commit/5d6ff49f3c3263d10bd32e49f61e625152c06ff3))

### Features

- add vendor-specific Lights classes for direct access ([90177e7](https://github.com/JnyJny/busylight-core/commit/90177e7065df833d231e07e506331885632ef968))
- Updated busylight_core package with version information string. ([9fdfde3](https://github.com/JnyJny/busylight-core/commit/9fdfde3706bc3ab53d90fca9eebfed99e72e8190))
- added release method to busylight_core.light.Light ([6bce0de](https://github.com/JnyJny/busylight-core/commit/6bce0de67a0ad5a63e510bf02494f2a95a97ebd2))
- Add error handling for missing Python version config ([aebb765](https://github.com/JnyJny/busylight-core/commit/aebb765ad6a660f6ea8fa90dd3eba9a333318208))

### Other

- add comprehensive tests for vendor Lights classes ([ee27c3c](https://github.com/JnyJny/busylight-core/commit/ee27c3c44e7174750a005dfd69d41891d5e5ce0c))
- Remove unnecessary JSON conversion for Python versions ([6866a0f](https://github.com/JnyJny/busylight-core/commit/6866a0f6d14d9dfd03bda7797da49ebb929f6e53))

### Refactor

- Standardize Light class caching to @cache decorator ([e7fe6e3](https://github.com/JnyJny/busylight-core/commit/e7fe6e33a6641649d16a0d2bb663733e103f3b01))
## [0.11.0](https://github.com/JnyJny/busylight-core/releases/tag/v0.11.0) - 2025-07-22

### Other

- Update tests to match corrected device capabilities ([303e0f5](https://github.com/JnyJny/busylight-core/commit/303e0f58cd0b93217eb6983fc897fae59594d8df))
## [0.10.0](https://github.com/JnyJny/busylight-core/releases/tag/v0.10.0) - 2025-07-22

### Bug Fixes

- Correct audio capabilities across Embrava Blynclight variants ([d88e806](https://github.com/JnyJny/busylight-core/commit/d88e8068077a6b9a8f827a96e055e671140884af))

### Documentation

- Updated light and init docstrings ([645e592](https://github.com/JnyJny/busylight-core/commit/645e592f02dec10d188602b27e860187c740b970))
- Updated README examples. ([f083f06](https://github.com/JnyJny/busylight-core/commit/f083f063dbef420d0fcb0f26bcaecb80eb695c4f))
- Update project documentation with docstring format guidance ([84e8cce](https://github.com/JnyJny/busylight-core/commit/84e8cce1a1e64c45694b014373fc8bd56af81ff1))
- Update project documentation with docstring format guidance ([ccabfc8](https://github.com/JnyJny/busylight-core/commit/ccabfc899a4778a1cb5d4e46d09e561d54acde8f))

### Other

- ignore scripts directory that CLAUDE creates for one-off tools. ([afbd9dd](https://github.com/JnyJny/busylight-core/commit/afbd9dd6fa247df7bab40457fb78789735fe89d0))

### Refactor

- Standardize docstrings to Sphinx reStructuredText format ([64f182f](https://github.com/JnyJny/busylight-core/commit/64f182f184f52329294ea14901a758348eab4b09))
- Standardize docstrings to Sphinx reStructuredText format ([c3b10a4](https://github.com/JnyJny/busylight-core/commit/c3b10a4364870c8bfd82f00e10d77f2310ece607))
## [0.9.2](https://github.com/JnyJny/busylight-core/releases/tag/v0.9.2) - 2025-07-22

### CI

- Updated release workflow to include automatic changelog updates. ([7fa49dc](https://github.com/JnyJny/busylight-core/commit/7fa49dcc0b4bd7cecc2834a773c43a16380caf0d))

### Other

- Updated CLAUDE.md ([73eceb6](https://github.com/JnyJny/busylight-core/commit/73eceb67e8a58aa17366be1d92543c7d7d437674))
## [0.9.1](https://github.com/JnyJny/busylight-core/releases/tag/v0.9.1) - 2025-07-22

### Other

- satisfying ruff check in src and tests ([4aca9d7](https://github.com/JnyJny/busylight-core/commit/4aca9d7ba1301f4d2d0d20e916bd431ad050102a))
- ruff check updates, refactor of the blinkstick claims methods. ([2d3f681](https://github.com/JnyJny/busylight-core/commit/2d3f68119f18478d3352376813ceac402a7f654e))
## [0.9.0](https://github.com/JnyJny/busylight-core/releases/tag/v0.9.0) - 2025-07-22

### Documentation

- Restore proper docstrings with Google/JavaDoc style formatting ([185e04a](https://github.com/JnyJny/busylight-core/commit/185e04a16a6fbb3959b265bace1db294c28cb62f))

### Features

- Enhanced async task management with prioritization and error handling ([a395382](https://github.com/JnyJny/busylight-core/commit/a3953820965d7051090c55ed1d8ab8542680ad2c))

### Other

- Add plan.md to .gitignore ([d114171](https://github.com/JnyJny/busylight-core/commit/d1141719372577077c472895f052a89dbd026261))
- Add comprehensive hierarchy tests for all vendor base classes ([345bae0](https://github.com/JnyJny/busylight-core/commit/345bae0b12254558ee4208279eab0df50278428a))

### Refactor

- Updated agile innovative blinkstick classes with a parameterized _claims classmethod ([267de41](https://github.com/JnyJny/busylight-core/commit/267de41de4d3fb5f5d04922ad83a78669bd33cf8))
- Replace try/except/pass with contextlib.suppress ([942c245](https://github.com/JnyJny/busylight-core/commit/942c2454bfb9a28a644227ce5713c8f1f3c9cd4d))
- Clean up async task management code ([ca28010](https://github.com/JnyJny/busylight-core/commit/ca280108a0dcd66e386a2c360328ac40f40f5ecb))
- Remove plan.md from repository ([eebd65a](https://github.com/JnyJny/busylight-core/commit/eebd65a7f5cba2113887c5d188704df45ccf98ca))
- complete vendor base class hierarchy standardization ([1f61902](https://github.com/JnyJny/busylight-core/commit/1f6190270737c5667d2a29235646900d66d881ff))
- implement Phase 1 foundation improvements ([de94f2f](https://github.com/JnyJny/busylight-core/commit/de94f2f4a19a01b943ec98382d69220d8826afe6))

### Styling

- Replace single-character exception variable with descriptive name ([01cd5d7](https://github.com/JnyJny/busylight-core/commit/01cd5d77822498c9e0c49b4489e24f5cff0acb13))
## [0.8.0](https://github.com/JnyJny/busylight-core/releases/tag/v0.8.0) - 2025-07-20

### Other

- Updated Kuando _busylight.ScaledColorField to work with 3.11 and 3.12 ([73778cc](https://github.com/JnyJny/busylight-core/commit/73778cc34b2da8fe61b379dd699c6f0d1bf5ab66))
## [0.7.0](https://github.com/JnyJny/busylight-core/releases/tag/v0.7.0) - 2025-07-20

### Bug Fixes

- Fixed a bug in the _muteme.OneBitField class's setter method. ([2a988b7](https://github.com/JnyJny/busylight-core/commit/2a988b76c5cac7ef7201974df1b797960031c28a))

### Other

- Updated Kunado _busylight ColorField set and get methods. ([a1c3044](https://github.com/JnyJny/busylight-core/commit/a1c30440ffa0e2f9e38ee84c22822ec180817a68))
- Ruff updates for test_vendor_plantronics_status_indicator ([8907412](https://github.com/JnyJny/busylight-core/commit/89074123dffcd29f349f01b07bbafb7f212efb0c))
- Add comprehensive tests for Plantronics Status Indicator device ([6abfdac](https://github.com/JnyJny/busylight-core/commit/6abfdac946aa2eafa94a3c7b3ec99f1ef90d8233))
## [0.6.0](https://github.com/JnyJny/busylight-core/releases/tag/v0.6.0) - 2025-07-20

### Other

- Cleaned up poe tasks in pyproject. ([073df3a](https://github.com/JnyJny/busylight-core/commit/073df3a233f3024633ad93fce0576e41163fc0ce))
- Ruff updates to tests. ([80e4975](https://github.com/JnyJny/busylight-core/commit/80e49756fc8a179aaeb387b9ad7a125b67d2b108))
- Add comprehensive tests for CompuLab fit-statUSB device ([22f835a](https://github.com/JnyJny/busylight-core/commit/22f835affe60bf76a2982198aa358534ed71f9a1))
- Add comprehensive tests for Light.udev_rules classmethod ([3aac874](https://github.com/JnyJny/busylight-core/commit/3aac874cfac0b35e4b099ede453175bb0c8b2267))
- Ruff check fixes. ([ccc92a9](https://github.com/JnyJny/busylight-core/commit/ccc92a94eb53a602026fb31b1243ab82a11c038f))
- Refactored Kuando Busylight tests. ([ec00ad7](https://github.com/JnyJny/busylight-core/commit/ec00ad7ff3baf2a7a20a768e8ab2eca740cf8539))
- Clean up docstrings and standardize color property documentation ([367874b](https://github.com/JnyJny/busylight-core/commit/367874bb5b65c13a459dfb27d18d69d30492920d))
- Renamed Kuando Busylight Alpha test suite. ([dab57e9](https://github.com/JnyJny/busylight-core/commit/dab57e9b3e46ec283dace28e141bd3f90e671a75))
- Refactored Kuando Busylight family and updated tests. ([eac743d](https://github.com/JnyJny/busylight-core/commit/eac743de85ddf49dc2b27177ea8cec43aab444cf))
- Refactor color handling architecture across all devices ([af4d85d](https://github.com/JnyJny/busylight-core/commit/af4d85db4f883dea9eb4def5647936b9e22af95c))
- Updated .gitignore ([2c26238](https://github.com/JnyJny/busylight-core/commit/2c262389804d9302e69124ebf4be01cccc4f5782))
- Bugfix for blinkstick_base.BlinkStickBase ([35df5b8](https://github.com/JnyJny/busylight-core/commit/35df5b814cbcef66d4aac7e41941fae654b7c47c))
- Updated busylight_core.light.Light ([42b8597](https://github.com/JnyJny/busylight-core/commit/42b859758ac3877df724a4b553ef3dd1ad5ec803))
- Updated Luxafor tests for proper Busy Tag vendor name. ([53a935e](https://github.com/JnyJny/busylight-core/commit/53a935e40b928a824782760e1bc03d5a2c2ffe44))
- Busy Tag device now in the Luxafor family of devices. ([ef2ef45](https://github.com/JnyJny/busylight-core/commit/ef2ef45b08dcfbf1791ef5ee39872acc0a6c6e52))
- Updated Agile Innovative BlinkStick family ([f8da555](https://github.com/JnyJny/busylight-core/commit/f8da555f5561166f89f03a3f48598dfed3904379))
- Updated Agile Innovative BlinkStick family of imports. ([95396da](https://github.com/JnyJny/busylight-core/commit/95396dac185245a13a40f6bebdec5c62f74470be))
## [0.5.0](https://github.com/JnyJny/busylight-core/releases/tag/v0.5.0) - 2025-07-19

### Bug Fixes

- Fix exception implementation and hardware handle property ([d9ab8b7](https://github.com/JnyJny/busylight-core/commit/d9ab8b7b7b30442e5bbf04a2eecbd70e9b436ae7))

### Other

- Updated Embrava blynclight test, removed check for deleted struct property. ([f640d11](https://github.com/JnyJny/busylight-core/commit/f640d110b59a60899eda9cc0e6421d47d72db85b))
- Add BlinkStickBase abstract base class for Agile Innovative devices ([889ba11](https://github.com/JnyJny/busylight-core/commit/889ba11c14384e351185275187b0e4b6809094a6))
- Simplify Embrava Blynclight implementation and improve documentation ([e617c68](https://github.com/JnyJny/busylight-core/commit/e617c68b91943bef2ceaa7a7aa0833833e1e6335))
- Enhance Embrava Blynclight implementation with color field support ([b5a1de4](https://github.com/JnyJny/busylight-core/commit/b5a1de4cfaa8b61b1768ba4f2c5152adba64302a))
- Enhance exception handling and improve hardware robustness ([801d92a](https://github.com/JnyJny/busylight-core/commit/801d92a16a26ce15cc02a8746bfb6f9bc7060882))
- Enhance Light class documentation and type safety ([68c8e91](https://github.com/JnyJny/busylight-core/commit/68c8e91d04ff5a611dffcbf1d13e051ad5263139))
- Updated test_light ([db665f1](https://github.com/JnyJny/busylight-core/commit/db665f1ce87c0095db2ee1a2256b3397193882ce))
- Updated Agile Innovative tests: ruff check ([d255617](https://github.com/JnyJny/busylight-core/commit/d2556170a7acbd2bc4140c9d22140e9e9f4224a5))
- Updated README with link to Busylight For Humans™ ([e650fc7](https://github.com/JnyJny/busylight-core/commit/e650fc7bb8c0a4317d49a13c218686a6bf27934f))
## [0.4.1](https://github.com/JnyJny/busylight-core/releases/tag/v0.4.1) - 2025-07-18

### Other

- Added check to subclasses method to exclude Light subclasses whose supported_device_ids dictionary is None ([1904d9e](https://github.com/JnyJny/busylight-core/commit/1904d9ebaa7da6fc7b6a14f940d10de5022e12a0))
- Updated README.md ([b11f457](https://github.com/JnyJny/busylight-core/commit/b11f4578eb59715576c8d795c8603fd2856457e5))
## [0.4.0](https://github.com/JnyJny/busylight-core/releases/tag/v0.4.0) - 2025-07-18

### Other

- Added support for remainder of the Agile Innovative BlinkStick family of devices: BlinkStick, BlickStick Pro, BlickStick Nano, BlickStick Flex, and BlickStick Strip ([3b3a4c9](https://github.com/JnyJny/busylight-core/commit/3b3a4c9e9a79a058fc04b11842656bc6e40b2241))
- Update BlinkStick tests for new State API ([c1b0ed5](https://github.com/JnyJny/busylight-core/commit/c1b0ed5da1d3c81be6ffc6a926caad125df7d7ed))
## [0.3.5](https://github.com/JnyJny/busylight-core/releases/tag/v0.3.5) - 2025-07-18

### Bug Fixes

- Fix descriptor protocol handling for Python 3.11 compatibility ([2f03dab](https://github.com/JnyJny/busylight-core/commit/2f03dabcb4c5da7e149c081e40395d5ef50cde56))
## [0.3.4](https://github.com/JnyJny/busylight-core/releases/tag/v0.3.4) - 2025-07-18

### Other

- Update BlinkStick tests for GRB color fix implementation ([51912d8](https://github.com/JnyJny/busylight-core/commit/51912d81db32f0098ac1ba87bc65db240efff9e6))
- Updates to Agile Innovative BlinkStick, bug in new code and testing. ([ea5c4e4](https://github.com/JnyJny/busylight-core/commit/ea5c4e4e2e39a4720fade1138f9147ad7136483a))
- Updated BlinkStick devices. ([07a363f](https://github.com/JnyJny/busylight-core/commit/07a363f724a5c0fc8beb54636c8888200736ede9))
- ruff check tests now runs clean ([f26943f](https://github.com/JnyJny/busylight-core/commit/f26943fa3db979a606a966cf4adeac9147315fce))
- ruff format tests ([9e14843](https://github.com/JnyJny/busylight-core/commit/9e148434eabb11c2bf129fd9179aa8d4407dfadc))
- Achieve 99% test coverage with comprehensive edge case testing ([fdfaad6](https://github.com/JnyJny/busylight-core/commit/fdfaad60de64b20289447bb4d343fe1da6fb021f))
- Rename all vendor-specific test files with test_vendor_ prefix ([9215065](https://github.com/JnyJny/busylight-core/commit/9215065fc652d10332c39002f743b23739f4d5e0))
- Complete comprehensive test coverage for all remaining vendor implementations ([4a90a9a](https://github.com/JnyJny/busylight-core/commit/4a90a9a4fed33f21ddda6799982443e2a01bbda5))
- Add comprehensive test coverage for EPOS and Kuando vendor implementations ([5e57d55](https://github.com/JnyJny/busylight-core/commit/5e57d55c97376a4fc62965d1135b62f5bb1ff35f))
## [0.3.3](https://github.com/JnyJny/busylight-core/releases/tag/v0.3.3) - 2025-07-17

### Other

- Renamed Light.reset property to Light.was_reset since it shadowed the reset method. Whoops. ([b29c7d7](https://github.com/JnyJny/busylight-core/commit/b29c7d717f8ed045ff81cb725b8db3477a67e9c0))
- ruff format tests updated unpacking. ([a10f704](https://github.com/JnyJny/busylight-core/commit/a10f704a48e9841d50d53fe573854e119ba516a1))
- Updated MuteSync ([5521c69](https://github.com/JnyJny/busylight-core/commit/5521c6921c1f7c6b4dd8b43aa311e443c995266f))
## [0.3.2](https://github.com/JnyJny/busylight-core/releases/tag/v0.3.2) - 2025-07-17

### Other

- Update mutesync claims method ([38d849b](https://github.com/JnyJny/busylight-core/commit/38d849bef2629a39b36507832bbb8ceb8bc2ffeb))
## [0.3.1](https://github.com/JnyJny/busylight-core/releases/tag/v0.3.1) - 2025-07-17

### Other

- Updated mutesync vendor to reflect new ownership by MuteMe ([30a6382](https://github.com/JnyJny/busylight-core/commit/30a6382f31ac491701345a0fc6e295f1ad76e646))
- Updated .envrc ([ddf3d0c](https://github.com/JnyJny/busylight-core/commit/ddf3d0cb912f40a2aa559fcf60d110e9f45457d4))
- Updated vendor and model information ([fcbf8e5](https://github.com/JnyJny/busylight-core/commit/fcbf8e5d6ab313f637b2ed092fb68ed22866e2c4))
## [0.3.0](https://github.com/JnyJny/busylight-core/releases/tag/v0.3.0) - 2025-07-16

### Bug Fixes

- Fixed typo in busylight_alpha ([6ab20ee](https://github.com/JnyJny/busylight-core/commit/6ab20eea31b9c5514bb2a083c6db1f1915fbf51d))
- Fix all ruff check issues in test suite and complete pytest compliance ([3d47216](https://github.com/JnyJny/busylight-core/commit/3d47216b7d25a39bf02a59b7f367669caf4c61f3))
- Fix all ruff check issues in src directory ([c6752f7](https://github.com/JnyJny/busylight-core/commit/c6752f7a2d1ddfc3ec694fb6df94e11218f4c9a8))
- Fixed light.Light.__hash__ ([070fcbb](https://github.com/JnyJny/busylight-core/commit/070fcbb0f5d8a57fedd46418bdbac37e99f9d526))
- Fix API Reference navigation to properly show Light class ([b3e6bda](https://github.com/JnyJny/busylight-core/commit/b3e6bdae3fd3f338c0c2e2ee7b3e742984d0a223))

### Other

- Updated project dependencies ([9939a28](https://github.com/JnyJny/busylight-core/commit/9939a28ecf77286d442e23d1b14e56d1079d1ff2))
- Improve API design and test coverage with property refactoring ([df3a436](https://github.com/JnyJny/busylight-core/commit/df3a436eea7d84ff6a1f5602cadb1ff83023e30e))
- Update old exception references to new exception names ([0f5d07d](https://github.com/JnyJny/busylight-core/commit/0f5d07d9933cf61e4d4b61f8f8818498416b5fbd))
- Updated base class implementations to satisfy ruff check ([24b03db](https://github.com/JnyJny/busylight-core/commit/24b03db12fba742c3d7dde45127acde6e4febb4c))
- Updated source with ruff format ([52f7102](https://github.com/JnyJny/busylight-core/commit/52f7102b35e5754965fdfbdad999389ba1095042))
- Updated pyproject.toml ruff check options ([4e577cb](https://github.com/JnyJny/busylight-core/commit/4e577cb8db6f6ea345b2e592ecd3c42464c83915))
- Updated busylight_core/light.py ([254ba9d](https://github.com/JnyJny/busylight-core/commit/254ba9d1174fcb00a41df9e41be708f3364a72ab))
- Updated Vendor Embrava __init__ ([8096084](https://github.com/JnyJny/busylight-core/commit/80960844067b2efcde7eb229bcf103ae7df31304))
- Updated EPOS Busylight ([ed88619](https://github.com/JnyJny/busylight-core/commit/ed8861900cf35a38340b05c4a02327801ca8e069))
- EPOS Busylight Support ([ba756be](https://github.com/JnyJny/busylight-core/commit/ba756be1fb9ff48317574b2f14f1f931c3500f58))
- Updated Tests ([b25f72d](https://github.com/JnyJny/busylight-core/commit/b25f72db8bcbf4487812519330ca8a33c8157d94))
- Refactored Embrava Blynclight ([c964555](https://github.com/JnyJny/busylight-core/commit/c9645555cd9030fbe55bb275b62df23a3eaca1e3))
- Updated MuteMe vendor tests to include MuteSync ([28dc5d1](https://github.com/JnyJny/busylight-core/commit/28dc5d117ce3c89573e6b24eed6c0bc68fd9f061))
- Removed empty vendor test for busytag ([1b30067](https://github.com/JnyJny/busylight-core/commit/1b30067bea79bf90ec126dd11d7c643a9681684a))
- Updated tests" -m "Moved MuteSync fixtures to MuteMe module. ([c232f91](https://github.com/JnyJny/busylight-core/commit/c232f9183f71a95a5c998af3b2337b72fcca4d53))
- Refactor Light API to simplify device support pattern ([e6a09c4](https://github.com/JnyJny/busylight-core/commit/e6a09c4c00b1e88b98fa696e53c5da00d5ebfdfe))
- MuteSync now vendored by MuteMe ([577913a](https://github.com/JnyJny/busylight-core/commit/577913a0261a262e44d2318221f59d9131218c42))
- MuteSync now vendored by MuteMe ([dd24156](https://github.com/JnyJny/busylight-core/commit/dd241562675ce97041e7da678d986d428acc2469))
- Moved BusyTag to the Luxafor vendor subdirectory. ([8ee7ed0](https://github.com/JnyJny/busylight-core/commit/8ee7ed0d8997da56ea169dab24e6f3bda7b174da))
- Updated tests/conftest.py ([420361a](https://github.com/JnyJny/busylight-core/commit/420361a7ef4bc30a4a5d61f7d387c86cdc3538f2))
- Updated pyproject.toml ([204bf44](https://github.com/JnyJny/busylight-core/commit/204bf44280d980abb68ec133758c4341dcd92c1f))
- Updated README.md ([602a686](https://github.com/JnyJny/busylight-core/commit/602a6864e3fcae3bccd135d9468e15ccb6ef7aa6))
- Updated gitignore for .claude ([1435089](https://github.com/JnyJny/busylight-core/commit/14350894ea9f44c1e0e86fef0943da19e3c90f7f))
- Updated envrc ([f40fbc8](https://github.com/JnyJny/busylight-core/commit/f40fbc8ebd68f505653444f8ae2bd56a19858e45))
- Updated docs to highlight busylight_core.Light class ([c1059d6](https://github.com/JnyJny/busylight-core/commit/c1059d69c4b1e0416d7638774896c4d2fae03d86))
- Updated .envrc ([e008dfb](https://github.com/JnyJny/busylight-core/commit/e008dfbe90b309291b52faa24fde662e29c99fa9))
- Prominently feature Light class in API reference ([2f26ff4](https://github.com/JnyJny/busylight-core/commit/2f26ff480e38aa1e329a285126b81f8523bc35a9))
- Improve API reference navigation with organized table of contents ([2f2f48f](https://github.com/JnyJny/busylight-core/commit/2f2f48fcbdbef0678f53af5f9842a2c851c17040))
- Remove pre-commit hook installation from contributing docs ([aac516e](https://github.com/JnyJny/busylight-core/commit/aac516ef668031b68c4f4187d6ef2519ff542c82))
- Update documentation to remove CLI references and expand features ([76f5bf3](https://github.com/JnyJny/busylight-core/commit/76f5bf30c11831ab229e60d8856510309097532e))
## [0.2.4](https://github.com/JnyJny/busylight-core/releases/tag/v0.2.4) - 2025-07-13

### Other

- Increased minimum python version to 3.11 ([e312f9d](https://github.com/JnyJny/busylight-core/commit/e312f9dbe01142b4f516b4aa48628aa41967fc9c))
## [0.2.3](https://github.com/JnyJny/busylight-core/releases/tag/v0.2.3) - 2025-07-13

### Bug Fixes

- Fixed bug in conftest.py ([222963a](https://github.com/JnyJny/busylight-core/commit/222963aea95e5fef833a18a6b01a5801660badfd))
## [0.2.2](https://github.com/JnyJny/busylight-core/releases/tag/v0.2.2) - 2025-07-13

### Other

- Narrowed supported python versions ([f9f19d9](https://github.com/JnyJny/busylight-core/commit/f9f19d992d8fef331e4322f090811d33d519a545))
## [0.2.1](https://github.com/JnyJny/busylight-core/releases/tag/v0.2.1) - 2025-07-13

### Other

- Added dev dep tomlkit ([87a222c](https://github.com/JnyJny/busylight-core/commit/87a222c53e9d05172b70f4f8e2f4f3bef340654c))
- Initial commit of CLAUDE.md ([ad15f96](https://github.com/JnyJny/busylight-core/commit/ad15f968cf38d199e1028bdf8dd0c1f71ba417ee))
## [0.2.0](https://github.com/JnyJny/busylight-core/releases/tag/v0.2.0) - 2025-07-13

### Bug Fixes

- Fix async test failures and deprecation warnings ([0da7618](https://github.com/JnyJny/busylight-core/commit/0da76187c60c377efc336d10396d17332d0459f6))

### Other

- Transplanted working busylight_core into new template hotness. ([d6dbd01](https://github.com/JnyJny/busylight-core/commit/d6dbd0192c8239ad6684ec84cd50c3dcd0d20ba5))
- initial commit ([fd5ca26](https://github.com/JnyJny/busylight-core/commit/fd5ca26333bae3d0cf314ebae66b566dc278212e))


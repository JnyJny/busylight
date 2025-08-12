# CHANGELOG

## [v0.42.0](https://github.com/JnyJny/busylight/releases/tag/v0.42.0) - 2025-08-12 03:52:48

## Release v0.42.0

- v0.42.0 (7017a66)
- Merge pull request #478 from JnyJny/features/improve-manager-usability (9dc04e3)
- docs: Add comprehensive Sphinx-style docstrings and improve type hints (d2c64dc)
- fix: correct web API off endpoints and add blink task cancellation (fb3dce1)
- fix: update web API blink endpoints to use new LightController fluent API (9cecb36)
- fix: update web API endpoints to use light.hardware instead of light.info (651dd45)
- feat: replace LightManager with simplified fluent LightController (8c91e5b)
- Merge pull request #477 from JnyJny/features/improve-test-coverage (7767ffb)
- feat: improve test coverage from 59% to 77% (0eccc09)
- feat: significantly improve test coverage (ba9ea92)
- docs(CHANGELOG): update release notes (74d1f20)
- fix: optimize release workflow to prevent hanging (3fa9aea)
- v0.41.3 (f3cc6c4)
- cicd: missing permission causes automatic release action fail. (401cfb7)
- v0.41.2 (cf900b5)
- v0.41.1 (87dc252)
- Merge pull request #476 from JnyJny/features/fix-webapi-extras-optional (9caed64)
- fix: make CLI work without webapi extras (67772d6)
- v0.41.0 (f3a791c)
- Merge pull request #475 from JnyJny/features/refactor-effects-taskmixin (ee4222c)
---
**Full Changelog**: https://github.com/JnyJny/busylight/compare/v0.42.0...v0.42.0


## What's Changed
* Improve test coverage from 59% to 77% by @JnyJny in https://github.com/JnyJny/busylight/pull/477
* feat: replace LightManager with simplified fluent LightController by @JnyJny in https://github.com/JnyJny/busylight/pull/478


**Full Changelog**: https://github.com/JnyJny/busylight/compare/v0.41.3...v0.42.0

### Feature

- general:
  - replace LightManager with simplified fluent LightController ([8c91e5b](https://github.com/JnyJny/busylight/commit/8c91e5b9dc65994e783cd77fdbc52d52eafd601d)) ([#478](https://github.com/JnyJny/busylight/pull/478))
  - improve test coverage from 59% to 77% ([0eccc09](https://github.com/JnyJny/busylight/commit/0eccc09b96010467db5faf65930b1f4714a6aabe)) ([#477](https://github.com/JnyJny/busylight/pull/477))
  - significantly improve test coverage ([ba9ea92](https://github.com/JnyJny/busylight/commit/ba9ea9283aa2d64645e4139fbd7ef8075e2d24c2)) ([#477](https://github.com/JnyJny/busylight/pull/477))

### Bug Fixes

- general:
  - correct web API off endpoints and add blink task cancellation ([fb3dce1](https://github.com/JnyJny/busylight/commit/fb3dce1c2a89aa43b1e6701970e3795122463809)) ([#478](https://github.com/JnyJny/busylight/pull/478))
  - update web API blink endpoints to use new LightController fluent API ([9cecb36](https://github.com/JnyJny/busylight/commit/9cecb3667681c531dfc433cdfcf490369e20390f)) ([#478](https://github.com/JnyJny/busylight/pull/478))
  - update web API endpoints to use light.hardware instead of light.info ([651dd45](https://github.com/JnyJny/busylight/commit/651dd451be90f33fc4ca084a880ed0d94a40f17c)) ([#478](https://github.com/JnyJny/busylight/pull/478))
  - optimize release workflow to prevent hanging ([3fa9aea](https://github.com/JnyJny/busylight/commit/3fa9aea560ae06bf60b242fe8c9007ba9fd63f4f))

### Documentation

- general:
  - Add comprehensive Sphinx-style docstrings and improve type hints ([d2c64dc](https://github.com/JnyJny/busylight/commit/d2c64dc5768e65fefb8cbf33be696da6da69f745)) ([#478](https://github.com/JnyJny/busylight/pull/478))

## [v0.41.3](https://github.com/JnyJny/busylight/releases/tag/v0.41.3) - 2025-08-10 17:19:41

## [v0.37.0](https://github.com/JnyJny/busylight/releases/tag/v0.37.0) - 2025-07-18 21:31:45

This release of busylight-for-humans is the first release using the new [busylight-core][0] library, which supplies the unified API for working with various USB lights. Going forward, busylight-for-humans will supply the command-line and web interfaces and busylight-core should be used for projects that want to integrate USB light controls.

[0]: https://github.com/JnyJny/busylight-core

## [v0.35.4](https://github.com/JnyJny/busylight/releases/tag/v0.35.4) - 2025-06-06 15:16:44

Visible Changes:
- Still fighting Windows, trying to craft a byte string that different versions of the OS will accept.

Invisible Changes:

- Started ruff-ing source code instead of using black and isort. It's just so fast.

### Bug Fixes

- general:
  - fixed mypy poe task to work with src layout ([5c2abca](https://github.com/JnyJny/busylight/commit/5c2abcad42a707aa0ebcbecd47b0f55d45505ba9))

## [v0.35.2](https://github.com/JnyJny/busylight/releases/tag/v0.35.2) - 2025-05-18 21:25:32

## [0.33.0](https://github.com/JnyJny/busylight/releases/tag/0.33.0) - 2024-12-03 17:18:07

This release includes lots of dependency updates and two big fixes:

- Issue #416 / commit e9ee49f - Fix for infinite async task creation
- Issue #417 / commit 63b874f - Prepend zero byte to data buffer on Windows

With these two fixes, I'm going to conditionally claim Windows is now supported.

### Bug Fixes

- general:
  - building a wheel ([74ca283](https://github.com/JnyJny/busylight/commit/74ca283e2250564f422d904ece1b9ab0dd9a8f6c)) ([#369](https://github.com/JnyJny/busylight/pull/369))

## [0.27.6](https://github.com/JnyJny/busylight/releases/tag/0.27.6) - 2023-11-24 05:15:54

This release was supposed to be a cool hack that fixed a bug reported in issue #301. Instead, after writing the cool hack and testing it, I discovered that all my publishing infrastructure was borked. I switched from a Makefile to using poethepoet to specify build and publish rules in my pyproject.toml. While I was in there goofing with it, I completely borked the extras section which broke the ability to install busylight-for-humans with and without the webapi extras. It's fixed now and I also fixed the pytests for pydantic model checking that were failing with the latest pydantic and finally fixed the poe rules to push the tags to GitHub so the workflows will run.  Tests are passing, bugs are fixed and publishing seems unbroken for now.

### Bug Fixes

- general:
  - fixed whitespace in pytest-linux workflow ([310eb02](https://github.com/JnyJny/busylight/commit/310eb02e8c29e9ba8ae647e786da278698366149))

## [0.26.0](https://github.com/JnyJny/busylight/releases/tag/0.26.0) - 2023-02-24 18:45:16

I forgot to make releases for 0.25 (at the least) so here is 0.26.0.
- updated workflows to use checkout@v3 and setup-python3@v4
- disabled logging by default for busylight and it's packages to cut down on noise
- updated fastapi to pull in patched starlette which suffered from a config file vulnerability
- small webapi fixes to keep status from failing while lights are animating.
- Luxafor Bluetooth support from contributor @volkangurel 
- Many many updated dependencies, thanks @dependabot!

## [0.22.1](https://github.com/JnyJny/busylight/releases/tag/0.22.1) - 2022-09-12 01:53:13

New features:
- Serial USB support

New light support:
- Compusa fit-statUSB
- MuteMe MuteMe
- MuteSync MuteSync

Deprecated:
- The `fastapi` based web api is now deprecated and will be replaced with a standalone project.


Windows tests are passing, weirdly. I still don't claim Windows support but it might be working better now. 

### Bug Fixes

- general:
  - fixed missing numbers ([0acef61](https://github.com/JnyJny/busylight/commit/0acef6126e3e73cbeec7c9c6dc750d6c4ce9c018))

### Refactor

- general:
  - excised ColorTuple and ColorList ([8a7d21d](https://github.com/JnyJny/busylight/commit/8a7d21d6d19c01679163bc7009dc8c18a21dad16))

## [0.21.1](https://github.com/JnyJny/busylight/releases/tag/0.21.1) - 2022-07-16 16:02:25

Fixed a self-inflicted bug regarding version tracking that broke FastAPIs automatic documentation generation. All good now.

### Feature

- general:
  - feature: initial support for reading state of Luxafor Mute button status ([df5684a](https://github.com/JnyJny/busylight/commit/df5684a8c205e769be208d0c8bf17ba858501ded))
  - feature: list subcommand prints lights in vendor sorted order ([82a3d09](https://github.com/JnyJny/busylight/commit/82a3d09b19fe3e6d0f7cd609a691f9cfd522703b))
  - feature: release Makefile targets now update requirements.txt ([6fe65a9](https://github.com/JnyJny/busylight/commit/6fe65a9701ee7e9b0330e37d65faf910c49bb044))

### Bug Fixes

- general:
  - reverted requirements.txt dependency in publish rules ([a09e140](https://github.com/JnyJny/busylight/commit/a09e140034646ad198e34cbf3ae49dc87f018a07))

## [0.21.0](https://github.com/JnyJny/busylight/releases/tag/0.21.0) - 2022-07-15 18:31:22

This release includes initial support for the MuteMe LLC's family of devices:
- MuteMe Original
- MuteMe Mini

### Bug Fixes

- general:
  - broken blink implementation and documentation ([3b516ef](https://github.com/JnyJny/busylight/commit/3b516ef7d98d6d3d07e27a2b6cdc6f8df783956b))

### Refactor

- general:
  - cleaned up support for MuteMe devices ([e012ba1](https://github.com/JnyJny/busylight/commit/e012ba11d3e07c0a8822ec6a8b413994cb971e64))

## [0.20.5](https://github.com/JnyJny/busylight/releases/tag/0.20.5) - 2022-06-29 19:57:12

- Improved blinking with multiple devices (it works now, so definitely improved)
- Test coverage is hovering around 87% which is better.
- Generally a more pleasing and consistent interface.

### Feature

- general:
  - feature: added alias routes for webapi status queries ([5173453](https://github.com/JnyJny/busylight/commit/5173453ee23871b6ceb1471670f5ac085f096252))
  - feature: api exports pydantic models from toplevel ([a204f09](https://github.com/JnyJny/busylight/commit/a204f090543963ebaab464e9ea09ab4eaf72afab))
  - feature: clamped scale between 0 and 1.0 ([7c0471c](https://github.com/JnyJny/busylight/commit/7c0471cb7cc668ee67fc3259dc88c9b73946b2cd))
  - feature: added dim attribute to API model ([25a9254](https://github.com/JnyJny/busylight/commit/25a9254b8e74b351cc50be8385973b31e65d52fc))
  - feature: combined parse_color_string and scale_color ([a204e76](https://github.com/JnyJny/busylight/commit/a204e76bcdfe07102adf021c1b4e1ceec187602a))
  - feature: tested colortuple_to_name with bogus colors ([d7b142a](https://github.com/JnyJny/busylight/commit/d7b142a5ea438ea157630a371b4d3ed62cfa2971))
  - feature: added tests for scale_color ([8ebaf3f](https://github.com/JnyJny/busylight/commit/8ebaf3fc4a121e702d390ca5ea3b8356804f4cae))
  - feature: print usage if called with no arguments ([1e5fa5b](https://github.com/JnyJny/busylight/commit/1e5fa5bff5819d27c65303fa42a2b790f77e5975))
  - features: updated function names, added scaled_color ([d646548](https://github.com/JnyJny/busylight/commit/d64654850b6936af129ac853f824afbd024791a1))
  - feature: improved busylight.lights.exceptions and tests ([3341d75](https://github.com/JnyJny/busylight/commit/3341d751232e443c113c4da4ea86575276fe797f))

### Bug Fixes

- general:
  - changed scope for anyio_backend and client to module ([a36cea6](https://github.com/JnyJny/busylight/commit/a36cea6a5f20f973c24fa803f4c4db9453f16efe))
  - bad f-string in list cli test ([a702708](https://github.com/JnyJny/busylight/commit/a70270896c7335cbcaaba48e70c85a3180587bdc))
  - bug & feature: fixed broken color parsing, added dim support ([87253c5](https://github.com/JnyJny/busylight/commit/87253c56e3f77ff0b6f74023c7d9d99df4ef0c42))
  - bugs: lights left on after timeout, throb not using scaled colors ([5fafb63](https://github.com/JnyJny/busylight/commit/5fafb63dd33384d8526a57de8d262e608b7d3908))
  - clamped step in effects.Gradient init ([aaffd10](https://github.com/JnyJny/busylight/commit/aaffd106fd3a38892129c15c91490b7886bd0de3))
  - left an old implementation in the manager on_supervisor ([e90988a](https://github.com/JnyJny/busylight/commit/e90988a49dfccc93d1f09f43a9549107d17d2f92))
  - bugfix: list subcommand only showing first light ([c1ea990](https://github.com/JnyJny/busylight/commit/c1ea99066061768cbfaac42ce26198760573240f))

### Documentation

- general:
  - module docstring elaboration ([66429d3](https://github.com/JnyJny/busylight/commit/66429d3d154784ca396bf1af5e0fadf4116315f6))

### Refactor

- general:
  - __main__.webapi renamed to __main__.webcli ([76185ee](https://github.com/JnyJny/busylight/commit/76185eeddc0adcc1277c5525f1113142f17bfe6a))
  - webcli testing moved out of cli testing ([0bf5e31](https://github.com/JnyJny/busylight/commit/0bf5e3159c141426d121c5fe141800f1c2af5c1a))
  - removed webapi testing from cli testing ([594c96a](https://github.com/JnyJny/busylight/commit/594c96a5ea8c38b286f3de6f7c0d9d85e1ee6286))
  - simplified api/__init__.py ([457ee7c](https://github.com/JnyJny/busylight/commit/457ee7c125bc3f912333ea72b65f8d769c750c31))
  - cli subcommand 'throb' renamed to 'pulse' to match web api ([c928440](https://github.com/JnyJny/busylight/commit/c928440974afe874343969c0d0cb7ee3f25488de))
  - web api code ([5e92392](https://github.com/JnyJny/busylight/commit/5e92392009329bcbc3be61ee0b90b21d6cb02a59))

## [0.17.0](https://github.com/JnyJny/busylight/releases/tag/0.17.0) - 2022-04-25 21:49:38

Ok I'm _sorry_, but I'm not **sorry**. This version contains breaking changes. Lots of breaking changes. So many breaking changes. All of these changes were in service of converting the programming model from threads (to allow each light to be animated concurrently by a separate software thread), to `asyncio.Task`s.  Converting to tasks allowed each thread to be animated concurrently from a single thread. The driving reason is the explicitly single-threaded nature of `hidapi` which was beginning to exhibit more unstable behavior when used in a multi-threaded environment. 

Version 0.17.0 is a near complete re-write of `busylight.lights.USBLight`:
- improved subclass support
- expanded utility of class methods for `USBLight`
- removed threading support for animations and keep alive activities
- added asyncio support for animations and keep alive activities
- improved exception handling to detect unplugged/unavailable lights

The manager class `busylight.manager.LightManager` was re-written:
- updated for `USBLight` class and subclasses
- improved exception handling of lights
- switched threading for asyncio to support concurrency

The command-line interface was updated to use the `LightManager` class with only minor changes to the actual interface.

The `tests` suite was updated for the new asyncio implementation. The mocking isn't quite as clean as I would like, but it's good enough for now. The tests should run whether or not there are physical lights connected.

Lastly, the FastAPI web interface underwent significant changes:
- routes were removed
- routes were expanded to accept optional keyword arguments

Note: changes between versions 0.16 and 0.17 were mostly python version compatibility fixes and GitHub Action maintenance. The real changes happened between 0.15 and 0.16. 

**Full Changelog**: https://github.com/JnyJny/busylight/compare/0.15.0...0.17.0

### Feature

- general:
  - feature: added busyserve docs ([0dbc56e](https://github.com/JnyJny/busylight/commit/0dbc56ed84c2c9761b03865b943aff490984a742))
  - feature: added colortuple_to_name function ([f74799c](https://github.com/JnyJny/busylight/commit/f74799c9134e8e876c8af6fef40a47d8091c17b5))

### Bug Fixes

- general:
  - importlib.metadata missing is python <3.8 ([341eabe](https://github.com/JnyJny/busylight/commit/341eabeb093a35690577657ecc342419154b943f))
  - typed a Generator yeild with List when it should have been Dict ([5708d28](https://github.com/JnyJny/busylight/commit/5708d28b28adca681ec20115fd1b46e1ca16d6e4))
  - bugfix: improved exception handling in main ([6a51178](https://github.com/JnyJny/busylight/commit/6a511784e79eaf964e8b91ac60bec110b2f0b865))
  - bugfix: Removed KeyboardInterrupt handling. ([cabdf4a](https://github.com/JnyJny/busylight/commit/cabdf4a2cecd9ad082a9c446b15e98472ce4b950))
  - bugfix: removed unnecessary Speed.Stop state ([fc0a386](https://github.com/JnyJny/busylight/commit/fc0a386b3ece52c04c71b31d6a4b270bcc930ab8))
  - bugfix: busylight.manager.LightManager overhaul ([76ce2c1](https://github.com/JnyJny/busylight/commit/76ce2c1b882b179760aca70c6c9102d7b1183df8))

## [0.15.4](https://github.com/JnyJny/busylight/releases/tag/0.15.4) - 2022-03-30 21:36:13

Barring unforeseen circumstances, this will be the finial version of Busylight For Humans™ utilizing a threaded model. The next version, provisionally 0.16.0, will use asynchronous I/O to implement features that previously used threads. The `hidapi` framework is single threaded, so it was basically lucky on my part that `busylight` worked as well as it did.

## [0.14.0](https://github.com/JnyJny/busylight/releases/tag/0.14.0) - 2022-02-05 20:24:17

ThingM blink lights now blink. 

## [0.13.2](https://github.com/JnyJny/busylight/releases/tag/0.13.2) - 2021-11-09 03:13:58

This release fixes blink for the Luxafor Flag. It blinks now, where before it didn't. 

### Bug Fixes

- general:
  - bugfix: relaxed bounds checking on USBLight.strategy return value ([62cef0b](https://github.com/JnyJny/busylight/commit/62cef0bffcccf3ddfb041c66549eb7790cf7ebd4))
  - bugfix: manager.lights_for() returns a list ([379c364](https://github.com/JnyJny/busylight/commit/379c364aa2b5184e20a6b01288b007e1de77b7a9))

### Documentation

- general:
  - docstring: fixed blink and blink_async docstrings ([c5ccfb5](https://github.com/JnyJny/busylight/commit/c5ccfb54dd3d54033cea97dc9d7d0ab78fabd803))

## [0.12.5](https://github.com/JnyJny/busylight/releases/tag/0.12.5) - 2021-05-20 23:00:56

This patch release fixed a big bug in `busylight.manager.LightManager.update()` and will only matter to users of the web API. The `LightManager` will now be able to realize that devices have been plugged and unplugged while it wasn't looking.

## [0.12.2](https://github.com/JnyJny/busylight/releases/tag/0.12.2) - 2021-05-18 18:06:46

The optional web API is now working again after some minor breakage, please refer to the builtin API documentation:

```
$ busylight server
...
```

and navigate a browser to "http://hostname:port/docs" to see the automatically generated API documentation.

Bugs fixed:
- Kuando BusyLight keep-alive thread was too good at it's job. 

### Bug Fixes

- general:
  - fixing the busylight markdown ([5d5e774](https://github.com/JnyJny/busylight/commit/5d5e774b82757cfa9171b3495631feaed23c5a36))

### Documentation

- general:
  - docstring updates for cli ([5396ef8](https://github.com/JnyJny/busylight/commit/5396ef8c6cf1abdde0817fc9fcc1e2a95b544786))

\* *This CHANGELOG was automatically generated by [auto-generate-changelog](https://github.com/BobAnkh/auto-generate-changelog)*

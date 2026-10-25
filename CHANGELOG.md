# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-10-24

### Changed
- **Breaking:** requires Reflex `>=0.10.0` and Python `>=3.11` (Reflex 0.10
  dropped Python 3.10).
- Build backend requires `setuptools>=78.1.1`.
- Demo apps pin `reflex==0.10.0`.

### Fixed
- Timelines lost their `height`/`width`: TimelineJS overwrites the `className`
  of the node it mounts on, dropping the class Reflex uses for sizing. The
  wrapper now keeps the sized props on an outer `div` and mounts TimelineJS on
  an inner `div` that fills it.
- `Slide.validate()` / `TimelineData.validate()` reject a `media` block without
  a `url`, which TimelineJS cannot render (`Cannot read properties of undefined
  (reading 'match')`).

### Added
- GitHub Actions CI (tests on Python 3.11–3.13, build, `twine check`) and a
  tag-triggered PyPI release workflow (Trusted Publishing).

## [0.1.2]

- Sandbox demo (`examples/tl_demo`) installing the package from PyPI.

## [0.1.1]

- Repository metadata in `pyproject.toml` and README.

## [0.1.0]

- Initial release: native Reflex wrapper for Knight Lab TimelineJS with typed
  data builders, all TimelineJS options and event triggers.

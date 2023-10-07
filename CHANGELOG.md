# Changelog

## [v0.4.0](https://github.com/XaviArnaus/janitor/releases/tag/v0.4.0)

### Added

- Runner to monitor Git repositories and publish the identified new version from the Changelog
- New `TODO.md` list ;-)

### Changed

- `MastodonHelper` now is able to receive connection params injected
- Bumped pyxavi to 0.5.1

## [v0.3.0](https://github.com/XaviArnaus/janitor/releases/tag/v0.3.0)

### Added

- Runner to update Directic's Dynamic DNS

### Changed

- Changelog iterated to adhere to [Common Changelog](https://common-changelog.org). Will start from this version on.
- Bumped pyxavi to 0.5.0

## [v0.2.0](https://github.com/XaviArnaus/janitor/releases/tag/v0.2.0)

- Add Firefish support by bumping pyxavi to v0.4.0. 
- pyxavi v0.4.0 makes `logger.getLogger()` deprecated and should move to `logger.get_logger()`. Catching up.
- Add a `publish_test.py` entry point runnable with `make publish_test` to fully test a Mastodon publishing implementation.
- Move all `Mastodon.py` interactions behind the `MastodonHelper` instance selection, as a first step before abstracting it out.
- Adding a CHANGELOG.md
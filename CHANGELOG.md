# Changelog

ℹ️ If you're upgrading between versions, please see the document [Upgrading Guide](UPGRADING.md).

## [Unreleased](https://github.com/XaviArnaus/janitor)

### Changed

- Fix issue with the main runner in Raspberry ([#24](https://github.com/XaviArnaus/janitor/pull/24))
- Fix issue with controlling the listener with the main runner ([#25](https://github.com/XaviArnaus/janitor/pull/25))

## [v0.5.0](https://github.com/XaviArnaus/janitor/releases/tag/v0.5.0)

### Added

- A *config migration tool* that converts the single old config file into the sliced new ones ([#21](https://github.com/XaviArnaus/janitor/pull/21))
- A `UPGRADING.md` document to assist on Upgrading from version to version ([#21](https://github.com/XaviArnaus/janitor/pull/21))
- Added the ability for the Git Monitor to use arbitrary Mastodon named accounts for each monitored repository ([#23](https://github.com/XaviArnaus/janitor/pull/23))

### Changed

- README and documentation has been iterated ([#20](https://github.com/XaviArnaus/janitor/pull/20))
- The *config* file has been sliced into several *config* files per module ([#21](https://github.com/XaviArnaus/janitor/pull/21))
- The `validate_config` now is improved and considers all config files ([#21](https://github.com/XaviArnaus/janitor/pull/21))
- Now all mastodon publishing accounts are registered inside the `mastodon.yaml` config file, each under a name, to easily be referenced from other Janitor modules ([#22](https://github.com/XaviArnaus/janitor/pull/22))

### Removed

- Removed the old-main `config.yaml.dist`

## [v0.4.0](https://github.com/XaviArnaus/janitor/releases/tag/v0.4.0)

### Added

- Runner to monitor Git repositories and publish the identified new version from the Changelog
- New `TODO.md` list ;-)
- Added a main runner to serve as a Command Line Interface tool.
- Added the possibility from the config file to run the listener in debug mode
- Added a new `definitions` root module to serve global info like the root directory.

### Changed

- `MastodonHelper` now is able to receive connection params injected
- Bumped pyxavi to 0.5.2
- Moved all runners into an internal directory. They can't be called directly anymore.

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
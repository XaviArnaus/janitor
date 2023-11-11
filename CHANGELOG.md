# Changelog

ℹ️ If you're upgrading between versions, please see the document [Upgrading Guide](UPGRADING.md).

## [Unreleased](https://github.com/XaviArnaus/janitor/)

### Added

- The Publisher retries 3 times with a sleep of 10 seconds in between ([#35](https://github.com/XaviArnaus/janitor/pull/35))
- Re-queue the message in case of total failure while publishing ([#35](https://github.com/XaviArnaus/janitor/pull/35))
- Support *publish only oldest in queue every iteration* feature, based on the [Mastodon Echo Bot](https://github.com/XaviArnaus/mastodon-echo-bot) ([#35](https://github.com/XaviArnaus/janitor/pull/35))
- Add a set of Publisher's methods to improve internal code ([#35](https://github.com/XaviArnaus/janitor/pull/35))
- Support for `publish_queue` for the Scheduler ([#35](https://github.com/XaviArnaus/janitor/pull/35))
- Added some colors into the logging to easy the reading ([#38](https://github.com/XaviArnaus/janitor/pull/38))

### Changed

- Now the System metrics templates live in the config file, not in the class ([#34](https://github.com/XaviArnaus/janitor/pull/34))
- Now the messages sent as DIRECT and PRIVATE must come with a mention and will appear private only ([#34](https://github.com/XaviArnaus/janitor/pull/34))
- Manage the `MastodonHelper` internally in the Publisher ([#35](https://github.com/XaviArnaus/janitor/pull/35))
- Manage the `MastodonConnectionParams` internally in the Publisher ([#35](https://github.com/XaviArnaus/janitor/pull/35))
- Reduced the amount of `info` logging to produce cleaner logs ([#38](https://github.com/XaviArnaus/janitor/pull/38))
- Make Flask to log above WARNING ([#38](https://github.com/XaviArnaus/janitor/pull/38))
- Show who is sending a request to the Listener ([#38](https://github.com/XaviArnaus/janitor/pull/38))

### Fixed

- Fix a wrong param name in `mastodon.yaml.dist` ([#39](https://github.com/XaviArnaus/janitor/pull/39))
- Fix a bug that made fail the `bin/jan mastodon test` command ([#39](https://github.com/XaviArnaus/janitor/pull/39))

## [v0.5.1](https://github.com/XaviArnaus/janitor/releases/tag/v0.5.1)

### Added

- A new CLI command (the main runner) to return the current external address ([#29](https://github.com/XaviArnaus/janitor/pull/29))
- New CLI arguments to override logging config and print it to stdout ([#29](https://github.com/XaviArnaus/janitor/pull/29))
- A new CLI and Scheduler command to rotate the log file ([#30](https://github.com/XaviArnaus/janitor/pull/30))

### Changed

- Fix issue with the main runner in Raspberry ([#25](https://github.com/XaviArnaus/janitor/pull/25))
- Fix issue with controlling the listener with the main runner ([#26](https://github.com/XaviArnaus/janitor/pull/26) & [#27](https://github.com/XaviArnaus/janitor/pull/27))
- Fix Directnic's Dynamic DNS Updater runner ([#28](https://github.com/XaviArnaus/janitor/pull/28))

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
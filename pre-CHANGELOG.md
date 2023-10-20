# pre-Changelog

## [Unreleased](https://github.com/XaviArnaus/janitor)

### Added

- A *config migration tool* that converts the single old config file into the sliced new ones (#21)
- A `UPGRADING.md` document to assist on Upgrading from version to version (#21)
- Added the ability for the Git Monitor to use arbitrary Mastodon named accounts for each monitored repository (#23)

### Changed

- README and documentation has been iterated (#20)
- The *config* file has been sliced into several *config* files per module (#21)
- The `validate_config` now is improved and considers all config files (#21)
- Now all mastodon publishing accounts are registered inside the `mastodon.yaml` config file, each under a name, to easily be referenced from other Janitor modules (#22)
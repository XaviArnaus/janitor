# pre-Changelog

## [v0.5.0](https://github.com/XaviArnaus/janitor/releases/tag/v0.5.0)

### Added

- A *config migration tool* that converts the single old config file into the sliced new ones.
- A `UPGRADING.md` document to assist on Upgrading from version to version

### Changed

- README and documentation has been iterated
- The *config* file has been sliced into several *config* files per module
- The `validate_config` now is improved and considers all config files
- Now all mastodon publishing accounts are registered inside the `mastodon.yaml` config file, each under a name, to easily be referenced from other Janitor modules.
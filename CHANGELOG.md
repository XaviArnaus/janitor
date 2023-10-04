# v0.2.0

- Add Firefish support by bumping pyxavi to v0.4.0. 
- pyxavi v0.4.0 makes `logger.getLogger()` deprecated and should move to `logger.get_logger()`. Catching up.
- Add a `publish_test.py` entry point runnable with `make publish_test` to fully test a Mastodon publishing implementation.
- Move all `Mastodon.py` interactions behind the `MastodonHelper` instance selection, as a first step before abstracting it out.
- Adding a CHANGELOG.md
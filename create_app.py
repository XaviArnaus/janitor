from pyxavi.config import Config
from pyxavi.logger import Logger
from janitor.lib.mastodon_helper import MastodonHelper

#######
# This is meant to be run just once.
##


class CreateApp:

    def __init__(self):
        self._config = Config()
        self._logger = Logger(self._config).get_logger()
        self._logger.info("Run Create App")

    def run(self):
        self._logger.info("Run Create App")
        MastodonHelper.create_app(
            self._config.get("mastodon.instance_type"),
            self._config.get("mastodon.app_name"),
            api_base_url=self._config.get("mastodon.api_base_url"),
            to_file=self._config.get("mastodon.credentials.client_file")
        )
        self._logger.info("Finished Create App")


if __name__ == '__main__':
    CreateApp().run()

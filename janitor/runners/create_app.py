from pyxavi.config import Config
from pyxavi.terminal_color import TerminalColor
from pyxavi.mastodon_helper import MastodonHelper
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import logging
import os


#######
# This is meant to be run just once.
##
class CreateApp(RunnerProtocol):

    def __init__(
        self, config: Config = None, logger: logging = None, params: dict = None
    ) -> None:
        self._config = config
        self._logger = logger

    def run(self):
        self._logger.info(f"{TerminalColor.MAGENTA}Starting Create App{TerminalColor.END}")
        MastodonHelper.create_app(
            self._config.get("mastodon.named_accounts.default.instance_type"),
            self._config.get("mastodon.named_accounts.default.app_name"),
            api_base_url=self._config.get("mastodon.named_accounts.default.api_base_url"),
            to_file=os.path.join(
                ROOT_DIR,
                self._config.get("mastodon.named_accounts.default.credentials.client_file")
            )
        )
        self._logger.info("Finished Create App")

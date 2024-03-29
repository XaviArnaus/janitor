from pyxavi.terminal_color import TerminalColor
from pyxavi.config import Config
from janitor.lib.publisher import Publisher
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import logging

DEFAULT_NAMED_ACCOUNT = ["test", "default"]


class PublishTest(RunnerProtocol):
    '''
    Runner that publishes a test
    '''

    def __init__(
        self, config: Config = None, logger: logging = None, params: dict = None
    ) -> None:
        self._config = config
        self._logger = logger
        self.load_params(params=params)

    def load_params(self, params: dict) -> None:
        named_account = None
        preferred_named_accounts = DEFAULT_NAMED_ACCOUNT
        if params is None:
            params = {}
        else:
            if "named_account" in params and params["named_account"] is not None:
                preferred_named_accounts = [params["named_account"]] + preferred_named_accounts
        for account in preferred_named_accounts:
            if self._config.key_exists(f"mastodon.named_accounts.{account}"):
                named_account = account
                break

        if named_account is None:
            raise RuntimeError(
                "Could not find any of the defined possible named accounts: " +
                preferred_named_accounts
            )
        else:
            self._logger.debug(f"Will publish to {named_account}")
            params["named_account"] = named_account
            self._params = params

    def run(self):
        '''
        Just publish a test
        '''
        try:
            # Publish the message
            self._logger.info(
                f"{TerminalColor.MAGENTA}Publishing Test Message" +
                f"{TerminalColor.END} to account {self._params['named_account']}"
            )
            Publisher(
                config=self._config,
                named_account=self._params["named_account"],
                base_path=ROOT_DIR
            ).info("this is a **test**")

        except Exception as e:
            self._logger.exception(e)

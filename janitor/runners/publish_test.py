from pyxavi.config import Config
from janitor.lib.mastodon_helper import MastodonHelper
from janitor.objects.mastodon_connection_params import MastodonConnectionParams
from janitor.lib.publisher import Publisher
from janitor.objects.message import Message
from janitor.objects.queue_item import QueueItem
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import logging
import os

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
            account_defined = self._config.get(f"mastodon.named_accounts.{account}", None)
            if account_defined is not None:
                named_account = account_defined
                break

        if named_account is None:
            raise RuntimeError(
                "Could not find any of the defined possible named accounts: " +
                preferred_named_accounts
            )
        else:
            self._logger.debug(f"Will publish to {named_account['app_name']}")
            params["named_account"] = named_account
            self._params = params

    def run(self):
        '''
        Just publish a test
        '''
        try:
            # All actions are done under a Mastodon API instance
            conn_params = MastodonConnectionParams.from_dict(self._params["named_account"])
            # If the client_file does not exist we need to trigger the
            #   create app action.
            client_file = os.path.join(ROOT_DIR, conn_params.credentials.client_file)
            if not os.path.exists(client_file):
                self._logger.info(f"The client file did not exist: {client_file}")
                MastodonHelper.create_app(
                    instance_type=conn_params.instance_type,
                    client_name=conn_params.app_name,
                    api_base_url=conn_params.api_base_url,
                    to_file=client_file
                )
            self._logger.info(f"Defined instance type: {conn_params.instance_type}")
            mastodon = MastodonHelper.get_instance(
                config=self._config, connection_params=conn_params, base_path=ROOT_DIR
            )
            wrapper = type(mastodon)
            self._logger.info(f"Loaded wrapper: {wrapper}")

            # Prepare the Publisher
            publisher = Publisher(
                config=self._config,
                mastodon=mastodon,
                connection_params=conn_params,
                base_path=ROOT_DIR
            )

            # Prepare a test message
            self._logger.info("Preparing a test message")
            message = Message(text="this is a **test**")

            # Making it a queue item
            self._logger.info("Making it a queue item")
            queue_item = QueueItem(message=message)

            # Publish the item
            self._logger.info("Publishing the test queue item")
            _ = publisher.publish_one(queue_item)

        except Exception as e:
            self._logger.exception(e)

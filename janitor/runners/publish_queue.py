from pyxavi.config import Config
from janitor.lib.mastodon_helper import MastodonHelper
from janitor.objects.mastodon_connection_params import MastodonConnectionParams
from janitor.lib.publisher import Publisher
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import logging


class PublishQueue(RunnerProtocol):
    '''
    Runner that publishes the queue
    '''

    def __init__(self, config: Config = None, logger: logging = None) -> None:
        self._config = config
        self._logger = logger

    def run(self):
        '''
        Just publishes the queue
        '''
        try:
            # All actions are done under a Mastodon API instance
            conn_params = MastodonConnectionParams.from_dict(
                self._config.get("mastodon.named_accounts.default")
            )
            mastodon = MastodonHelper.get_instance(
                config=self._config, connection_params=conn_params, base_path=ROOT_DIR
            )

            # Read from the queue the toots to publish
            # and publishes all of them
            publisher = Publisher(self._config, mastodon, base_path=ROOT_DIR)
            self._logger.info("Publishing the whole queue")
            publisher.publish_all_from_queue()
        except Exception as e:
            self._logger.exception(e)

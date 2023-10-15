from pyxavi.config import Config
from janitor.lib.mastodon_helper import MastodonHelper
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
            mastodon = MastodonHelper.get_instance(self._config, base_path=ROOT_DIR)

            # Read from the queue the toots to publish
            # and publishes all of them
            publisher = Publisher(self._config, mastodon, base_path=ROOT_DIR)
            self._logger.info("Publishing the whole queue")
            publisher.publish_all_from_queue()
        except Exception as e:
            self._logger.exception(e)

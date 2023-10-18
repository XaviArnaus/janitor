from pyxavi.config import Config
from janitor.lib.mastodon_helper import MastodonHelper
from janitor.lib.publisher import Publisher
from janitor.objects.message import Message
from janitor.objects.queue_item import QueueItem
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import logging
from pyxavi.debugger import dd


class PublishTest(RunnerProtocol):
    '''
    Runner that publishes a test
    '''

    def __init__(self, config: Config = None, logger: logging = None) -> None:
        dd(config)
        self._config = config
        self._logger = logger

    def run(self):
        '''
        Just publish a test
        '''
        try:
            # All actions are done under a Mastodon API instance
            instance_type = self._config.get("mastodon.instance_type")
            self._logger.info(f"Defined instance type: {instance_type}")
            mastodon = MastodonHelper.get_instance(self._config, base_path=ROOT_DIR)
            wrapper = type(mastodon)
            self._logger.info(f"Loaded wrapper: {wrapper}")

            # Prepare the Publisher
            publisher = Publisher(self._config, mastodon, base_path=ROOT_DIR)

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

from pyxavi.logger import Logger
from pyxavi.config import Config
from janitor.lib.mastodon_helper import MastodonHelper
from janitor.lib.publisher import Publisher
from janitor.objects.message import Message
from janitor.objects.queue_item import QueueItem


class PublishTest:
    '''
    Runner that publishes the queue
    '''

    def init(self):
        self._config = Config()
        self._logger = Logger(self._config).get_logger()

        return self

    def run(self):
        '''
        Just publishes the queue
        '''
        try:
            # All actions are done under a Mastodon API instance
            instance_type = self._config.get("mastodon.instance_type")
            self._logger.info(f"Defined instance type: {instance_type}")
            mastodon = MastodonHelper.get_instance(self._config)
            wrapper = type(mastodon)
            self._logger.info(f"Loaded wrapper: {wrapper}")

            # Prepare the Publisher
            publisher = Publisher(self._config, mastodon)

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


if __name__ == '__main__':
    PublishTest().init().run()

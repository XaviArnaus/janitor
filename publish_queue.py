from pyxavi.logger import Logger
from pyxavi.config import Config
from lib.mastodon_helper import MastodonHelper
from lib.publisher import Publisher


class PublishQueue:
    '''
    Runner that publishes the queue
    '''

    def init(self):
        self._config = Config()
        self._logger = Logger(self._config).getLogger()

        return self

    def run(self):
        '''
        Just publishes the queue
        '''
        try:
            # All actions are done under a Mastodon API instance
            mastodon = MastodonHelper.get_instance(self._config)

            # Read from the queue the toots to publish
            # and publishes all of them
            publisher = Publisher(self._config, mastodon)
            self._logger.info("Publishing the whole queue")
            publisher.publish_all_from_queue()
        except Exception as e:
            self._logger.exception(e)


if __name__ == '__main__':
    PublishQueue().init().run()

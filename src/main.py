from pyxavi.config import Config
from .mastodon_helper import MastodonHelper
from .parsers.mastodon_parser import MastodonParser
from .parsers.feed_parser import FeedParser
from .parsers.twitter_parser import TwitterParser
from .publisher import Publisher
import logging

class Main:
    '''
    Main Runner of the Echo bot
    '''
    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))

    def run(self) -> None:
        '''
        Full run
        - Gathers the system information
        - Saves the info tabulated into a file
        - Compares the info to the defined thresholds and decides alarming and notifications
        - Fills the queue with notifications and alarms
        - Publishes the queue

        Set the behaviour in the config.yaml
        '''
        try:
            # All actions are done under a Mastodon API instance
            mastodon = MastodonHelper.get_instance(self._config)

            # Gather the information

            # Read from the queue the posts to publish
            # and do so according to the config parameters
            publisher = Publisher(self._config, mastodon)
            publisher.publish_all_from_queue()
        except Exception as e:
            self._logger.exception(e)


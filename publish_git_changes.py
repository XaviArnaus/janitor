from pyxavi.logger import Logger
from pyxavi.config import Config
from janitor.lib.mastodon_helper import MastodonHelper
from janitor.lib.publisher import Publisher
from janitor.objects.message import Message
from janitor.objects.queue_item import QueueItem
from janitor.lib.git_monitor import GitMonitor
from janitor.objects.repository import Repository


class PublishGitChanges:
    '''
    Runner that goes through all monitored git repositories and detect changes,
    publishing them into the mastodon-like defined account
    '''

    def init(self):
        self._config = Config()
        self._logger = Logger(self._config).get_logger()

        return self

    def run(self):
        '''
        Get the changes and publish them
        '''
        try:
            # Initialize
            monitor = GitMonitor(self._config)

            # Get all repos to monitor
            repositories = list(
                map(lambda x: Repository.from_dict(x), self._config.get("git_monitor.repositories", []))
            )
            for repository in repositories:
                # Check if we already have the repo cloned
                # If not, clone it localy
                monitor.initiate_or_clone_repository(repository=repository)

                # Get the new updates
                monitor.get_updates()

                # Diff the CHANGELOG with the previous commited.
                # Shall we just store what was the one we saw the last?

                # Publish the changes into the Updates account

                # Publish a notification into the Service account






        except Exception as e:
            self._logger.exception(e)


if __name__ == '__main__':
    PublishGitChanges().init().run()

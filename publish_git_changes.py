from pyxavi.logger import Logger
from pyxavi.config import Config
from janitor.lib.mastodon_helper import MastodonHelper
from janitor.objects.mastodon_connection_params import MastodonConnectionParams
from janitor.lib.publisher import Publisher
from janitor.objects.message import Message
from janitor.objects.queue_item import QueueItem
from janitor.lib.git_monitor import GitMonitor
import os


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
            repositories = self._config.get("git_monitor.repositories", [])
            published_projects = []
            for repository in repositories:
                repo_name = repository["name"]

                # Check if we already have the repo cloned
                # If not, clone it localy
                monitor.initiate_or_clone_repository(repository=repository)

                # Get the new updates
                monitor.get_updates()

                # Get the contents of the changelog file, parsed in a dict
                content = monitor.get_changelog_content()
                parsed_content = monitor.parse_changelog(content=content)

                # Build the message to publish
                message = monitor.build_update_message(parsed_content=parsed_content)
                if message is None:
                    self._logger.info("No new version for repository " + repo_name)
                    continue
                self._logger.info("New version for repository " + repo_name)
                
                # Publish the changes into the Updates account
                self._publish_update(message=message)

                # Add a note about the project to publish them all together
                published_projects.append(
                    f"- {repo_name}: {monitor.prepare_versions(parsed_content=parsed_content)}"
                )

                # Save the current last known version
                monitor.store_last_known_version(list(parsed_content.keys())[0])

            if len(published_projects) > 0:
                self._publish_notification(
                    message=Message(
                        text="Published an update for:\n\n" + 
                            "\n".join(published_projects)
                    )
                )

        except Exception as e:
            self._logger.exception(e)

            self._publish_notification(
                message=Message(
                    text="Error while publishing updates:\n\n" + str(e))
            )
    
    def _publish_update(self, message: Message):
        # We want to publish to a different account,
        #   which only publishes updates.
        #   This means to instantiate a different Mastodon helper
        conn_params = MastodonConnectionParams.from_dict(
            self._config.get("git_monitor.mastodon")
        )
        # If the client_file does not exist we need to trigger the
        #   create app action.
        if not os.path.exists(conn_params.credentials.client_file):
            MastodonHelper.create_app(
                instance_type = conn_params.instance_type,
                client_name = self._config.get("git_monitor.mastodon.app_name"),
                api_base_url = conn_params.api_base_url,
                to_file = conn_params.credentials.client_file
            )
        # Now get the instance
        mastodon_instance = MastodonHelper.get_instance(
            config = self._config,
            connection_params = conn_params
        )
        # Now publish the message
        _ = Publisher(self._config, mastodon_instance).publish_one(
            QueueItem(message)
        )
    
    def _publish_notification(self, message: Message):
        # This is the notification that we publish to
        #   the usual account, just to say who the action went.
        
        # Get the instance. Everything is by default
        mastodon_instance = MastodonHelper.get_instance(self._config)
        # Now publish the message
        _ = Publisher(self._config, mastodon_instance).publish_one(
            QueueItem(message)
        )


if __name__ == '__main__':
    PublishGitChanges().init().run()

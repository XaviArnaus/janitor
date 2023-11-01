from pyxavi.config import Config
from janitor.objects.mastodon_connection_params import MastodonConnectionParams
from janitor.lib.publisher import Publisher
from janitor.objects.message import Message
from janitor.lib.git_monitor import GitMonitor
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import logging


class GitChanges(RunnerProtocol):
    '''
    Runner that goes through all monitored git repositories and detect changes,
    publishing them into the mastodon-like defined account
    '''

    def __init__(
        self, config: Config = None, logger: logging = None, params: dict = None
    ) -> None:
        self._config = config
        self._logger = logger

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
                monitor.initiate_or_clone_repository(repository_info=repository)

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
                self._logger.debug(
                    f"Publishing an update message into account {repository['named_account']}"
                )
                self._publish_update(message=message, named_account=repository["named_account"])

                # Add a note about the project to publish them all together
                published_projects.append(
                    f"- {repo_name}: {monitor.prepare_versions(parsed_content=parsed_content)}"
                )

                # Save the current last known version
                self._logger.debug(
                    f"Storing a new last known version: {list(parsed_content.keys())[0]}"
                )
                monitor.store_last_known_version(list(parsed_content.keys())[0])

            if len(published_projects) > 0:
                self._logger.debug("Publishing an notice into account default")
                self._publish_notification(
                    message=Message(
                        text="Published an update for:\n\n" + "\n".join(published_projects)
                    )
                )

        except Exception as e:
            self._logger.exception(e)

            self._publish_notification(
                message=Message(text="Error while publishing updates:\n\n" + str(e))
            )

    def _publish_update(self, message: Message, named_account: str = "updates"):
        # We want to publish to a different account,
        #   which only publishes updates.
        #   This means to instantiate a different Mastodon helper
        conn_params = MastodonConnectionParams.from_dict(
            self._config.get(f"mastodon.named_accounts.{named_account}")
        )
        # Now publish the message
        _ = Publisher(
            config=self._config, connection_params=conn_params, base_path=ROOT_DIR
        ).publish_message(message=message)

    def _publish_notification(self, message: Message, named_account: str = "default"):
        # This is the notification that we publish to
        #   the usual account, just to say who the action went.
        conn_params = MastodonConnectionParams.from_dict(
            self._config.get(f"mastodon.named_accounts.{named_account}")
        )
        # Now publish the message
        _ = Publisher(
            config=self._config, connection_params=conn_params, base_path=ROOT_DIR
        ).publish_message(message=message)

from pyxavi.config import Config
from janitor.lib.mastodon_helper import MastodonHelper
from janitor.objects.mastodon_connection_params import MastodonConnectionParams
from janitor.lib.publisher import Publisher
from janitor.objects.message import Message
from janitor.objects.queue_item import QueueItem
from janitor.lib.git_monitor import GitMonitor
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import os
import logging
from pyxavi.debugger import dd


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

                # Bring the new updates
                monitor.get_updates()

                # Delegate the work to a ChangesProtocol class
                #   It implements a custom approach for each monitoring style
                #   all packed in a same protocol.
                #
                #   If it fails skip this repo and go for the next
                try:
                    controller = monitor.get_changes_instance()
                except RuntimeError as e:
                    self._logger.warning(e)
                    self._publish_notification(message=Message(text=f"Warning: {e}"))
                    continue

                # So get the values to compare
                current_last_known = controller.get_current_last_known()
                new_last_known = controller.get_new_last_known()

                # If we don't have a previous value, it is the first run.
                #   Just save the new value but avoid messaging around.
                if current_last_known is None:
                    controller.write_new_last_known(value=new_last_known)
                    continue

                # Now let's chech if we have new changes
                if new_last_known is None or current_last_known == new_last_known:
                    # No we don't. Finish here
                    self._logger.info("No new changes for repository " + repo_name)
                    continue

                # Still here? So we have changes!
                self._logger.info("New changes for repository " + repo_name)
                # Build the message
                message = controller.build_update_message()

                # And publish it using the defined named_account.
                self._logger.debug(
                    f"Publishing an update message into account {repository['named_account']}"
                )
                self._publish_update(message=message, named_account=repository["named_account"])

                # Add a note about the project to publish them all together by the Service
                published_projects.append(f"- {repo_name}: {controller.get_changes_note()}")

                # And finally store this new last known
                self._logger.debug(
                    f"Storing a new last known change id: {new_last_known}"
                )
                controller.write_new_last_known(new_last_known)

            if len(published_projects) > 0:
                self._logger.debug("Publishing an notice into account default")
                self._publish_notification(
                    message=Message(
                        text="Published an update for:\n\n" + "\n".join(published_projects)
                    )
                )

        except Exception as e:
            self._logger.exception(e)

            # self._publish_notification(
            #     message=Message(text="Error while publishing updates:\n\n" + str(e))
            # )

    def _publish_update(self, message: Message, named_account: str = "updates"):
        # We want to publish to a different account,
        #   which only publishes updates.
        #   This means to instantiate a different Mastodon helper
        conn_params = MastodonConnectionParams.from_dict(
            self._config.get(f"mastodon.named_accounts.{named_account}")
        )
        client_file = os.path.join(ROOT_DIR, conn_params.credentials.client_file)
        # If the client_file does not exist we need to trigger the
        #   create app action.
        if not os.path.exists(client_file):
            MastodonHelper.create_app(
                instance_type=conn_params.instance_type,
                client_name=conn_params.app_name,
                api_base_url=conn_params.api_base_url,
                to_file=client_file
            )
        # Now get the instance
        mastodon_instance = MastodonHelper.get_instance(
            config=self._config, connection_params=conn_params
        )
        # Now publish the message
        _ = Publisher(
            config=self._config,
            mastodon=mastodon_instance,
            connection_params=conn_params,
            base_path=ROOT_DIR
        ).publish_one(QueueItem(message))

    def _publish_notification(self, message: Message, named_account: str = "default"):
        # This is the notification that we publish to
        #   the usual account, just to say who the action went.
        conn_params = MastodonConnectionParams.from_dict(
            self._config.get(f"mastodon.named_accounts.{named_account}")
        )

        # Get the instance. Everything is by default
        mastodon_instance = MastodonHelper.get_instance(
            config=self._config, connection_params=conn_params
        )
        # Now publish the message
        _ = Publisher(
            config=self._config,
            mastodon=mastodon_instance,
            connection_params=conn_params,
            base_path=ROOT_DIR
        ).publish_one(QueueItem(message))

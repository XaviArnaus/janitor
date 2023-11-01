from pyxavi.config import Config
from pyxavi.dictionary import Dictionary
from janitor.lib.publisher import Publisher
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

        self._service_publisher = Publisher(
            config=self._config, named_account="default", base_path=ROOT_DIR
        )

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
                repo = Dictionary(repository)

                # Check if we already have the repo cloned
                # If not, clone it localy
                monitor.initiate_or_clone_repository(repository_info=repo)

                # Bring the new updates
                monitor.get_updates()

                # So get the values to compare
                current_last_known = monitor.get_current_last_known()
                new_last_known = monitor.get_new_last_known()

                # If we don't have a previous value, it is the first run.
                #   Just save the new value but avoid messaging around.
                if current_last_known is None:
                    monitor.write_new_last_known(value=new_last_known)
                    continue

                # Now let's chech if we have new changes
                if new_last_known is None or current_last_known == new_last_known:
                    # No we don't. Finish here
                    self._logger.info(f"No new changes for repository {repo.get('name')}")
                    continue

                # Still here? So we have changes!
                self._logger.info(f"New changes for repository {repo.get('name')}")
                # Build the message
                message = monitor.get_update_message()

                # And publish it using the defined named_account.
                self._logger.debug(
                    f"Publishing an update message into account {repo.get('named_account')}"
                )

                Publisher(
                    config=self._config,
                    named_account=repo.get('named_account'),
                    base_path=ROOT_DIR
                ).info(content=message)

                # Add a note about the project to publish them all together by the Service
                published_projects.append(f"- {repo.get('name')}: {monitor.get_changes_note()}")

                # And finally store this new last known
                self._logger.debug(f"Storing a new last known change id: {new_last_known}")
                monitor.write_new_last_known(new_last_known)

            if len(published_projects) > 0:
                self._logger.debug("Publishing an notice into account default")
                self._service_publisher.info(
                    "Published an update for:\n\n" + "\n".join(published_projects)
                )

        except Exception as e:
            self._logger.exception(e)
            self._service_publisher.error("Error while publishing updates:\n\n" + str(e))

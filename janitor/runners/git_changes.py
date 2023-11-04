from pyxavi.terminal_color import TerminalColor
from pyxavi.config import Config
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
            self._logger.info(
                f"{TerminalColor.MAGENTA}Starting Git Changes Monitoring{TerminalColor.END}"
            )
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
                    self._logger.info(
                        f"{TerminalColor.BLUE}No new version for repository " +
                        f"{repo_name}{TerminalColor.END}"
                    )
                    continue
                self._logger.info(
                    f"{TerminalColor.BLUE}New version for repository " +
                    f"{repo_name}{TerminalColor.END}"
                )

                # Publish the changes into the Updates account
                self._logger.debug(
                    f"Publishing an update message into account {repository['named_account']}"
                )
                Publisher(
                    config=self._config,
                    named_account=repository["named_account"],
                    base_path=ROOT_DIR
                ).publish_message(message=message)

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
                self._service_publisher.info(
                    "Published an update for:\n\n" + "\n".join(published_projects)
                )

        except Exception as e:
            self._logger.exception(e)
            self._service_publisher.error("Error while publishing updates:\n\n" + str(e))

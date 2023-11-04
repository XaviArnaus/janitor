from pyxavi.terminal_color import TerminalColor
from pyxavi.config import Config
from janitor.lib.publisher import Publisher
from janitor.lib.directnic_ddns import DirectnicDdns
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import logging


class UpdateDdns(RunnerProtocol):
    '''
    Runner that gets the current external IP and updates
        Directnic's Dynamic DNS entries
    '''

    def __init__(
        self, config: Config = None, logger: logging = None, params: dict = None
    ) -> None:
        self._config = config
        self._logger = logger
        self._directnic = DirectnicDdns(config=self._config, base_path=ROOT_DIR)

        self._service_publisher = Publisher(
            config=self._config, named_account="default", base_path=ROOT_DIR
        )

    def run(self):
        '''
        Get the IP, update and communicate
        '''
        self._logger.info(
            f"{TerminalColor.MAGENTA}Starting Directnic DDNS Updater{TerminalColor.END}"
        )
        try:
            # Get the current external IP
            self._directnic.get_external_ip()

            # Compare with the one that we have stored
            # If they are different,
            if self._directnic.current_ip_is_different():

                self._logger.info("Current external IP is different from the previous known.")

                # For each entry in the config, send an update
                items_to_update = self._config.get("directnic_ddns.updates", [])
                for item in items_to_update:
                    link = self._directnic.build_updating_link(item)
                    result = self._directnic.send_update(updating_url=link)
                    if not result:
                        self._logger.error(
                            f"{TerminalColor.RED_BRIGHT}Failed call to " +
                            f"{link}{TerminalColor.END}"
                        )
                        self._service_publisher.error(
                            content=f"Failed to update the new external IP to {link}"
                        )
                    else:
                        self._logger.info(
                            f"{TerminalColor.GREEN}Update was successful" +
                            f"{TerminalColor.END} for {link}"
                        )

                # Store the new external IP locally
                self._logger.debug("Saving the currnet IP")
                self._directnic.save_current_ip()

                # Publish into Mastodon
                self._service_publisher.info(
                    content=f"New external IP updated to {len(items_to_update)} items."
                )
            else:
                self._logger.info(
                    f"{TerminalColor.CYAN}Current external IP is the same " +
                    f"as the previous known.{TerminalColor.END}"
                )

        except RuntimeError as e:
            self._logger.exception(e)
            try:
                self._logger.error(str(e))
            except Exception as e:
                self._logger.exception(e)
        except Exception as e:
            self._logger.exception(e)

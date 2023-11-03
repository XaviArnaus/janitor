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
        try:
            # Get the current external IP
            self._directnic.get_external_ip()

            # Compare with the one that we have stored
            # If they are different,
            if self._directnic.current_ip_is_different():

                # For each entry in the config, send an update
                items_to_update = self._config.get("directnic_ddns.updates", [])
                for item in items_to_update:
                    link = self._directnic.build_updating_link(item)
                    result = self._directnic.send_update(updating_url=link)
                    if not result:
                        self._logger.error(f"Failed call to {link}")
                        self._service_publisher.error(
                            content=f"Failed to update the new external IP to {link}"
                        )

                # Store the new external IP locally
                self._directnic.save_current_ip()

                # Publish into Mastodon
                self._service_publisher.info(
                    content=f"New external IP updated to {len(items_to_update)} items."
                )

        except RuntimeError as e:
            self._logger.exception(e)
            try:
                self._logger.error(str(e))
            except Exception as e:
                self._logger.exception(e)
        except Exception as e:
            self._logger.exception(e)

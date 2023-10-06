from pyxavi.logger import Logger
from pyxavi.config import Config
from janitor.lib.mastodon_helper import MastodonHelper
from janitor.lib.publisher import Publisher
from janitor.objects.message import Message
from janitor.objects.queue_item import QueueItem
from janitor.lib.directnic_ddns import DirectnicDdns


class UpdateDdns:
    '''
    Runner that gets the current external IP and updates
        Directnic's Dynamic DNS entries
    '''

    def init(self):
        self._config = Config()
        self._logger = Logger(self._config).get_logger()
        self._directnic = DirectnicDdns(self._config)

        return self
    
    def _send_mastodon_message(self, text: str) -> None:
        self._logger.info("Initializing Mastodon tooling")
        mastodon = MastodonHelper.get_instance(self._config)
        publisher = Publisher(self._config, mastodon)
        queue_item = QueueItem(message=Message(text=text))
        self._logger.info("Publishing Mastodon message")
        _ = publisher.publish_one(queue_item)

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
                        self._send_mastodon_message(
                            f"Failed to update the new external IP to {link}"
                        )

                # Store the new external IP locally
                self._directnic.save_current_ip()

                # Publish into Mastodon
                self._send_mastodon_message(
                    f"New external IP updated to {len(items_to_update)} items."
                )

        except RuntimeError as e:
            self._logger.exception(e)
            try:
                self._send_mastodon_message(str(e))
            except Exception as e:
                self._logger.exception(e)
        except Exception as e:
            self._logger.exception(e)

if __name__ == '__main__':
    UpdateDdns().init().run()

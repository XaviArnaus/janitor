from pyxavi.config import Config
from pyxavi.storage import Storage
from pyxavi.network import Network
import logging
import requests

DEFAULT_FILENAME = "storage/external_ip.yaml"

class DirectnicDdns:

    current_external_ip: str = None

    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
        self._storage = Storage(self._config.get("directnic_ddns.file", DEFAULT_FILENAME))
    
    def get_external_ip(self) -> str:
        if self.current_external_ip is None:
            self._logger.debug("Getting external IP from service")
            # The class raises RuntimeError if could not succeed
            self.current_external_ip = Network.get_external_ipv4(self._logger)
            self._logger.info(f"External IP is {self.current_external_ip}")

        return self.current_external_ip
    
    def current_ip_is_different(self) -> bool:
        last_external_ip = self._storage.get("last_external_ip")
        self._logger.debug(f"Last external IP was {last_external_ip}")

        if last_external_ip != self.get_external_ip():
            self._logger.info(f"Current external IP is different from the previous known.")
            return True
        
        self._logger.info(f"Current external IP is the same as the previous known.")
        return False
    
    def build_updating_link(self, partial_url: str) -> str:
        updating_url = f"{partial_url}{self.get_external_ip()}"
        self._logger.debug(f"Updating URL is {updating_url}")
        return updating_url
    
    def send_update(self, updating_url: str) -> bool:
        self._logger.info("Sending update call")
        response = requests.get(url=updating_url)

        if response.status_code == 200:
            self._logger.info("Update succeeded")
            return True
        else:
            self._logger.info("Update failed")
            return False
    
    def save_current_ip(self) -> None:
        self._storage.set("last_external_ip", self.get_external_ip())
        self._storage.write_file()

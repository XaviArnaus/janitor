from pyxavi.config import Config
from pyxavi.network import Network
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import logging


class WhatIsMyIp(RunnerProtocol):
    '''
    Runner that gets the current external IP and updates
        Directnic's Dynamic DNS entries
    '''

    def __init__(self, config: Config = None, logger: logging = None) -> None:
        self._config = config
        self._logger = logger


    def run(self):
        '''
        Get the IP, update and communicate
        '''
        try:
            self._logger.debug("Getting external IP from service")
            # The class raises RuntimeError if could not succeed
            current_external_ip = Network.get_external_ipv4(self._logger)
            print(current_external_ip)

        except Exception as e:
            self._logger.exception(e)

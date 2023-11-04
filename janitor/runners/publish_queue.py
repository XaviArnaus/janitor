from pyxavi.terminal_color import TerminalColor
from pyxavi.config import Config
from janitor.lib.publisher import Publisher
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import logging


class PublishQueue(RunnerProtocol):
    '''
    Runner that publishes the queue
    '''

    def __init__(
        self, config: Config = None, logger: logging = None, params: dict = None
    ) -> None:
        self._config = config
        self._logger = logger

    def run(self):
        '''
        Just publishes the queue
        '''
        try:
            # Read from the queue the toots to publish and publishes all of them
            #   This runner WILL ALWAYS run in ONLY OLDEST mode, as it is meant to
            #   be added as a scheduler task to run every n minutes (10?)
            publisher = Publisher(
                config=self._config,
                named_account="default",
                base_path=ROOT_DIR,
                only_oldest=True
            )
            self._logger.info(
                f"{TerminalColor.MAGENTA}Starting Publish Queue{TerminalColor.END}"
            )
            publisher.publish_all_from_queue()
        except Exception as e:
            self._logger.exception(e)

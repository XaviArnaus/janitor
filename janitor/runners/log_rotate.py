from pyxavi.terminal_color import TerminalColor
from pyxavi.config import Config
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import logging
from datetime import datetime
import os
import shutil

ROTATED_DATETIME = "%Y%m%d_%H%I%S"


class LogRotate(RunnerProtocol):
    '''
    Runner that rotates the log file
    '''

    def __init__(
        self, config: Config = None, logger: logging = None, params: dict = None
    ) -> None:
        self._config = config
        self._logger = logger

    def run(self):
        '''
        Reads the current log filename and moves it to a rotated one.
        '''
        self._logger.info(f"{TerminalColor.MAGENTA}Starting Log Rotate{TerminalColor.END}")
        # So the strategy is the following:
        #   1. Copy the current log file to f"{current_log_file.log}.old-{datetime}"
        #   2. Remove the current log file f"{current_log_file.log}"
        #   2. The logging system will create automatically the new f"{current_log_file.log}"

        current_log_file = self._config.get("logger.filename")
        if current_log_file is None:
            raise RuntimeError(
                "Could not get the current log filename. Do you have it in the config file?"
            )
        now = datetime.now().strftime(ROTATED_DATETIME)
        new_log_file_name = f"{current_log_file}.old-{now}"
        self._logger.debug(f"Will rotate the log {current_log_file} to {new_log_file_name}")
        shutil.copyfile(
            os.path.join(ROOT_DIR, current_log_file),
            os.path.join(ROOT_DIR, new_log_file_name),
        )
        os.remove(current_log_file)
        self._logger.info(
            f"{TerminalColor.CYAN}Log rotate {current_log_file} " +
            f"to {new_log_file_name}{TerminalColor.END}"
        )

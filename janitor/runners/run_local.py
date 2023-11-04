from pyxavi.config import Config
from pyxavi.terminal_color import TerminalColor
from janitor.lib.system_info import SystemInfo
from janitor.lib.system_info_templater import SystemInfoTemplater
from janitor.lib.publisher import Publisher
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
import logging


class RunLocal(RunnerProtocol):
    '''
    Main runner of the app
    '''

    def __init__(
        self, config: Config = None, logger: logging = None, params: dict = None
    ) -> None:
        self._config = config
        self._logger = logger
        self._sys_info = SystemInfo(self._config)

    def run(self):
        self._logger.info(
            f"{TerminalColor.MAGENTA}Starting Local System Info{TerminalColor.END}"
        )

        # Get the data
        sys_data = self._collect_data()

        # If there is no issue, just stop here.
        if not self._sys_info.crossed_thresholds(sys_data, ["hostname"]):
            self._logger.info(
                f"{TerminalColor.CYAN}No issues found. Ending here.{TerminalColor.END}"
            )
            return False

        # Make it a message
        message = SystemInfoTemplater(self._config).process_report(sys_data)

        # Publish the queue
        Publisher(
            config=self._config, named_account="default", base_path=ROOT_DIR
        ).publish_message(message=message)

    def _collect_data(self) -> dict:
        return {
            **{
                "hostname": self._sys_info.get_hostname()
            },
            **self._sys_info.get_cpu_data(),
            **self._sys_info.get_mem_data(),
            **self._sys_info.get_disk_data()
        }

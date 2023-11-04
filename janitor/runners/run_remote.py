from pyxavi.terminal_color import TerminalColor
from pyxavi.config import Config
from janitor.lib.system_info import SystemInfo
from janitor.runners.runner_protocol import RunnerProtocol
import requests
import logging


class RunRemote(RunnerProtocol):
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
            f"{TerminalColor.MAGENTA}Starting Remote System Info{TerminalColor.END}"
        )

        # Get the data
        sys_data = self._collect_data()

        # Send the data
        if not self._config.get("app.run_control.dry_run"):
            remote_url = self._config.get("app.service.remote_url")
            self._logger.debug("Sending sys_data away")
            r = requests.post(f"{remote_url}/sysinfo", json={'sys_data': sys_data})
            if r.status_code == 200:
                self._logger.info(
                    f"{TerminalColor.CYAN}Request was successful{TerminalColor.END}"
                )
            else:
                self._logger.warning(
                    f"{TerminalColor.RED_BRIGHT}Request was unsuccessful:" +
                    f" {r.status_code}{TerminalColor.END}"
                )
        else:
            self._logger.info(f"{TerminalColor.CYAN}Dry Run, not sent.{TerminalColor.END}")

    def _collect_data(self) -> dict:
        return {
            **{
                "hostname": self._sys_info.get_hostname()
            },
            **self._sys_info.get_cpu_data(),
            **self._sys_info.get_mem_data(),
            **self._sys_info.get_disk_data(),
        }

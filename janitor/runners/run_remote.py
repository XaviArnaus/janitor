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
        self._logger.info("Init Remote Runner")

    def run(self):
        self._logger.info("Run remote app")

        # Get the data
        sys_data = self._collect_data()

        # Send the data
        if not self._config.get("app.run_control.dry_run"):
            remote_url = self._config.get("app.service.remote_url")
            self._logger.info("Sending sys_data away")
            r = requests.post(f"{remote_url}/sysinfo", json={'sys_data': sys_data})
            if r.status_code == 200:
                self._logger.info("Request was successful")
            else:
                self._logger.warning(f"Request was unsuccessful: {r.status_code}")
        else:
            self._logger.info("Dry Run, not sent.")

        self._logger.info("End.")

    def _collect_data(self) -> dict:
        return {
            **{
                "hostname": self._sys_info.get_hostname()
            },
            **self._sys_info.get_cpu_data(),
            **self._sys_info.get_mem_data(),
            **self._sys_info.get_disk_data(),
        }

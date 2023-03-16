from pyxavi.config import Config
from pyxavi.logger import Logger
from src.lib.system_info import SystemInfo
from src.lib.queue import Queue
import requests

class RunRemote:
    '''
    Main runner of the app
    '''
    def init(self):
        self._config = Config()
        self._logger = Logger(self._config).getLogger()
        self._sys_info = SystemInfo(self._config)
        self._queue = Queue(self._config)
        self._logger.info("Init Runner")

        return self

    def run(self):
        self._logger.info("Run app")

        # Get the data
        sys_data = self._collect_data()

        # Send the data
        remote_url = self._config.get("app.remote_service_url")
        self._logger.info("Sending sys_data away")
        r = requests.post(f"{remote_url}/sysinfo", data={'sys_data': sys_data})
        if r.status_code == 200:
            self._logger.info("Request was successful")
        else:
            self._logger.warning(f"Request was unsuccessful: {r.status_code}")

        self._logger.info("End.")

    def _collect_data(self) -> dict:
        return {
            **self._sys_info.get_cpu_data(),
            **self._sys_info.get_mem_data(),
            **self._sys_info.get_disk_data(),
            **self._sys_info.get_temp_data(),
        }

if __name__ == '__main__':
    RunRemote().init().run()


from pyxavi.config import Config
from pyxavi.logger import Logger
from src.lib.system_info import SystemInfo
from pyxavi.debugger import dd

class Runner:
    '''
    Main runner of the app
    '''
    def init(self):
        self._config = Config()
        self._logger = Logger(self._config).getLogger()
        self._logger.info("Init Runner")

        return self

    def run(self):
        self._logger.info("Run app")
        sys_data = self._collect_data()
        dd(sys_data)
        self._logger.info("End.")

    def _collect_data(self) -> dict:
        sys_info = SystemInfo(self._config)
        return {
            **sys_info.get_cpu_data(),
            **sys_info.get_mem_data(),
            **sys_info.get_disk_data(),
            **sys_info.get_temp_data(),
        }

if __name__ == '__main__':
    Runner().init().run()


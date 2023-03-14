from pyxavi.config import Config
from pyxavi.logger import Logger
from src.lib.system_info import SystemInfo
from src.lib.system_info_templater import SystemInfoTemplater
from src.lib.queue import Queue
from src.objects.queue_item import QueueItem
from pyxavi.debugger import dd

class RunApp:
    '''
    Main runner of the app
    '''
    def init(self):
        self._config = Config()
        self._logger = Logger(self._config).getLogger()
        self._queue = Queue(self._config)
        self._logger.info("Init Runner")

        return self

    def run(self):
        self._logger.info("Run app")
        # Get the data
        sys_data = self._collect_data()
        # Make it a message
        message = SystemInfoTemplater(self._config).process_report(sys_data)
        print(message.summary)
        print(message.text)
        # Add it into the queue and save
        self._logger.debug("Adding message into the queue")
        self._queue.append(QueueItem(message))
        self._queue.save()
        # Publish the queue


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
    RunApp().init().run()


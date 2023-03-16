from pyxavi.config import Config
from pyxavi.logger import Logger
from src.lib.system_info import SystemInfo
from src.lib.system_info_templater import SystemInfoTemplater
from src.lib.publisher import Publisher
from src.lib.mastodon_helper import MastodonHelper
from src.objects.queue_item import QueueItem

class RunLocal:
    '''
    Main runner of the app
    '''
    def init(self):
        self._config = Config()
        self._logger = Logger(self._config).getLogger()
        self._sys_info = SystemInfo(self._config)
        self._logger.info("Init Local Runner")

        return self

    def run(self):
        self._logger.info("Run local app")

        # Get the data
        sys_data = self._collect_data()

        # If there is no issue, just stop here.
        if not self._sys_info.crossed_thressholds(sys_data, ["hostname"]):
            self._logger.info("No issues found. Ending here.")
            return False

        # Make it a message
        message = SystemInfoTemplater(self._config).process_report(sys_data)

        # Publish the queue
        mastodon = MastodonHelper.get_instance(self._config)
        publisher = Publisher(self._config, mastodon)
        self._logger.info("Publishing the whole queue")
        publisher.publish_one(QueueItem(message))

        self._logger.info("End.")

    def _collect_data(self) -> dict:
        return {
            **{
                "hostname": self._sys_info.get_hostname()
            },
            **self._sys_info.get_cpu_data(),
            **self._sys_info.get_mem_data(),
            **self._sys_info.get_disk_data(),
            **self._sys_info.get_temp_data(),
        }

if __name__ == '__main__':
    RunLocal().init().run()


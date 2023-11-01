from pyxavi.config import Config
from janitor.lib.system_info import SystemInfo
from janitor.lib.system_info_templater import SystemInfoTemplater
from janitor.lib.publisher import Publisher
from janitor.objects.mastodon_connection_params import MastodonConnectionParams
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
        self._logger.info("Init Local Runner")

    def run(self):
        self._logger.info("Run local app")

        # Get the data
        sys_data = self._collect_data()

        # If there is no issue, just stop here.
        if not self._sys_info.crossed_thresholds(sys_data, ["hostname"]):
            self._logger.info("No issues found. Ending here.")
            return False

        # Make it a message
        message = SystemInfoTemplater(self._config).process_report(sys_data)

        # Publish the queue
        conn_params = MastodonConnectionParams.from_dict(
            self._config.get("mastodon.named_accounts.default")
        )
        Publisher(
            config=self._config, connection_params=conn_params, base_path=ROOT_DIR
        ).publish_message(message=message)

        self._logger.info("End.")

    def _collect_data(self) -> dict:
        return {
            **{
                "hostname": self._sys_info.get_hostname()
            },
            **self._sys_info.get_cpu_data(),
            **self._sys_info.get_mem_data(),
            **self._sys_info.get_disk_data()
        }

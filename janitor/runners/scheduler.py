from pyxavi.config import Config
from croniter import croniter
from datetime import datetime
from janitor.runners.runner_protocol import RunnerProtocol
import logging

from janitor.runners.run_local import RunLocal
from janitor.runners.run_remote import RunRemote
from janitor.runners.update_ddns import UpdateDdns
from janitor.runners.git_changes import GitChanges
from janitor.runners.log_rotate import LogRotate


class Scheduler(RunnerProtocol):
    '''
    Runner for scheduled actions
    '''

    def __init__(
        self, config: Config = None, logger: logging = None, params: dict = None
    ) -> None:
        self._config = config
        self._logger = logger

    def run(self):
        '''
        Read and react to schedules
        '''
        try:
            schedules = list(self._config.get("schedules"))
            now_dt = datetime.now()

            for schedule in schedules:
                if croniter.match(schedule["when"], now_dt):
                    self._logger.debug("Running schedule " + schedule["name"])
                    self._execute_action(schedule["action"])

        except Exception as e:
            self._logger.exception(e)

    def _execute_action(self, action: str):
        if action == "sysinfo_local":
            RunLocal(config=self._config, logger=self._logger).run()
        elif action == "sysinfo_remote":
            RunRemote(config=self._config, logger=self._logger).run()
        elif action == "update_ddns":
            UpdateDdns(config=self._config, logger=self._logger).run()
        elif action == "git_changes":
            GitChanges(config=self._config, logger=self._logger).run()
        elif action == "rotate_log":
            LogRotate(config=self._config, logger=self._logger).run()
        elif action == "publish_queue":
            LogRotate(config=self._config, logger=self._logger).run()

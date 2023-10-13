from pyxavi.config import Config
from croniter import croniter
from datetime import datetime
from janitor.runners.runner_protocol import RunnerProtocol
import logging

from janitor.runners.run_local import RunLocal
from janitor.runners.run_remote import RunRemote
from janitor.runners.update_ddns import UpdateDdns
from janitor.runners.publish_git_changes import PublishGitChanges


class Scheduler(RunnerProtocol):
    '''
    Runner for scheduled actions
    '''

    def __init__(self, config: Config = None, logger: logging = None) -> None:
        self._config = config
        self._logger = logger

    def run(self):
        '''
        Read and react to schedules
        '''
        try:
            schedules = list(self._config.get("app.schedules"))
            now_dt = datetime.now()

            for schedule in schedules:
                if croniter.match(schedule["when"], now_dt):
                    self._logger.info("Running schedule " + schedule["name"])
                    self._execute_action(schedule["action"])

        except Exception as e:
            self._logger.exception(e)

    def _execute_action(self, action: str):
        if action == "sysinfo_local":
            RunLocal().run()
        elif action == "sysinfo_remote":
            RunRemote().run()
        elif action == "update_ddns":
            UpdateDdns().run()
        elif action == "publish_git_changes":
            PublishGitChanges().run()


if __name__ == '__main__':
    Scheduler().run()
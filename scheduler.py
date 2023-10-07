from pyxavi.logger import Logger
from pyxavi.config import Config
from croniter import croniter
from datetime import datetime

from run_local import RunLocal
from run_remote import RunRemote
from update_ddns import UpdateDdns
from publish_git_changes import PublishGitChanges


class Scheduler:
    '''
    Runner for scheduled actions
    '''

    def __init__(self):
        self._config = Config()
        self._logger = Logger(self._config).get_logger()

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
            RunLocal().init().run()
        elif action == "sysinfo_remote":
            RunRemote().init().run()
        elif action == "update_ddns":
            UpdateDdns().init().run()
        elif action == "publish_git_changes":
            PublishGitChanges().init().run()


if __name__ == '__main__':
    Scheduler().run()

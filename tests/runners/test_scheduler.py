from pyxavi.config import Config
from pyxavi.logger import Logger
from scheduler import Scheduler
from unittest.mock import patch, Mock
from croniter import croniter
from freezegun import freeze_time
from datetime import datetime
from logging import Logger as PythonLogger

SCHEDULES = [
    {
        "name": "Heartbeat",
        "when": "* * * * *",
        "action": "sysinfo_local"
    }
]


def patched_generic_init(self):
    pass


def patched_generic_init_with_config(self, config):
    pass


@patch.object(Config, "__init__", new=patched_generic_init)
@patch.object(Logger, "__init__", new=patched_generic_init_with_config)
def get_instance() -> Scheduler:
    mocked_official_logger = Mock()
    mocked_official_logger.__class__ = PythonLogger
    mocked_logger_getLogger = Mock()
    mocked_logger_getLogger.return_value = mocked_official_logger
    with patch.object(Logger, "getLogger", new=mocked_logger_getLogger):
        return Scheduler()


def test_init():
    runner = get_instance()

    assert isinstance(runner, Scheduler)
    assert isinstance(runner._config, Config)
    assert isinstance(runner._logger, PythonLogger)


@freeze_time("2023-03-26 13:00")
def test_run_time_does_not_match():
    now = datetime(2023, 3, 26, 13, 00)
    runner = get_instance()

    mocked_config_get = Mock()
    mocked_config_get.return_value = SCHEDULES
    mocked_croniter_match = Mock()
    mocked_croniter_match.return_value = False
    mocked_action_execution = Mock()
    with patch.object(Config, "get", new=mocked_config_get):
        with patch.object(croniter, "match", new=mocked_croniter_match):
            with patch.object(runner, "_execute_action", new=mocked_action_execution):
                runner.run()

    print(mocked_croniter_match.call_args_list)
    mocked_croniter_match.assert_called_once_with(
        SCHEDULES[0]["when"],
        now
    )
    mocked_action_execution.assert_not_called()


@freeze_time("2023-03-26 13:00")
def test_run_time_does_match():
    now = datetime(2023, 3, 26, 13, 00)
    runner = get_instance()

    mocked_config_get = Mock()
    mocked_config_get.return_value = SCHEDULES
    mocked_croniter_match = Mock()
    mocked_croniter_match.return_value = True
    mocked_action_execution = Mock()
    with patch.object(Config, "get", new=mocked_config_get):
        with patch.object(croniter, "match", new=mocked_croniter_match):
            with patch.object(runner, "_execute_action", new=mocked_action_execution):
                runner.run()

    print(mocked_croniter_match.call_args_list)
    mocked_croniter_match.assert_called_once_with(
        SCHEDULES[0]["when"],
        now
    )
    mocked_action_execution.assert_called_once_with(SCHEDULES[0]["action"])

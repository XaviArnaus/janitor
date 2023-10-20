from pyxavi.config import Config
from pyxavi.logger import Logger
from janitor.lib.system_info import SystemInfo
from janitor.lib.system_info_templater import SystemInfoTemplater
from janitor.lib.publisher import Publisher
from janitor.lib.mastodon_helper import MastodonHelper
from janitor.objects.message import Message
from janitor.objects.queue_item import QueueItem
from janitor.runners.run_local import RunLocal
from unittest.mock import patch, Mock
import pytest
from logging import Logger as PythonLogger

COLLECTED_DATA = {
    "hostname": "endor",
    "cpu": {
        "cpu_percent": 50,
        "cpu_count": 2,
    },
    "memory": {
        "memory_total": 8000,
        "memory_avail": 4000,
        "memory_used": 3000,
        "memory_free": 2000,
        "memory_percent": 40,
    },
    "disk": {
        "disk_usage_total": 8000,
        "disk_usage_used": 4000,
        "disk_usage_free": 2000,
        "disk_usage_percent": 20
    }
}

CONFIG_MASTODON_CONN_PARAMS = {
    "app_type": "SuperApp",
    "instance_type": "mastodon",
    "api_base_url": "https://mastodont.cat",
    "credentials": {
        "user_file": "user.secret",
        "client_file": "client.secret",
        "user": {
            "email": "bot+syscheck@my-fancy.site",
            "password": "SuperSecureP4ss",
        }
    }
}


def patched_get_hostname(self):
    return COLLECTED_DATA["hostname"]


def patched_get_cpu_data(self):
    return COLLECTED_DATA["cpu"]


def patched_get_mem_data(self):
    return COLLECTED_DATA["memory"]


def patched_get_disk_data(self):
    return COLLECTED_DATA["disk"]


@pytest.fixture
def collected_data():
    return {
        **{
            "hostname": COLLECTED_DATA["hostname"]
        },
        **COLLECTED_DATA["cpu"],
        **COLLECTED_DATA["memory"],
        **COLLECTED_DATA["disk"]
    }


def patched_generic_init(self):
    pass


def patched_config_get(self, param):
    if param == "mastodon.named_accounts.default":
        return CONFIG_MASTODON_CONN_PARAMS


def patched_generic_init_with_config(self, config):
    pass


def patched_mastodon_get_instance(config, connection_params, base_path):
    pass


def patched_publisher_init(self, config, mastodon, connection_params, base_path):
    pass


@patch.object(Config, "__init__", new=patched_generic_init)
@patch.object(Logger, "__init__", new=patched_generic_init_with_config)
@patch.object(SystemInfo, "__init__", new=patched_generic_init_with_config)
def get_instance() -> RunLocal:
    mocked_official_logger = Mock()
    mocked_official_logger.__class__ = PythonLogger
    mocked_logger_get_logger = Mock()
    mocked_logger_get_logger.return_value = mocked_official_logger
    with patch.object(Logger, "get_logger", new=mocked_logger_get_logger):
        return RunLocal(config=Config(), logger=mocked_official_logger)


def test_init():
    runner = get_instance()

    assert isinstance(runner, RunLocal)
    assert isinstance(runner._config, Config)
    assert isinstance(runner._logger, PythonLogger)
    assert isinstance(runner._sys_info, SystemInfo)


@patch.object(SystemInfo, "get_hostname", new=patched_get_hostname)
@patch.object(SystemInfo, "get_cpu_data", new=patched_get_cpu_data)
@patch.object(SystemInfo, "get_mem_data", new=patched_get_mem_data)
@patch.object(SystemInfo, "get_disk_data", new=patched_get_disk_data)
def test_run_no_crossed_thresholds():
    runner = get_instance()

    mocked_crossed_thresholds = Mock()
    mocked_crossed_thresholds.return_value = False
    with patch.object(SystemInfo, "crossed_thresholds", new=mocked_crossed_thresholds):
        result = runner.run()

    assert result is False


@patch.object(SystemInfo, "get_hostname", new=patched_get_hostname)
@patch.object(SystemInfo, "get_cpu_data", new=patched_get_cpu_data)
@patch.object(SystemInfo, "get_mem_data", new=patched_get_mem_data)
@patch.object(SystemInfo, "get_disk_data", new=patched_get_disk_data)
@patch.object(SystemInfoTemplater, "__init__", new=patched_generic_init_with_config)
@patch.object(MastodonHelper, "get_instance", new=patched_mastodon_get_instance)
@patch.object(Publisher, "__init__", new=patched_publisher_init)
@patch.object(Config, "get", new=patched_config_get)
def test_run_crossed_thresholds(collected_data):
    message = Message(text="content of the report")

    runner = get_instance()

    mocked_crossed_thresholds = Mock()
    mocked_crossed_thresholds.return_value = True
    mocked_templater_process_report = Mock()
    mocked_templater_process_report.return_value = message
    mocked_publisher_publish_one = Mock()
    mocked_queue_item_init = Mock()
    mocked_queue_item_init.__class__ = QueueItem
    mocked_queue_item_init.return_value = None
    with patch.object(SystemInfo, "crossed_thresholds", new=mocked_crossed_thresholds):
        with patch.object(SystemInfoTemplater,
                          "process_report",
                          new=mocked_templater_process_report):
            with patch.object(QueueItem, "__init__", new=mocked_queue_item_init):
                with patch.object(Publisher, "publish_one", new=mocked_publisher_publish_one):
                    runner.run()

    mocked_templater_process_report.assert_called_once_with(collected_data)
    mocked_queue_item_init.assert_called_once_with(message)
    # For any reason I can't ensure that publish_one() is called with the mocked queue item!
    mocked_publisher_publish_one.assert_called_once()

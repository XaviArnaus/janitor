from pyxavi.config import Config
from pyxavi.logger import Logger
from src.lib.system_info import SystemInfo
from src.lib.system_info_templater import SystemInfoTemplater
from src.lib.publisher import Publisher
from src.lib.mastodon_helper import MastodonHelper
from src.objects.message import Message
from src.objects.queue_item import QueueItem
from run_local import RunLocal
from unittest.mock import patch, Mock, call
from unittest import TestCase
import pytest
from mastodon import Mastodon
from logging import Logger as PythonLogger
import os



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


def patched_templater_init(self, config):
    pass


def patched_mastodon_get_instance(config):
    pass


def patched_publisher_init(self, config, mastodon):
    pass


def get_instance() -> RunLocal:
    mocked_config_init = Mock()
    mocked_config_init.__class__ = Config
    mocked_config_init.return_value = None
    mocked_logger_init = Mock()
    mocked_logger_init.return_value = None
    mocked_official_logger = Mock()
    mocked_official_logger.__class__ = PythonLogger
    mocked_logger_getLogger = Mock()
    mocked_logger_getLogger.return_value = mocked_official_logger
    mocked_system_info_init = Mock()
    mocked_system_info_init.__class__ = SystemInfo
    mocked_system_info_init.return_value = None
    with patch.object(Config, "__init__", new=mocked_config_init):
        with patch.object(Logger, "__init__", new=mocked_logger_init):
            with patch.object(Logger, "getLogger", new=mocked_logger_getLogger):
                with patch.object(SystemInfo, "__init__", new=mocked_system_info_init):
                    return RunLocal()


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
    
    assert result == False


@patch.object(SystemInfo, "get_hostname", new=patched_get_hostname)
@patch.object(SystemInfo, "get_cpu_data", new=patched_get_cpu_data)
@patch.object(SystemInfo, "get_mem_data", new=patched_get_mem_data)
@patch.object(SystemInfo, "get_disk_data", new=patched_get_disk_data)
@patch.object(SystemInfoTemplater, "__init__", new=patched_templater_init)
@patch.object(MastodonHelper, "get_instance", new=patched_mastodon_get_instance)
@patch.object(Publisher, "__init__", new=patched_publisher_init)
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
        with patch.object(SystemInfoTemplater, "process_report", new=mocked_templater_process_report):
            with patch.object(QueueItem, "__init__", new=mocked_queue_item_init):
                with patch.object(Publisher, "publish_one", new=mocked_publisher_publish_one):
                    result = runner.run()
    
    mocked_templater_process_report.assert_called_once_with(collected_data)
    mocked_queue_item_init.assert_called_once_with(message)
    # For any reason I can't ensure that publish_one() is called with the mocked queue item!
    mocked_publisher_publish_one.assert_called_once()
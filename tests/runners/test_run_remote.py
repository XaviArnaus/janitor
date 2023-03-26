from pyxavi.config import Config
from pyxavi.logger import Logger
from src.lib.system_info import SystemInfo
from run_remote import RunRemote
from unittest.mock import patch, Mock, call
import requests
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


def patched_get_hostname(self):
    return COLLECTED_DATA["hostname"]


def patched_get_cpu_data(self):
    return COLLECTED_DATA["cpu"]


def patched_get_mem_data(self):
    return COLLECTED_DATA["memory"]


def patched_get_disk_data(self):
    return COLLECTED_DATA["disk"]


def patched_generic_init(self):
    pass


def patched_generic_init_with_config(self, config):
    pass


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


@patch.object(Config, "__init__", new=patched_generic_init)
@patch.object(Logger, "__init__", new=patched_generic_init_with_config)
@patch.object(SystemInfo, "__init__", new=patched_generic_init_with_config)
def get_instance() -> RunRemote:
    mocked_official_logger = Mock()
    mocked_official_logger.__class__ = PythonLogger
    mocked_logger_getLogger = Mock()
    mocked_logger_getLogger.return_value = mocked_official_logger
    with patch.object(Logger, "getLogger", new=mocked_logger_getLogger):
        return RunRemote()


def test_init():
    runner = get_instance()

    assert isinstance(runner, RunRemote)
    assert isinstance(runner._config, Config)
    assert isinstance(runner._logger, PythonLogger)
    assert isinstance(runner._sys_info, SystemInfo)


@patch.object(SystemInfo, "get_hostname", new=patched_get_hostname)
@patch.object(SystemInfo, "get_cpu_data", new=patched_get_cpu_data)
@patch.object(SystemInfo, "get_mem_data", new=patched_get_mem_data)
@patch.object(SystemInfo, "get_disk_data", new=patched_get_disk_data)
def test_run_dry_run():
    runner = get_instance()

    mocked_config_dry_run = Mock()
    mocked_config_dry_run.return_value = True
    with patch.object(Config, "get", new=mocked_config_dry_run):
        runner.run()

    mocked_config_dry_run.assert_called_once_with("run_control.dry_run")


@patch.object(SystemInfo, "get_hostname", new=patched_get_hostname)
@patch.object(SystemInfo, "get_cpu_data", new=patched_get_cpu_data)
@patch.object(SystemInfo, "get_mem_data", new=patched_get_mem_data)
@patch.object(SystemInfo, "get_disk_data", new=patched_get_disk_data)
def test_run_success(collected_data):
    class ObjectFaker:
        def __init__(self, d: dict):
            for key, value in d.items():
                setattr(self, key, value)

    remote_url = "http://remote.url"

    runner = get_instance()

    mocked_config_get = Mock()
    mocked_config_get.side_effect = [
        False,
        remote_url
    ]
    mocked_requests_post = Mock()
    mocked_requests_post.return_value = ObjectFaker({
        "status_code": 200
    })
    mocked_logger_info = Mock()
    with patch.object(Config, "get", new=mocked_config_get):
        with patch.object(requests, "post", new=mocked_requests_post):
            with patch.object(runner._logger, "info", new=mocked_logger_info):
                runner.run()

    mocked_config_get.assert_has_calls([
        call("run_control.dry_run"),
        call("app.service.remote_url")
    ])
    mocked_requests_post.assert_called_once_with(
        f"{remote_url}/sysinfo", json={'sys_data': collected_data}
    )
    mocked_logger_info.assert_has_calls([
        call('Run remote app'),
        call('Sending sys_data away'),
        call('Request was successful'),
        call('End.')
    ])


@patch.object(SystemInfo, "get_hostname", new=patched_get_hostname)
@patch.object(SystemInfo, "get_cpu_data", new=patched_get_cpu_data)
@patch.object(SystemInfo, "get_mem_data", new=patched_get_mem_data)
@patch.object(SystemInfo, "get_disk_data", new=patched_get_disk_data)
def test_run_fail(collected_data):
    class ObjectFaker:
        def __init__(self, d: dict):
            for key, value in d.items():
                setattr(self, key, value)

    remote_url = "http://remote.url"

    runner = get_instance()

    mocked_config_get = Mock()
    mocked_config_get.side_effect = [
        False,
        remote_url
    ]
    mocked_requests_post = Mock()
    mocked_requests_post.return_value = ObjectFaker({
        "status_code": 400
    })
    mocked_logger_warning = Mock()
    with patch.object(Config, "get", new=mocked_config_get):
        with patch.object(requests, "post", new=mocked_requests_post):
            with patch.object(runner._logger, "warning", new=mocked_logger_warning):
                runner.run()

    mocked_config_get.assert_has_calls([
        call("run_control.dry_run"),
        call("app.service.remote_url")
    ])
    mocked_requests_post.assert_called_once_with(
        f"{remote_url}/sysinfo", json={'sys_data': collected_data}
    )
    mocked_logger_warning.assert_called_once_with("Request was unsuccessful: 400")

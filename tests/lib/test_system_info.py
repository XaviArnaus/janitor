from pyxavi.config import Config
from src.lib.system_info import SystemInfo
from unittest.mock import patch, Mock
import psutil
import socket
from logging import Logger


CONFIG = {
    "logger.name": "logger_test",
    "system_info.thresholds": {
        "cpu_percent": {
            "value": 80.0,
            "type": "warning"
        },
        "memory_percent": {
            "value": 80.0,
            "type": "warning"
        },
        "disk_usage_percent": {
            "value": 80.0,
            "type": "alarm"
        },
    }
}


def patched_config_init(self):
    pass


def patched_config_get(self, param: str, default = None) -> str:
    return CONFIG[param]


def get_instance() -> SystemInfo:
    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            return SystemInfo(config=Config())


def test_initialize():
    system_info = get_instance()

    assert isinstance(system_info, SystemInfo)
    assert isinstance(system_info._config, Config)
    assert isinstance(system_info._logger, Logger)


def test_hostname():
    hostname = "endor"
    system_info = get_instance()

    mocked_hostname = Mock()
    mocked_hostname.return_value = hostname
    with patch.object(socket, "gethostname", new=mocked_hostname):
        assert system_info.get_hostname(), hostname


def test_cpu_data():
    cpu_percent = "50"
    cpu_count = "2"
    system_info = get_instance()

    mocked_cpu_percent = Mock()
    mocked_cpu_percent.return_value = cpu_percent
    mocked_cpu_count = Mock()
    mocked_cpu_count.return_value = cpu_count
    with patch.object(psutil, "cpu_percent", new=mocked_cpu_percent):
        with patch.object(psutil, "cpu_count", new=mocked_cpu_count):
            data = system_info.get_cpu_data()

    assert data, {
        "cpu_percent": cpu_percent,
        "cpu_count": cpu_count
    }


def test_mem_data():
    class InputData:
        def __init__(self, d:dict):
            for key, value in d.items():
                setattr(self, key, value)
    
    memory = InputData({
        "total": 8000,
        "available": 4000,
        "used": 3000,
        "free": 2000
    })

    system_info = get_instance()

    mocked_virtual_memory = Mock()
    mocked_virtual_memory.return_value = memory
    with patch.object(psutil, "virtual_memory", new=mocked_virtual_memory):
        data = system_info.get_mem_data()

    assert data, {
        "memory_total": memory.total,
        "memory_avail": memory.available,
        "memory_used": memory.used,
        "memory_free": memory.free,
        "memory_percent": round(( memory.used / memory.total ) * 100, 2)
    }


def test_disk_data():
    class InputData:
        def __init__(self, d:dict):
            for key, value in d.items():
                setattr(self, key, value)
    
    disk = InputData({
        "total": 8000,
        "used": 3000,
        "free": 2000,
        "percent": 25.4
    })

    system_info = get_instance()

    mocked_disk_usage= Mock()
    mocked_disk_usage.return_value = disk
    with patch.object(psutil, "disk_usage", new=mocked_disk_usage):
        data = system_info.get_disk_data()

    assert data, {
        "disk_usage_total": disk.total,
        "disk_usage_used": disk.used,
        "disk_usage_free": disk.free,
        "disk_usage_percent": disk.percent
    }


def test_crossed_thresholds_return_false():
    data = {
        "hostname": "endor",
        "cpu_percent": 50,
        "cpu_count": 2,
        "memory_total": 8000,
        "memory_avail": 4000,
        "memory_used": 3000,
        "memory_free": 2000,
        "memory_percent": 40,
        "disk_usage_total": 8000,
        "disk_usage_used": 4000,
        "disk_usage_free": 2000,
        "disk_usage_percent": 20
    }
    system_info = get_instance()

    with patch.object(Config, "get", new=patched_config_get):
        assert system_info.crossed_thresholds(data, ["hostname"]) == False


def test_crossed_thresholds_return_true():
    data = {
        "hostname": "endor",
        "cpu_percent": 50,
        "cpu_count": 2,
        "memory_total": 8000,
        "memory_avail": 4000,
        "memory_used": 3000,
        "memory_free": 2000,
        "memory_percent": 85,
        "disk_usage_total": 8000,
        "disk_usage_used": 4000,
        "disk_usage_free": 2000,
        "disk_usage_percent": 20
    }
    system_info = get_instance()

    with patch.object(Config, "get", new=patched_config_get):
        assert system_info.crossed_thresholds(data, ["hostname"]) == True
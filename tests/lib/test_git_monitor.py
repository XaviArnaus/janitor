from pyxavi.config import Config
from pyxavi.storage import Storage
from janitor.lib.git_monitor import GitMonitor
from unittest.mock import patch, Mock
from logging import Logger
import requests

CONFIG = {"logger.name": "logger_test", "git_monitor.file": "storage/git_monitor.yaml"}


def patched_config_init(self):
    pass


def patched_config_get(self, param: str, default=None) -> str:
    return CONFIG[param]


def patched_storage_init(self, filename):
    pass


def patched_storage_write(self):
    pass


def patched_storage_get(self, param_name: str = "", default_value: any = None) -> any:
    return []


def get_instance() -> GitMonitor:
    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            with patch.object(Storage, "__init__", new=patched_storage_init):
                return GitMonitor(config=Config())


def test_initialize():
    updater = get_instance()

    assert isinstance(updater, GitMonitor)
    assert isinstance(updater._config, Config)
    assert isinstance(updater._logger, Logger)
    assert isinstance(updater._storage, Storage)



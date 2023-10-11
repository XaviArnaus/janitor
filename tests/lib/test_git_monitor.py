from pyxavi.config import Config
from pyxavi.storage import Storage
from janitor.lib.git_monitor import GitMonitor
from unittest.mock import patch, Mock
import pytest
from unittest import TestCase
from logging import Logger
from git import Repo
import os

CONFIG = {"logger.name": "logger_test", "git_monitor.file": "storage/git_monitor.yaml"}
REPOSITORY = {
    "name": "pyxavi",
    "url": "https://github.com/XaviArnaus/pyxavi",
    "tags": ["#Python", "#library"],
    "git": "git@github.com:XaviArnaus/pyxavi.git",
    "path": "storage/repos/pyxavi",
    "changelog": {
        "file": "CHANGELOG.md",
        "section_separator": r"\n## ",
        "version_regex": r"\[(v[0-9]+\.[0-9]+\.[0-9]+)\]"
    }
}


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
    monitor = get_instance()

    assert isinstance(monitor, GitMonitor)
    assert isinstance(monitor._config, Config)
    assert isinstance(monitor._logger, Logger)
    assert isinstance(monitor._storage, Storage)

@pytest.mark.parametrize(
    argnames=('repository', 'path_exist', 'expected_exception'),
    argvalues=[
        ({"none":"none"}, None, True),
        ({"git":"yes"}, None, True),
        ({"path":"yes"}, True, False),
        ({"path":"yes", "git":"yes"}, False, False),
    ],
)
def test_initiate_existing_repository(repository, path_exist, expected_exception):

    monitor = get_instance()

    if expected_exception:
        with TestCase.assertRaises(monitor, RuntimeError):
            monitor.initiate_or_clone_repository(repository=repository)
    else:
        mocked_starter = Mock()
        mocked_path_exists = Mock()
        mocked_path_exists.return_value = path_exist
        if path_exist is True:
            with patch.object(os.path, "exists", new=mocked_path_exists):
                with patch.object(Repo, "init", new=mocked_starter):
                    monitor.initiate_or_clone_repository(repository=repository)
                mocked_starter.assert_called_once_with(repository["path"])
        else:
            with patch.object(os.path, "exists", new=mocked_path_exists):
                with patch.object(Repo, "clone_from", new=mocked_starter):
                    monitor.initiate_or_clone_repository(repository=repository)
                mocked_starter.assert_called_once_with(repository["git"], repository["path"])

def test_get_updates():
    mocked_repo = Mock()
    mocked_remotes = Mock()
    mocked_origin = Mock()
    mocked_pull = Mock()
    mocked_origin.return_value = mocked_pull
    mocked_remotes.return_value = mocked_origin
    mocked_repo.return_value = mocked_remotes

    monitor = get_instance()
    monitor.current_repository = mocked_repo

    with patch.object(mocked_origin, "pull", new=mocked_pull):
        monitor.get_updates()
    
    mocked_pull.assert_called_once()
from pyxavi.config import Config
from pyxavi.storage import Storage
from janitor.lib.git_monitor import GitMonitor
from unittest.mock import patch, Mock, mock_open, MagicMock, call
import pytest
from unittest import TestCase
from logging import Logger
from git import Repo
import os
import builtins
from slugify import slugify


CONFIG = {"logger.name": "logger_test", "git_monitor.file": "storage/git_monitor.yaml"}
REPOSITORY = {
    "name": "pyxavi",
    "url": "https://github.com/XaviArnaus/pyxavi",
    "tags": ["#Python", "#library"],
    "git": "git@github.com:XaviArnaus/pyxavi.git",
    "path": "storage/repos/pyxavi",
    "changelog": {
        "file": "CHANGELOG.md",
        "section_separator": "\n## ",
        "version_regex": r"\[(v[0-9]+\.[0-9]+\.?[0-9]?)\]"
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

    monitor = get_instance()
    monitor.current_repository = mocked_repo

    with patch.object(mocked_origin, "pull", new=mocked_pull):
        with patch.object(mocked_remotes, "origin", new=mocked_origin):
            with patch.object(mocked_repo, "remotes", new=mocked_remotes):
                monitor.get_updates()
    
    mocked_pull.assert_called_once()

def test_get_changelog_content_exception_when_not_file():
    changelog_filename = "this/is/a/changelog.md"
    is_file = False
    mocked_repo = Mock()
    working_tree_dir = "test"

    monitor = get_instance()
    monitor.repository_info = REPOSITORY
    monitor.current_repository = mocked_repo

    mocked_working_tree_dir = Mock()
    mocked_working_tree_dir.return_value = working_tree_dir
    mocked_path_join = Mock()
    mocked_path_join.return_value = changelog_filename
    mocked_path_isfile = Mock()
    mocked_path_isfile.return_value = is_file
    with patch.object(mocked_repo, "working_tree_dir", new=mocked_working_tree_dir):
        with patch.object(os.path, "join", new=mocked_path_join):
            with patch.object(os.path, "isfile", new=mocked_path_isfile):
                with TestCase.assertRaises(monitor, RuntimeError):
                    monitor.get_changelog_content()
    
    mocked_path_join.assert_called_once_with(
        mocked_working_tree_dir, REPOSITORY["changelog"]["file"]
    )

def test_get_changelog_content_reads_file_when_isfile():
    changelog_filename = "this/is/a/changelog.md"
    is_file = True
    mocked_repo = Mock()
    working_tree_dir = "test"
    content = "test content"

    monitor = get_instance()
    monitor.repository_info = REPOSITORY
    monitor.current_repository = mocked_repo

    mocked_working_tree_dir = Mock()
    mocked_working_tree_dir.return_value = working_tree_dir
    mocked_path_join = Mock()
    mocked_path_join.return_value = changelog_filename
    mocked_path_isfile = Mock()
    mocked_path_isfile.return_value = is_file
    mocked_open_file = MagicMock()
    with patch.object(mocked_repo, "working_tree_dir", new=mocked_working_tree_dir):
        with patch.object(os.path, "join", new=mocked_path_join):
            with patch.object(os.path, "isfile", new=mocked_path_isfile):
                with patch.object(builtins, "open", mock_open(mock=mocked_open_file, read_data=content)):
                    returned_content = monitor.get_changelog_content()
    
    mocked_path_join.assert_called_once_with(
        mocked_working_tree_dir, REPOSITORY["changelog"]["file"]
    )
    mocked_open_file.assert_called_once_with(
        changelog_filename, 'r'
    )
    assert returned_content == content

@pytest.fixture
def content_3():
    return "## [v3.0](link.html)\n\n### Added\n\n- Action 3\n"

@pytest.fixture
def content_3_fail():
    return "## [ABC](link.html)\n\n### Added\n\n- Action 3\n"

@pytest.fixture
def content_2():
    return "## [v2.0](link.html)\n\n### Changed\n\n- Action 2\n"

@pytest.fixture
def content_1():
    return "## [v1.0](link.html)\n\n### Removed\n\n- Action 1\n"

@pytest.mark.parametrize(
    argnames=('last_version', 'expected_parsed', 'content1_name', 'content2_name', 'content3_name'),
    argvalues=[
        ("v2.0", {"v3.0": "content_3"}, "content_1", "content_2", "content_3"),
        ("v1.0", {"v3.0": "content_3", "v2.0": "content_2"}, "content_1", "content_2", "content_3"),
        (None, {}, "content_1", "content_2", "content_3"),
        (None, False, "content_1", "content_2", "content_3_fail"),
    ],
)
def test_parse_changelog(last_version, expected_parsed: dict, content1_name, content2_name, content3_name, request):
    content_1 = request.getfixturevalue(content1_name)
    content_2 = request.getfixturevalue(content2_name)
    content_3 = request.getfixturevalue(content3_name)
    if type(expected_parsed) == dict:
        expected_parsed = {key: request.getfixturevalue(value).replace("## [", "[") for key, value in expected_parsed.items()}
    # Remember that the Changelog comes from newer to older
    content = f"# Title\n\n{content_3}\n{content_2}\n{content_1}"

    monitor = get_instance()
    monitor.repository_info = REPOSITORY

    mocked_storage_get = Mock()
    mocked_storage_get.side_effect = [
        {},
        last_version
    ]
    mocked_storage_set = Mock()
    mocked_storage_write_file = Mock()
    with patch.object(monitor._storage, "get", new=mocked_storage_get):
        with patch.object(monitor._storage, "set", new=mocked_storage_set):
            if last_version is None:
                if expected_parsed is False:
                    with TestCase.assertRaises(monitor, RuntimeError):
                        monitor.parse_changelog(content=content)
                else:
                    with patch.object(monitor._storage, "write_file", new=mocked_storage_write_file):
                        result = monitor.parse_changelog(content=content)
                        assert result == expected_parsed
                        mocked_storage_set.assert_has_calls([
                            call(slugify(REPOSITORY["git"]), {}),
                            call(slugify(REPOSITORY["git"]) + ".last_version", "v3.0"),
                        ])
                        mocked_storage_write_file.assert_called_once()
            else:
                with patch.object(monitor._storage, "write_file", new=mocked_storage_write_file):
                    result = monitor.parse_changelog(content=content)
                    assert result == expected_parsed
                    mocked_storage_set.assert_called_once_with(slugify(REPOSITORY["git"]), {})
                    mocked_storage_write_file.assert_not_called()

from pyxavi.config import Config
from pyxavi.logger import Logger
from pyxavi.storage import Storage
from pyxavi.dictionary import Dictionary
from janitor.lib.git_monitor import GitMonitor, ChangelogChanges, ChangesProtocol, CommitsChanges
from janitor.objects.message import Message
from unittest.mock import patch, Mock, mock_open, MagicMock, call
import pytest
from unittest import TestCase
from logging import Logger as Logging
from git import Repo
import os
import builtins
from slugify import slugify

CONFIG = {"logger.name": "logger_test", "git_monitor.file": "storage/git_monitor.yaml"}
REPOSITORY_CHANGELOG = {
    "name": "pyxavi",
    "url": "https://github.com/XaviArnaus/pyxavi",
    "tags": ["#Python", "#library"],
    "git": "git@github.com:XaviArnaus/pyxavi.git",
    "path": "storage/repos/pyxavi",
    "monitoring_method": "changelog",
    "params": {
        "file": "CHANGELOG.md",
        "section_separator": "\n## ",
        "version_regex": r"\[(v[0-9]+\.[0-9]+\.?[0-9]?)\]"
    }
}

REPOSITORY_COMMITS = {
    "name": "pyxavi",
    "url": "https://github.com/XaviArnaus/pyxavi",
    "tags": ["#Python", "#library"],
    "git": "git@github.com:XaviArnaus/pyxavi.git",
    "path": "storage/repos/pyxavi",
    "monitoring_method": "commits",
    "params": {
        "file": "CHANGELOG.md",
        "section_separator": "\n## ",
        "version_regex": r"\[(v[0-9]+\.[0-9]+\.?[0-9]?)\]"
    }
}


@pytest.fixture
def content_30():
    return "## [v3.0.0](link.html)\n\n### Added\n\n- Action 33\n"


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
    assert isinstance(monitor._logger, Logging)
    assert isinstance(monitor._storage, Storage)


@pytest.mark.parametrize(
    argnames=('repository', 'path_exist', 'expected_exception'),
    argvalues=[
        ({
            "name": "test_name", "none": "none"
        }, None, True),
        ({
            "name": "test_name", "git": "yes"
        }, None, True),
        ({
            "name": "test_name", "path": "yes"
        }, True, False),
        ({
            "name": "test_name", "path": "yes", "git": "yes"
        }, False, False),
    ],
)
def test_initiate_existing_repository(repository, path_exist, expected_exception):

    monitor = get_instance()

    if expected_exception:
        with TestCase.assertRaises(monitor, RuntimeError):
            monitor.initiate_or_clone_repository(repository_info=Dictionary(repository))
    else:
        mocked_starter = Mock()
        mocked_path_exists = Mock()
        mocked_path_exists.return_value = path_exist
        if path_exist is True:
            with patch.object(os.path, "exists", new=mocked_path_exists):
                with patch.object(Repo, "init", new=mocked_starter):
                    monitor.initiate_or_clone_repository(repository_info=Dictionary(repository))
                mocked_starter.assert_called_once_with(repository["path"])
        else:
            with patch.object(os.path, "exists", new=mocked_path_exists):
                with patch.object(Repo, "clone_from", new=mocked_starter):
                    monitor.initiate_or_clone_repository(repository_info=Dictionary(repository))
                mocked_starter.assert_called_once_with(repository["git"], repository["path"])


def test_get_updates():
    mocked_repo = Mock()
    mocked_remotes = Mock()
    mocked_origin = Mock()
    mocked_pull = Mock()

    monitor = get_instance()
    monitor.repository_info = Dictionary(REPOSITORY_CHANGELOG)
    monitor.current_repository = mocked_repo

    with patch.object(mocked_origin, "pull", new=mocked_pull):
        with patch.object(mocked_remotes, "origin", new=mocked_origin):
            with patch.object(mocked_repo, "remotes", new=mocked_remotes):
                monitor.get_updates()

    mocked_pull.assert_called_once()


def test_get_changes_instance_for_changelog():
    dictionary_monitoring_method = "changelog"

    mocked_repo = Mock()
    monitor = get_instance()
    monitor.repository_info = Dictionary(REPOSITORY_CHANGELOG)
    monitor.current_repository = mocked_repo
    
    mocked_changelog_changes_init = Mock()
    mocked_changelog_changes_init.return_value = None
    mocked_changelog_changes_init.__class__ = ChangelogChanges
    mocked_commits_changes_init = Mock()
    mocked_commits_changes_init.return_value = None
    mocked_commits_changes_init.__class__ = CommitsChanges
    mocked_dictionary_get = Mock()
    mocked_dictionary_get.return_value = dictionary_monitoring_method
    with patch.object(Dictionary, "get", new=mocked_dictionary_get):
        with patch.object(ChangelogChanges, "__init__", new=mocked_changelog_changes_init):
            with patch.object(CommitsChanges, "__init__", new=mocked_commits_changes_init):
                returned_instance = monitor.get_changes_instance()

    assert isinstance(returned_instance, ChangelogChanges) is True
    mocked_changelog_changes_init.assert_called_once_with(
        config=monitor._config,
        logger=monitor._logger,
        repository_info=monitor.repository_info,
        repository_object=monitor.current_repository
    )
    mocked_commits_changes_init.assert_not_called()

def test_get_changes_instance_for_commits():
    dictionary_monitoring_method = "commits"

    mocked_repo = Mock()
    monitor = get_instance()
    monitor.repository_info = Dictionary(REPOSITORY_COMMITS)
    monitor.current_repository = mocked_repo
    
    mocked_changelog_changes_init = Mock()
    mocked_changelog_changes_init.return_value = None
    mocked_changelog_changes_init.__class__ = ChangelogChanges
    mocked_commits_changes_init = Mock()
    mocked_commits_changes_init.return_value = None
    mocked_commits_changes_init.__class__ = CommitsChanges
    mocked_dictionary_get = Mock()
    mocked_dictionary_get.return_value = dictionary_monitoring_method
    with patch.object(Dictionary, "get", new=mocked_dictionary_get):
        with patch.object(ChangelogChanges, "__init__", new=mocked_changelog_changes_init):
            with patch.object(CommitsChanges, "__init__", new=mocked_commits_changes_init):
                returned_instance = monitor.get_changes_instance()

    assert isinstance(returned_instance, CommitsChanges) is True
    mocked_changelog_changes_init.assert_not_called()
    mocked_commits_changes_init.assert_called_once_with(
        config=monitor._config,
        logger=monitor._logger,
        repository_info=monitor.repository_info,
        repository_object=monitor.current_repository
    )

def test_get_changes_instance_for_unknown():
    dictionary_monitoring_method = "unknown"

    mocked_repo = Mock()
    monitor = get_instance()
    monitor.repository_info = Dictionary(REPOSITORY_COMMITS)
    monitor.current_repository = mocked_repo
    
    mocked_changelog_changes_init = Mock()
    mocked_changelog_changes_init.return_value = None
    mocked_changelog_changes_init.__class__ = ChangelogChanges
    mocked_commits_changes_init = Mock()
    mocked_commits_changes_init.return_value = None
    mocked_commits_changes_init.__class__ = CommitsChanges
    mocked_dictionary_get = Mock()
    mocked_dictionary_get.return_value = dictionary_monitoring_method
    with patch.object(Dictionary, "get", new=mocked_dictionary_get):
        with patch.object(ChangelogChanges, "__init__", new=mocked_changelog_changes_init):
            with patch.object(CommitsChanges, "__init__", new=mocked_commits_changes_init):
                with TestCase.assertRaises(monitor, RuntimeError):
                    returned_instance = monitor.get_changes_instance()

    mocked_changelog_changes_init.assert_not_called()
    mocked_commits_changes_init.assert_not_called


def test_monitor_get_current_last_known():
    value_to_return = "v1.2"

    monitor = get_instance()

    mock_changes_instance = Mock()
    mock_get_changes_instance = Mock()
    mock_get_changes_instance.return_value = mock_changes_instance
    mock_changes_get_current_last_known = Mock()
    mock_changes_get_current_last_known.return_value = value_to_return
    with patch.object(monitor, "get_changes_instance", new=mock_get_changes_instance):
        with patch.object(mock_changes_instance, "get_current_last_known", new=mock_changes_get_current_last_known):
            returned = monitor.get_current_last_known()
    
    assert returned == value_to_return
    mock_get_changes_instance.assert_called_once()
    mock_changes_get_current_last_known.assert_called_once()


def test_monitor_get_new_last_known():
    value_to_return = "v1.2"

    monitor = get_instance()

    mock_changes_instance = Mock()
    mock_get_changes_instance = Mock()
    mock_get_changes_instance.return_value = mock_changes_instance
    mock_changes_get_new_last_known = Mock()
    mock_changes_get_new_last_known.return_value = value_to_return
    with patch.object(monitor, "get_changes_instance", new=mock_get_changes_instance):
        with patch.object(mock_changes_instance, "get_new_last_known", new=mock_changes_get_new_last_known):
            returned = monitor.get_new_last_known()
    
    assert returned == value_to_return
    mock_get_changes_instance.assert_called_once()
    mock_changes_get_new_last_known.assert_called_once()


def test_monitor_get_update_message():
    value_to_return = "I am an update text"

    monitor = get_instance()

    mock_changes_instance = Mock()
    mock_get_changes_instance = Mock()
    mock_get_changes_instance.return_value = mock_changes_instance
    mock_changes_build_update_message = Mock()
    mock_changes_build_update_message.return_value = value_to_return
    with patch.object(monitor, "get_changes_instance", new=mock_get_changes_instance):
        with patch.object(mock_changes_instance, "build_update_message", new=mock_changes_build_update_message):
            returned = monitor.get_update_message()
    
    assert returned == value_to_return
    mock_get_changes_instance.assert_called_once()
    mock_changes_build_update_message.assert_called_once()


def test_monitor_get_update_message_with_parameters():
    value_to_return = "I am an update text"
    parameters = {"a": "b"}

    monitor = get_instance()

    mock_changes_instance = Mock()
    mock_get_changes_instance = Mock()
    mock_get_changes_instance.return_value = mock_changes_instance
    mock_changes_build_update_message = Mock()
    mock_changes_build_update_message.return_value = value_to_return
    with patch.object(monitor, "get_changes_instance", new=mock_get_changes_instance):
        with patch.object(mock_changes_instance, "build_update_message", new=mock_changes_build_update_message):
            returned = monitor.get_update_message(parameters=parameters)
    
    assert returned == value_to_return
    mock_get_changes_instance.assert_called_once()
    mock_changes_build_update_message.assert_called_once_with(
        parameters=parameters
    )


def test_monitor_get_changes_note():
    value_to_return = "I am a changes note"

    monitor = get_instance()

    mock_changes_instance = Mock()
    mock_get_changes_instance = Mock()
    mock_get_changes_instance.return_value = mock_changes_instance
    mock_changes_get_changes_note = Mock()
    mock_changes_get_changes_note.return_value = value_to_return
    with patch.object(monitor, "get_changes_instance", new=mock_get_changes_instance):
        with patch.object(mock_changes_instance, "get_changes_note", new=mock_changes_get_changes_note):
            returned = monitor.get_changes_note()
    
    assert returned == value_to_return
    mock_get_changes_instance.assert_called_once()
    mock_changes_get_changes_note.assert_called_once()


def test_monitor_write_new_last_known():
    value_to_write = "v1.2"

    monitor = get_instance()

    mock_changes_instance = Mock()
    mock_get_changes_instance = Mock()
    mock_get_changes_instance.return_value = mock_changes_instance
    mock_changes_write_new_last_known = Mock()
    with patch.object(monitor, "get_changes_instance", new=mock_get_changes_instance):
        with patch.object(mock_changes_instance, "write_new_last_known", new=mock_changes_write_new_last_known):
            returned = monitor.write_new_last_known(value=value_to_write)
    
    mock_get_changes_instance.assert_called_once()
    mock_changes_write_new_last_known.assert_called_once_with(
        value=value_to_write
    )


############ CHANGELOG changes class ################

def get_changelog_instance(repo_info, repo_object, avoid_discover_changes = False) -> ChangesProtocol:
    mock_logger = Mock()
    mock_logger.return_value = None
    mock_logging_instance = Mock()
    mock_logging = Mock()
    mock_logging.__class__ = Logging
    mock_logging.return_value = mock_logging_instance
    mock_discover_changes = Mock()
    mocked_logging_debug = Mock()
    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            with patch.object(Logger, "__init__", new=mock_logger):
                with patch.object(mock_logger, "get_logger", new=mock_logging):
                    with patch.object(mock_logging_instance, "debug", new=mocked_logging_debug):
                        with patch.object(Storage, "__init__", new=patched_storage_init):
                            if avoid_discover_changes:
                                with patch.object(ChangelogChanges, "discover_changes", new=mock_discover_changes):
                                    config = Config()
                                    return ChangelogChanges(
                                        config=config,
                                        logger=mock_logger,
                                        repository_info=repo_info,
                                        repository_object=repo_object
                                    )
                            else:
                                config = Config()
                                return ChangelogChanges(
                                    config=config,
                                    logger=mock_logger,
                                    repository_info=repo_info,
                                    repository_object=repo_object
                                )

def test_changelog_discover_changes_exception_when_not_file():
    changelog_filename = "this/is/a/changelog.md"
    is_file = False
    mocked_repo = Mock()
    working_tree_dir = "test"

    mocked_working_tree_dir = Mock()
    mocked_working_tree_dir.return_value = working_tree_dir
    mocked_path_join = Mock()
    mocked_path_join.return_value = changelog_filename
    mocked_path_isfile = Mock()
    mocked_path_isfile.return_value = is_file
    with patch.object(mocked_repo, "working_tree_dir", new=mocked_working_tree_dir):
        with patch.object(os.path, "join", new=mocked_path_join):
            with patch.object(os.path, "isfile", new=mocked_path_isfile):
                with TestCase.assertRaises(ChangelogChanges, RuntimeError):
                    controller = get_changelog_instance(
                        repo_info=Dictionary(REPOSITORY_CHANGELOG),
                        repo_object=mocked_repo
                    )

    mocked_path_join.assert_called_once_with(
        mocked_working_tree_dir, REPOSITORY_CHANGELOG["params"]["file"]
    )

@pytest.mark.parametrize(
    argnames=(
        'last_version', 'expected_parsed', 'content1_name', 'content2_name', 'content3_name'
    ),
    argvalues=[
        ("v2.0", {"v3.0.0": "content_30"}, "content_1", "content_2", "content_30"),
        ("v2.0", {"v3.0": "content_3"}, "content_1", "content_2", "content_3"),
        ("v1.0", {"v3.0": "content_3", "v2.0": "content_2"},
            "content_1",
            "content_2",
            "content_3"
        ),
        ("v2.0", False, "content_1", "content_2", "content_3_fail"),
    ],
)
def test_changelog_discover_changes_reads_file_when_isfile(
    last_version, expected_parsed: dict, content1_name, content2_name, content3_name, request
):
    changelog_filename = "this/is/a/changelog.md"
    is_file = True
    mocked_repo = Mock()
    working_tree_dir = "test"
    content = "test content"

    content_1 = request.getfixturevalue(content1_name)
    content_2 = request.getfixturevalue(content2_name)
    content_3 = request.getfixturevalue(content3_name)
    if type(expected_parsed) == dict:
        expected_parsed = {
            key: request.getfixturevalue(value).replace("## [", "[")
            for key,
            value in expected_parsed.items()
        }
    # Remember that the Changelog comes from newer to older
    content = f"# Title\n\n{content_3}\n{content_2}\n{content_1}"

    mocked_working_tree_dir = Mock()
    mocked_working_tree_dir.return_value = working_tree_dir
    mocked_path_join = Mock()
    mocked_path_join.return_value = changelog_filename
    mocked_path_isfile = Mock()
    mocked_path_isfile.return_value = is_file
    mocked_open_file = MagicMock()
    mocked_storage_get = Mock()
    mocked_storage_get.side_effect = [{}, last_version]
    mocked_storage_set = Mock()
    with patch.object(Storage, "get", new=mocked_storage_get):
        with patch.object(Storage, "set", new=mocked_storage_set):
            with patch.object(mocked_repo, "working_tree_dir", new=mocked_working_tree_dir):
                with patch.object(os.path, "join", new=mocked_path_join):
                    with patch.object(os.path, "isfile", new=mocked_path_isfile):
                        with patch.object(builtins,
                                        "open",
                                        mock_open(mock=mocked_open_file, read_data=content)):

                            if expected_parsed is False:
                                with TestCase.assertRaises(ChangelogChanges, RuntimeError):
                                    controller = get_changelog_instance(
                                        repo_info=Dictionary(REPOSITORY_CHANGELOG),
                                        repo_object=mocked_repo
                                    )
                            else:
                                controller = get_changelog_instance(
                                    repo_info=Dictionary(REPOSITORY_CHANGELOG),
                                    repo_object=mocked_repo
                                )
                                result = controller._changes_stack
                                assert result == expected_parsed
                                mocked_storage_set.assert_has_calls(
                                    [
                                        call(slugify(REPOSITORY_CHANGELOG["git"]), {}),
                                    ]
                                )

    mocked_path_join.assert_called_once_with(
        mocked_working_tree_dir, REPOSITORY_CHANGELOG["params"]["file"]
    )
    mocked_open_file.assert_called_once_with(changelog_filename, 'r')


def test_changelog_build_update_message_with_one_update(content_3):
    parsed_content = {"v3.0": content_3.replace("## [", "[")}
    expected_content = Message(
        text="**[pyxavi](https://github.com/XaviArnaus/pyxavi) v3.0** published!\n\n" +
        "[v3.0](link.html)\n\n**Added**\n- Action 3\n\n#Python #library\n"
    )

    mocked_repo = Mock()
    controller = get_changelog_instance(
        repo_info=Dictionary(REPOSITORY_CHANGELOG),
        repo_object=mocked_repo,
        avoid_discover_changes=True
    )
    controller._changes_stack = parsed_content

    message = controller.build_update_message()

    assert message.to_dict() == expected_content.to_dict()


def test_changelog_build_update_message_with_two_updates(content_3, content_2):
    parsed_content = {
        "v3.0": content_3.replace("## [", "["), "v2.0": content_2.replace("## [", "[")
    }
    expected_content = Message(
        text="**[pyxavi](https://github.com/XaviArnaus/pyxavi) " +
        "v2.0 & v3.0** published!\n\n[v3.0](link.html)\n\n**Added**\n- Action 3\n\n" +
        "[v2.0](link.html)\n\n**Changed**\n- Action 2\n\n#Python #library\n"
    )

    mocked_repo = Mock()
    controller = get_changelog_instance(
        repo_info=Dictionary(REPOSITORY_CHANGELOG),
        repo_object=mocked_repo,
        avoid_discover_changes=True
    )
    controller._changes_stack = parsed_content

    message = controller.build_update_message()

    assert message.to_dict() == expected_content.to_dict()


def test_changelog_write_new_last_known():
    value_to_write = "v1.2"

    mocked_storage_write = Mock()
    mocked_storage_get = Mock()
    mocked_storage_get.return_value = {}
    mocked_storage_set = Mock()
    with patch.object(Storage, "get", new=mocked_storage_get):
        with patch.object(Storage, "set", new=mocked_storage_set):
            with patch.object(Storage, "write_file", new=mocked_storage_write):
                mocked_repo = Mock()
                controller = get_changelog_instance(
                    repo_info=Dictionary(REPOSITORY_CHANGELOG),
                    repo_object=mocked_repo,
                    avoid_discover_changes=True
                )
                controller.write_new_last_known(value=value_to_write)
    
    mocked_storage_set.assert_has_calls(
        [
            call(slugify(REPOSITORY_CHANGELOG["git"]), {}),
            call(slugify(REPOSITORY_CHANGELOG["git"]) + ".last_version", value_to_write)
        ]
    )
    mocked_storage_write.assert_called_once()

@pytest.mark.parametrize(
    argnames=(
        'changes_stack', 'expected_note'
    ),
    argvalues=[
        ({"v3.0": "I am a content v3"}, "v3.0"),
        ({"v2.0": "I am a content v2", "v3.0": "I am a content v3"}, "v2.0 & v3.0"),
        ({"v1.0": "I am a content v1", "v2.0": "I am a content v2", "v3.0": "I am a content v3"}, "v1.0, v2.0 & v3.0"),
        ({"v3.0": "I am a content v3", "v2.0": "I am a content v2"}, "v2.0 & v3.0"),
        ({"v3.0": "I am a content v3", "v2.0": "I am a content v2", "v1.0": "I am a content v1"}, "v1.0, v2.0 & v3.0"),
        ({"v1.1": "I am a content v1", "v1.2": "I am a content v2", "v1.3": "I am a content v3"}, "v1.1, v1.2 & v1.3"),
        ({"v1.6": "I am a content v1", "v2.4": "I am a content v2", "v3.1": "I am a content v3"}, "v1.6, v2.4 & v3.1"),
    ],
)
def test_changelog_changes_note(changes_stack, expected_note):
    mocked_repo = Mock()
    controller = get_changelog_instance(
        repo_info=Dictionary(REPOSITORY_CHANGELOG),
        repo_object=mocked_repo,
        avoid_discover_changes=True
    )
    controller._changes_stack = changes_stack

    assert controller.get_changes_note() == expected_note

############ COMMITS changes class ################

def get_commits_instance(repo_info, repo_object, avoid_discover_changes = False) -> ChangesProtocol:
    mock_logger = Mock()
    mock_logger.return_value = None
    mock_logging_instance = Mock()
    mock_logging = Mock()
    mock_logging.__class__ = Logging
    mock_logging.return_value = mock_logging_instance
    mock_discover_changes = Mock()
    mocked_logging_debug = Mock()
    with patch.object(Config, "__init__", new=patched_config_init):
        with patch.object(Config, "get", new=patched_config_get):
            with patch.object(Logger, "__init__", new=mock_logger):
                with patch.object(mock_logger, "get_logger", new=mock_logging):
                    with patch.object(mock_logging_instance, "debug", new=mocked_logging_debug):
                        with patch.object(Storage, "__init__", new=patched_storage_init):
                            if avoid_discover_changes:
                                with patch.object(CommitsChanges, "discover_changes", new=mock_discover_changes):
                                    config = Config()
                                    return CommitsChanges(
                                        config=config,
                                        logger=mock_logger,
                                        repository_info=repo_info,
                                        repository_object=repo_object
                                    )
                            else:
                                config = Config()
                                return CommitsChanges(
                                    config=config,
                                    logger=mock_logger,
                                    repository_info=repo_info,
                                    repository_object=repo_object
                                )

def test_commits_discover_changes_rev_list_empty():
    last_known_commit = None
    commits = []
    expected_stack = {}

    mocked_last_knwon = Mock()
    mocked_last_knwon.return_value = last_known_commit
    mocked_iter_commits = Mock()
    mocked_iter_commits.return_value = commits
    mocked_repo = Mock()
    with patch.object(CommitsChanges, "get_current_last_known", new=mocked_last_knwon):
        with patch.object(mocked_repo, "iter_commits", new=mocked_iter_commits):
            controller = get_commits_instance(
                Dictionary(REPOSITORY_COMMITS),
                mocked_repo
            )
            assert controller._changes_stack == expected_stack

def test_commits_discover_changes_rev_list_full():
    last_known_commit = None

    class Commit:
        binsha: bytes
        author: str
        message: str

        def __init__(self, binsha: bytes, author: str, message: str) -> None:
            self.binsha = binsha
            self.author = author
            self.message = message

    commits = [
        Commit(bytes("test1".encode("utf-8")), "Xavi", "Description 1"),
        Commit(bytes("test2".encode("utf-8")), "Xavi", "Description 2"),
        Commit(bytes("test3".encode("utf-8")), "Xavi", "Description 3"),
    ]
    expected_stack = {
        "test1".encode("utf-8").hex(): {"author": "Xavi", "message": "Description 1"},
        "test2".encode("utf-8").hex(): {"author": "Xavi", "message": "Description 2"},
        "test3".encode("utf-8").hex(): {"author": "Xavi", "message": "Description 3"},
    }

    mocked_last_knwon = Mock()
    mocked_last_knwon.return_value = last_known_commit
    mocked_iter_commits = Mock()
    mocked_iter_commits.return_value = commits
    mocked_repo = Mock()
    with patch.object(CommitsChanges, "get_current_last_known", new=mocked_last_knwon):
        with patch.object(mocked_repo, "iter_commits", new=mocked_iter_commits):
            controller = get_commits_instance(
                Dictionary(REPOSITORY_COMMITS),
                mocked_repo
            )
            assert controller._changes_stack == expected_stack

def test_commits_get_current_last_known():
    value_to_read = "v1.2"

    mocked_storage_get = Mock()
    mocked_storage_get.return_value = value_to_read
    mocked_storage_get.side_effect = [{}, value_to_read]
    mocked_storage_set = Mock()
    with patch.object(Storage, "get", new=mocked_storage_get):
        with patch.object(Storage, "set", new=mocked_storage_set):
            mocked_repo = Mock()
            controller = get_commits_instance(
                repo_info=Dictionary(REPOSITORY_COMMITS),
                repo_object=mocked_repo,
                avoid_discover_changes=True
            )
            returned_value = controller.get_current_last_known()
    
    assert returned_value == value_to_read


def test_commits_build_update_message_with_one_update(content_3):
    parsed_content = {
        "test1".encode("utf-8").hex(): {"author": "Xavi", "message": "Description 1"},
    }
    expected_content = Message(
        text="**[pyxavi](https://github.com/XaviArnaus/pyxavi) 1 new commits** published!\n" +
        "\n- *Xavi*: Description 1\n#Python #library\n"
    )

    mocked_repo = Mock()
    controller = get_commits_instance(
        repo_info=Dictionary(REPOSITORY_COMMITS),
        repo_object=mocked_repo,
        avoid_discover_changes=True
    )
    controller._changes_stack = parsed_content

    message = controller.build_update_message()

    assert message.to_dict() == expected_content.to_dict()


def test_commits_build_update_message_with_two_updates(content_3, content_2):
    parsed_content = {
        "test1".encode("utf-8").hex(): {"author": "Xavi", "message": "Description 1"},
        "test2".encode("utf-8").hex(): {"author": "Xavi", "message": "Description 2"},
    }
    expected_content = Message(
        text="**[pyxavi](https://github.com/XaviArnaus/pyxavi) 2 new commits** published!\n" +
        "\n- *Xavi*: Description 1\n- *Xavi*: Description 2\n#Python #library\n"
    )

    mocked_repo = Mock()
    controller = get_commits_instance(
        repo_info=Dictionary(REPOSITORY_COMMITS),
        repo_object=mocked_repo,
        avoid_discover_changes=True
    )
    controller._changes_stack = parsed_content

    message = controller.build_update_message()

    assert message.to_dict() == expected_content.to_dict()

def test_commits_write_new_last_known():
    value_to_write = "test1".encode("utf-8").hex()

    mocked_storage_write = Mock()
    mocked_storage_get = Mock()
    mocked_storage_get.return_value = {}
    mocked_storage_set = Mock()
    with patch.object(Storage, "get", new=mocked_storage_get):
        with patch.object(Storage, "set", new=mocked_storage_set):
            with patch.object(Storage, "write_file", new=mocked_storage_write):
                mocked_repo = Mock()
                controller = get_commits_instance(
                    repo_info=Dictionary(REPOSITORY_CHANGELOG),
                    repo_object=mocked_repo,
                    avoid_discover_changes=True
                )
                controller.write_new_last_known(value=value_to_write)
    
    mocked_storage_set.assert_has_calls(
        [
            call(slugify(REPOSITORY_COMMITS["git"]), {}),
            call(slugify(REPOSITORY_COMMITS["git"]) + ".last_commit", value_to_write)
        ]
    )
    mocked_storage_write.assert_called_once()


def test_commits_changes_note():
    changes_stack = {
        "test1".encode("utf-8").hex(): {"author": "Xavi", "message": "Description 1"},
        "test2".encode("utf-8").hex(): {"author": "Xavi", "message": "Description 2"},
    }

    mocked_repo = Mock()
    controller = get_commits_instance(
        repo_info=Dictionary(REPOSITORY_COMMITS),
        repo_object=mocked_repo,
        avoid_discover_changes=True
    )
    controller._changes_stack = changes_stack

    assert controller.get_changes_note() == "2 new commits"
from pyxavi.config import Config
from pyxavi.storage import Storage
from pyxavi.dictionary import Dictionary
from janitor.objects.message import Message
from typing import Protocol
from git import Repo
from string import Template
from slugify import slugify
import logging
import os
import re
from pyxavi.debugger import dd

DEFAULT_FILENAME = "storage/git_monitor.yaml"
DEFAULT_VERSION_REGEX = r"\[(v[0-9]+\.[0-9]+\.?[0-9]?)\]"
DEFAULT_SECTION_SEPARATOR = "\n## "
DEFAULT_MONITORING_METHOD = "commits"
TEMPLATE_UPDATE_TEXT = "**[$project]($link) $version** published!\n\n$text\n$tags\n"


class ChangesProtocol(Protocol):
    def __init__(
        self, config: Config, logger: logging, repository_info: Dictionary, repository_object: Repo
    ) -> None:
        """Initializing the class"""
    
    def discover_changes(self, parameters: dict = None) -> None:
        """
        Method that triggers the discovery of the changes
            It is meant to keep a state internally of what to be published
        """
    
    def get_current_last_known(self) -> str:
        """Gets the current last known item, usually comes from the state"""
    
    def get_new_last_known(self) -> str:
        """Gets the new last known item, usually is the last parsed item"""
    
    def build_update_message(self, parameters: dict = None) -> Message:
        """Constructs the message to publish as an update"""
    
    def write_new_last_known(self, value: str) -> None:
        """It will write in the internal storage the last known item"""
    
    def get_changes_note(self) -> str:
        """It returns a string meant to be included in the summary message"""

class BaseChanges(ChangesProtocol):
    _config: Config
    _logger: logging
    _storage: Storage
    _repo_info: Dictionary
    _repo_object: Repo
    _changes_stack: dict

    def __init__(
        self, config: Config, logger: logging, repository_info: Dictionary, repository_object: Repo
    ) -> None:
        self._config = config
        self._logger = logger
        self._storage = Storage(config.get("git_monitor.file", DEFAULT_FILENAME))
        self._repo_info = repository_info
        self._repo_object = repository_object
        # The changes stack should keep the changes_id => changes_content dictionary
        #   sorted from newer to older
        #   We start from None to know if we already discovered the changes or not.
        self._changes_stack = None

        # Makes no sense to have this class without discovering the changes straight away
        self.discover_changes()
    
    def discover_changes(self, parameters: dict = None) -> None:
        raise NotImplementedError("The child class does not implement this method yet")
    
    def get_current_last_known(self) -> str:
        raise NotImplementedError("The child class does not implement this method yet")
    
    def get_new_last_known(self) -> str:
        if self._changes_stack is not None and len(self._changes_stack) > 0:
            # The newer should come first
            return list(self._changes_stack.keys())[0]
        else:
            return None
    
    def build_update_message(self, parameters: dict = None) -> Message:
        raise NotImplementedError("The child class does not implement this method yet")
    
    def write_new_last_known(self, value: str) -> None:
        raise NotImplementedError("The child class does not implement this method yet")
    
    def get_changes_note(self) -> str:
        raise NotImplementedError("The child class does not implement this method yet")

    def _get_param_name(self, param_name: str) -> str:
        current_repo_id = slugify(self._repo_info.get("git"))
        # This get/set dance ensures that the parameter parent will exist always
        current_value = self._storage.get(current_repo_id, {})
        self._storage.set(current_repo_id, current_value)

        return f"{current_repo_id}.{param_name}"


class ChangelogChanges(BaseChanges):

    STORAGE_PARAMETER_NAME = "last_version"

    def discover_changes(self, parameters: dict = None) -> None:
        # Get the content of the file to analyse
        content = self.__get_changelog_content()
        self._changes_stack = self.__parse_changelog(content=content)
    
    def get_current_last_known(self) -> str:
        return self._storage.get(
            self._get_param_name(self.STORAGE_PARAMETER_NAME), None
        )
    
    def build_update_message(self, parameters: dict = None) -> Message:
        return Message(
            text=Template(TEMPLATE_UPDATE_TEXT).substitute(
                project=self._repo_info.get("name"),
                link=self._repo_info.get("url"),
                version=self.get_changes_note(),
                text="\n".
                join([self._clean_markdown(text) for text in self._changes_stack.values()]),
                tags=" ".join(self._repo_info.get("tags", ""))
            )
        )
    
    def write_new_last_known(self, value: str) -> None:
        self._storage.set(self._get_param_name(self.STORAGE_PARAMETER_NAME), value)
        self._storage.write_file()
    
    def get_changes_note(self) -> str:
        '''
        We can have several versions to publish.
        - if we have one version: returned straight away
        - if we have more versions: split in commas and last with ampersand:
            - v1.0, v1.1 & v1.2
            - v1.1 & v1.2
        - if we have none: return False
        '''
        versions = [key for key in self._changes_stack.keys()]
        versions = sorted(versions, reverse=False)
        if len(versions) == 1:
            return versions[0]
        elif len(versions) > 1:
            all_but_last = versions[:-1]
            return ", ".join(all_but_last) + " & " + versions[-1]
    
    def __get_changelog_content(self) -> str:
        changelog_filename = os.path.join(
            self._repo_object.working_tree_dir, self._repo_info.get("params.file")
        )

        if os.path.isfile(changelog_filename):
            with open(changelog_filename, 'r') as file:
                content = file.read()
                return content
        else:
            raise RuntimeError("File not found in the repository")

    def __extract_version_from_section(self, section: str) -> str:
        regex = self._repo_info.get("params.version_regex", DEFAULT_VERSION_REGEX)
        matched = re.search(regex, section)
        if matched is None:
            return None
        return matched.group(1)

    def __parse_changelog(self, content: str) -> dict:
        version_section_separator = self._repo_info.get(
            "params.section_separator", DEFAULT_SECTION_SEPARATOR
        )

        last_known_version = self.get_current_last_known()
        versions_to_ignore = self._repo_info.get("params.version_exceptions", [])

        self._logger.debug(f"Last known version: {last_known_version}")
        self._logger.debug(f"Will ignore the versions: {', '.join(versions_to_ignore)}")

        sections = content.split(version_section_separator)
        # Discarding position 0, it's the title and won't match the version cleaner.
        sections = sections[1:]
        self._logger.debug(f"Found {len(sections)} sections")

        # Classify the content by version.
        # We already have the last known version, so stop when appears.
        sections_by_version = {}
        for section in sections:
            version = self.__extract_version_from_section(section)
            if version is None:
                raise RuntimeError("I could not get a version from this section")
            if version in versions_to_ignore:
                self._logger.debug(f"Found version {version} is meant to be ignored")
                continue
            if version == last_known_version:
                self._logger.debug(
                    f"Found version {version} is the same as " + "last known. Stopping here."
                )
                break
            self._logger.debug(f"Found version {version}, kept in parsed sections.")
            sections_by_version[version] = section

        return sections_by_version
    
    def _clean_markdown(self, text: str) -> str:
        '''
        Markdown is not fully supported. We need to do some transforming
        '''

        text = re.sub(r"###\s{1}([a-zA-Z]+)\n", r"**\1**", text)

        return text

class CommitsChanges(BaseChanges):

    STORAGE_PARAMETER_NAME = "last_commit"

    def discover_changes(self, parameters: dict = None) -> None:
        last_known_commit = self.get_current_last_known()
        if last_known_commit is None:
            commits = list(self._repo_object.iter_commits())
        else:
            git_rev_list_limits = f"{last_known_commit}..HEAD"
            commits = list(self._repo_object.iter_commits(rev=git_rev_list_limits))
        
        self._changes_stack = {}
        for c in commits:
            self._changes_stack[c.binsha.hex()] = {
                "author": str(c.author),
                "message": c.message.replace("\n", " ")
            }
    
    def get_current_last_known(self) -> str:
        return self._storage.get(
            self._get_param_name(self.STORAGE_PARAMETER_NAME), None
        )
    
    def build_update_message(self, parameters: dict = None) -> Message:
       return Message(
            text=Template(TEMPLATE_UPDATE_TEXT).substitute(
                project=self._repo_info.get("name"),
                link=self._repo_info.get("url"),
                version=self.get_changes_note(),
                text="\n".
                join([f"- *{c['author']}*: {c['message']}" for c in self._changes_stack.values()]),
                tags=" ".join(self._repo_info.get("tags", ""))
            )
        )
    
    def write_new_last_known(self, value: str) -> None:
        self._storage.set(self._get_param_name(self.STORAGE_PARAMETER_NAME), value)
        self._storage.write_file()
    
    def get_changes_note(self) -> str:
        return f"{len(self._changes_stack)} new commits"

class GitMonitor:

    repository_info: Dictionary
    current_repository: Repo
    changes_instance: ChangesProtocol = None

    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
        self._storage = Storage(self._config.get("git_monitor.file", DEFAULT_FILENAME))

    def initiate_or_clone_repository(self, repository_info: Dictionary) -> Repo:
        # Checking for mandatory parameters
        if repository_info.get("path", None) is None\
            and (repository_info.get("git", None) is None\
                 or repository_info.get("path", None) is None):
            raise RuntimeError(
                "Mandatory parameters [path] or [git] and [path] are not present"
            )

        if os.path.exists(repository_info.get("path")):
            self._logger.debug(f"Initializing repo {repository_info.get('name')}")
            self.current_repository = Repo.init(repository_info.get("path"))
        else:
            self._logger.debug(f"Cloning repo {repository_info.get('name')}")
            self.current_repository = Repo.clone_from(
                repository_info.get("git"), repository_info.get("path")
            )

        self.repository_info = repository_info
        return self.current_repository

    def get_updates(self):
        self._logger.debug(f"Getting updates for repo {self.repository_info.get('name')}")
        origin = self.current_repository.remotes.origin
        origin.pull()
    
    def get_changes_instance(self) -> ChangesProtocol:

        if self.changes_instance is None:
            monitoring_method = self.repository_info.get("monitoring_method", DEFAULT_MONITORING_METHOD)
            
            if monitoring_method == "changelog":
                self.changes_instance = ChangelogChanges(
                    config=self._config,
                    logger=self._logger,
                    repository_info=self.repository_info,
                    repository_object=self.current_repository
                )
            elif monitoring_method == "commits":
                self.changes_instance = CommitsChanges(
                    config=self._config,
                    logger=self._logger,
                    repository_info=self.repository_info,
                    repository_object=self.current_repository
                )
            else:
                raise RuntimeError(
                    f"The repository {self.repository_info.get('name')} does not have " +
                    "a valid monitoring set up."
                )
        
        return self.changes_instance
    
    def get_current_last_known(self) -> str:
        return self.get_changes_instance().get_current_last_known()
    
    def get_new_last_known(self) -> str:
        return self.get_changes_instance().get_new_last_known()
    
    def get_update_message(self, parameters: dict = None) -> Message:
        return self.get_changes_instance().build_update_message(parameters=parameters)
    
    def get_changes_note(self)-> str:
        return self.get_changes_instance().get_changes_note()
    
    def write_new_last_known(self, value: str) -> None:
        return self.get_changes_instance().write_new_last_known(value=value)
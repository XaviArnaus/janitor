from pyxavi.config import Config
from pyxavi.storage import Storage
from janitor.objects.message import Message
from git import Repo
from string import Template
from slugify import slugify
import logging
import os
import re
from pyxavi.debugger import dd

DEFAULT_FILENAME = "storage/git_monitor.yaml"
DEFAULT_VERSION_REGEX = "\[(v[0-9]+\.[0-9]+\.[0-9]+)\]"
DEFAULT_SECTION_SEPARATOR = "\n## "
TEMPLATE_UPDATE_TEXT = "**[$project]($link) $version** published!\n\n$text\n$tags\n"

class GitMonitor:

    repository_info: dict
    current_repository: Repo
    parsed_changelog_per_version: dict

    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
        self._storage = Storage(self._config.get("git_monitor.file", DEFAULT_FILENAME))
    
    def initiate_or_clone_repository(self, repository: dict) -> Repo:
        # Checking for mandatory parameters
        if "path" not in repository\
            or repository["path"] is None\
            or "git" not in repository\
            or repository["git"] is None:
            raise RuntimeError("Mandatory parameters [path] and [git] are not present")

        if os.path.exists(repository["path"]):
            self.current_repository = Repo.init(repository["path"])
        else:
            self.current_repository = Repo.clone_from(repository["git"], repository["path"])

        self.repository_info = repository
        return self.current_repository
    
    def get_updates(self):
        origin = self.current_repository.remotes.origin
        origin.pull()
    
    def get_changelog_content(self) -> str:
        changelog_filename = os.path.join(
            self.current_repository.working_tree_dir,
            self.repository_info["changelog"]["file"]
        )

        if os.path.isfile(changelog_filename):
            with open(changelog_filename, 'r') as file:
                content = file.read()
                return content
        else:
            raise RuntimeError("File not found in the repository")
    
    def __extract_version_from_section(self, section: str) -> str:
        regex = self.repository_info["changelog"]["version_regex"] or DEFAULT_VERSION_REGEX
        matched = re.search(regex, section)
        return matched.group(1)
    
    def __get_param_name(self, param_name: str) -> str:
        current_repo_id = slugify(self.repository_info["git"])
        current_value = self._storage.get(current_repo_id, {})
        self._storage.set(current_repo_id, current_value)
        return f"{current_repo_id}.{param_name}"
    
    def parse_changelog(self, content: str) -> dict:
        version_section_separator = self.repository_info["changelog"]["section_separator"] or DEFAULT_SECTION_SEPARATOR
        last_version_param_name = self.__get_param_name("last_version")
        last_known_version = self._storage.get(last_version_param_name, None)

        sections = content.split(version_section_separator)
        #Discarding position 0, it's the title and won't match the version cleaner.
        sections = sections[1:]

        # If we don't have a last version, we won't publish anything
        if last_known_version is None:
            # Then just take the first item, store the version and leave
            # Remember, Changelog is listing the versions the newer first.
            version_to_store = self.__extract_version_from_section(section=sections[0])
            if version_to_store is None:
                raise RuntimeError("I could not get a version from this section")
            else:
                self._storage.set(last_version_param_name, version_to_store)
                self._storage.write_file()
                return {}

        # Classify the content by version.
        # We already have the last known version, so stop when appears.
        sections_by_version = {}
        for section in sections:
            version = self.__extract_version_from_section(section)
            if version == last_known_version:
                break
            sections_by_version[version] = section
        
        return sections_by_version

    def build_update_message(self, parsed_content: dict) -> Message:
        prepared_version_string = self.prepare_versions(parsed_content=parsed_content)
        if prepared_version_string is False:
            # This means that we don't have any version to publish
            return None
        
        return Message(
            text=Template(TEMPLATE_UPDATE_TEXT).substitute(
                project = self.repository_info["name"],
                link = self.repository_info["url"],
                version = prepared_version_string,
                text = "\n".join(
                    [self._clean_markdown(text) for text in parsed_content.values()]
                ),
                tags = " ".join(self.repository_info["tags"]) if "tags" in self.repository_info else ""
            )
        )
    
    def store_last_known_version(self, last_known_version: str) -> None:
        self._storage.set(self.__get_param_name("last_version"), last_known_version)
        self._storage.write_file()
    
    def _clean_markdown(self, text: str) -> str:
        '''
        Markdown is not fully supported. We need to do some transforming
        '''

        text = re.sub(
            "###\s{1}([a-zA-Z]+)\n",
            r"**\1**",
            text
        )

        return text
    
    def prepare_versions(self, parsed_content: dict) -> str:
        '''
        We can have several versions to publish.
        - if we have one version: returned straight away
        - if we have more versions: split in commas and last with ampersand:
            - v1.0, v1.1 & v1.2
            - v1.1 & v1.2
        - if we have nonw: return False
        '''
        versions = [key for key in parsed_content.keys()]
        versions.reverse()
        if len(versions) == 1:
            return versions[0]
        elif len(versions) > 1:
            all_but_last  = versions[:-1]
            return ", ".join(all_but_last) + " & " + versions[-1]
        else:
            return False
        

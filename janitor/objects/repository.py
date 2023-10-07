from __future__ import annotations

class Changelog:
    file: str
    

class Repository:
    name: str
    url: str
    git: str
    path: str
    changelog: str

    def __init__(
        self,
        name: str = None,
        url: str = None,
        git: str = None,
        path: str = None,
        changelog: str = None
        ) -> None:

        self.name = name
        self.url = url
        self.git = git
        self.path = path
        self.changelog = changelog

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "git": self.git,
            "path": self.path,
            "changelog": self.changelog,
        }

    @staticmethod
    def from_dict(repository_dict: dict) -> Repository:
        return Repository(
            name = repository_dict["name"] if "name" in repository_dict else None,
            url = repository_dict["url"] if "url" in repository_dict else None,
            git = repository_dict["git"] if "git" in repository_dict else None,
            path = repository_dict["path"] if "path" in repository_dict else None,
            changelog = repository_dict["changelog"] if "changelog" in repository_dict else None
        )
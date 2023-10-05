from pyxavi.config import Config
from janitor.objects.repository import Repository
from git import Repo
import logging
import os

class GitMonitor:

    current_repository: Repo

    def __init__(self, config: Config) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
    
    def initiate_or_clone_repository(self, repository: Repository) -> Repo:
        if os.path.exists(repository.path):
            self.current_repository = Repo.init(repository.path)
        else:
            self.current_repository = Repo.clone_from(repository.git, repository.path)
    
    def get_updates(self):
        origin = self.current_repository.remotes.origin
        origin.pull()
        

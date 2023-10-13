from pyxavi.config import Config
from pyxavi.storage import Storage
from janitor.objects.queue_item import QueueItem
import logging
import os


class Queue:

    _queue = []

    def __init__(self, config: Config, base_path: str = None) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
        file_name = self._config.get("queue_storage.file")
        if base_path is not None:
            file_name = os.path.join(base_path, file_name)
        self._queue_manager = Storage(filename=file_name)
        self._queue = list(
            map(lambda x: QueueItem.from_dict(x), self._queue_manager.get("queue", []))
        )

    def append(self, item: QueueItem) -> None:
        self._queue.append(item)

    def sort_by_date(self) -> None:
        self._logger.debug("Sorting queue by date ASC")
        self._queue = sorted(self._queue, key=lambda x: x.published_at)

    def deduplicate(self) -> None:
        self._logger.debug("Deduplicating queue")
        new_queue = []
        [new_queue.append(x) for x in self._queue if x not in new_queue]
        self._queue = new_queue

    def save(self) -> None:
        self._logger.debug("Saving the queue")
        self._queue_manager.set("queue", list(map(lambda x: x.to_dict(), self._queue)))
        self._queue_manager.write_file()

    def update(self) -> None:
        self.sort_by_date()
        self.deduplicate()
        self.save()

    def is_empty(self) -> bool:
        return False if self._queue else True

    def get_all(self) -> list:
        return self._queue

    def clean(self) -> None:
        self._queue = []

    def pop(self) -> dict:
        if not self.is_empty():
            if not self._config.get("app.run_control.dry_run"):
                return self._queue.pop(0)
            else:
                return self._queue[0]
        else:
            return None

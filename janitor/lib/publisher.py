from pyxavi.config import Config
from pyxavi.logger import Logger
from pyxavi.terminal_color import TerminalColor
from pyxavi.mastodon_publisher import MastodonPublisher, MastodonPublisherException
from pyxavi.item_queue import Queue
from janitor.objects.queue_item import QueueItem
from janitor.objects.message import Message, MessageType
from .formatter import Formatter
import os


class Publisher(MastodonPublisher):
    '''
    Publisher

    It is responsible to publish the queued status posts.
    '''

    MAX_RETRIES = 3
    SLEEP_TIME = 10
    DEFAULT_QUEUE_FILE = "storage/queue.yaml"

    def __init__(
        self,
        config: Config,
        named_account: str = "default",
        base_path: str = None,
        only_oldest: bool = None
    ) -> None:
        
        logger = Logger(config=config).get_logger()

        super().__init__(
            config=config,
            logger=logger,
            named_account=named_account,
            base_path=base_path
        )

        queue_storage_file = config.get("queue_storage.file", self.DEFAULT_QUEUE_FILE)
        if base_path is not None:
            queue_storage_file = os.path.join(base_path, queue_storage_file) 
        self._queue = Queue(logger=logger, storage_file=queue_storage_file, queue_item_object=QueueItem)
        self._formatter = Formatter(config, self._connection_params.status_params)
        # Janitor has the dry_run set up somewhere else. Overwriting.
        self._is_dry_run = config.get("app.run_control.dry_run", False)
        self._only_oldest = only_oldest if only_oldest is not None\
            else config.get("publisher.only_oldest_post_every_iteration", False)

    def text(self, content: str, summary: str = None, requeue_if_fails: bool = False) -> dict:
        """
        Shorthand to publish a message with MessageType.NONE
        """
        return self.publish_message(
            message=Message(summary=summary, text=content, message_type=MessageType.NONE),
            requeue_if_fails=requeue_if_fails
        )

    def info(self, content: str, summary: str = None, requeue_if_fails: bool = False) -> dict:
        """
        Shorthand to publish a message with MessageType.INFO
        """
        return self.publish_message(
            message=Message(summary=summary, text=content, message_type=MessageType.INFO),
            requeue_if_fails=requeue_if_fails
        )

    def warning(
        self, content: str, summary: str = None, requeue_if_fails: bool = False
    ) -> dict:
        """
        Shorthand to publish a message with MessageType.WARNING
        """
        return self.publish_message(
            message=Message(summary=summary, text=content, message_type=MessageType.WARNING),
            requeue_if_fails=requeue_if_fails
        )

    def error(self, content: str, summary: str = None, requeue_if_fails: bool = False) -> dict:
        """
        Shorthand to publish a message with MessageType.ERROR
        """
        return self.publish_message(
            message=Message(summary=summary, text=content, message_type=MessageType.ERROR),
            requeue_if_fails=requeue_if_fails
        )

    def alarm(self, content: str, summary: str = None, requeue_if_fails: bool = False) -> dict:
        """
        Shorthand to publish a message with MessageType.ALARM
        """
        return self.publish_message(
            message=Message(summary=summary, text=content, message_type=MessageType.ALARM),
            requeue_if_fails=requeue_if_fails
        )

    def publish_queue_item(self, item: QueueItem) -> dict:
        """
        Publishes a received QueueItem

        This is a simple proxy method to publish_message
        """
        return self.publish_message(message=item.message)

    def publish_message(self, message: Message, requeue_if_fails: bool = False) -> dict:
        """
        Publishes a given Message object

        - Translates to a StatusPost object using the Formatter class.
        - It captures PublisherException errors thrown from publish_status_post
            when max retries is reached. with `requeue_if_fails` the failed message
            moves to the beginning of the queue, but the queue is not cared: you need
            to process it from another endpoint.
        - It delegates to publish_status_post for proper publishing
        """

        status_post = self._formatter.build_status_post(message=message)
        try:
            return self.publish_status_post(status_post=status_post)
        except MastodonPublisherException as e:
            self._logger.error(e)

            if requeue_if_fails:
                queue_item = QueueItem(message=message)
                self._queue.unpop(queue_item)
                if self._is_dry_run:
                    self._queue.save()

    def reload_queue(self) -> int:
        # Previous length
        previous = self._queue.length()
        self._queue.load()
        new = self._queue.length()

        return new - previous

    def publish_all_from_queue(self) -> None:
        if self._queue.is_empty():
            self._logger.info(
                f"{TerminalColor.CYAN}The queue is empty, skipping.{TerminalColor.END}"
            )
            return

        while not self._queue.is_empty():
            # Get the first element from the queue
            queued_post = self._queue.pop()
            # Publish it
            self.publish_queue_item(queued_post)
            # Do we want to publish only the oldest in every iteration?
            #   This means that the queue gets empty one item every run
            if self._only_oldest:
                self._logger.info(
                    f"{TerminalColor.CYAN}We're meant to publish only the oldest." +
                    f" Finishing.{TerminalColor.END}"
                )
                break

        if not self._is_dry_run:
            self._queue.save()

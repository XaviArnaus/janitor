from pyxavi.config import Config
from pyxavi.media import Media
from janitor.objects.queue_item import QueueItem
from janitor.objects.status_post import StatusPost
from janitor.objects.message import Message
from .queue import Queue
from .formatter import Formatter
from mastodon import Mastodon
from .mastodon_helper import MastodonHelper
from janitor.objects.mastodon_connection_params import MastodonConnectionParams
import logging
import time


class Publisher:
    '''
    Publisher

    It is responsible to publish the queued status posts.
    '''

    MAX_RETRIES = 3
    SLEEP_TIME = 10

    def __init__(
        self,
        config: Config,
        mastodon: Mastodon,
        connection_params: MastodonConnectionParams,
        base_path: str = None
    ) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
        self._queue = Queue(config, base_path=base_path)
        self._mastodon = mastodon
        self._connection_params = connection_params
        self._formatter = Formatter(config, connection_params.status_params)
        self._is_dry_run = config.get("app.run_control.dry_run", False)
        self._instance_type = MastodonHelper.valid_or_raise(
            self._connection_params.instance_type
        )
        self._only_oldest = config.get("publisher.only_oldest_post_every_iteration", False)
        self._media_storage = self._config.get("publisher.media_storage")

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
        except PublisherException as e:
            self._logger.error(e)

            if requeue_if_fails:
                queue_item = QueueItem(message=message)
                self._queue.unpop(queue_item)
                if self._is_dry_run:
                    self._queue.save()

    def _post_media(self, media_file: str, description: str) -> dict:
        try:
            downloaded = Media().download_from_url(media_file, self._media_storage)
            return self._mastodon.media_post(
                downloaded["file"], mime_type=downloaded["mime_type"], description=description
            )
        except Exception as e:
            self._logger.exception(e)

    def publish_all_from_queue(self) -> None:
        if self._queue.is_empty():
            self._logger.info("The queue is empty, skipping.")
            return

        while not self._queue.is_empty():
            # Get the first element from the queue
            queued_post = self._queue.pop()
            # Publish it
            self.publish_queue_item(queued_post)
            # Do we want to publish only the oldest in every iteration?
            #   This means that the queue gets empty one item every run
            if self._only_oldest:
                self._logger.info("We're meant to publish only the oldest. Finishing.")
                break

        if not self._is_dry_run:
            self._queue.save()

    def publish_status_post(self, status_post: StatusPost) -> dict:
        if self._is_dry_run:
            self._logger.debug("It's a Dry Run, stopping here.")
            return None

        # posted_media = []
        # if "media" in item and item["media"]:
        #     self._logger.info("Publising first %s media items", len(item["media"]))
        #     for item in item["media"]:
        #         posted_result = self._post_media(
        #             item["url"],
        #             description=item["alt_text"] if "alt_text" in item else None
        #         )
        #         if posted_result:
        #             posted_media.append(posted_result["id"])
        #         else:
        #             self._logger.info("Could not publish %s", item["url"])

        # Let's ensure that it fits according to the params
        status_post.status = self.__slice_status_if_longer_than_defined(
            status=status_post.status
        )

        retry = 0
        published = None
        while published is None:
            try:
                self._logger.info(
                    f"Publishing new post (retry: {retry}) for " +
                    f"instance type {self._instance_type}"
                )
                return self._do_status_publish(status_post=status_post)
            except Exception as e:
                self._logger.exception(e)
                self._logger.debug(f"sleeping {self.SLEEP_TIME} seconds")
                time.sleep(self.SLEEP_TIME)
                retry += 1
                if retry >= self.MAX_RETRIES:
                    self._logger.error(
                        f"MAX RETRIES of {self.MAX_RETRIES} is reached. Stop trying."
                    )
                    raise PublisherException(f"Could not publish the post: {e}")

    def _do_status_publish(self, status_post: StatusPost) -> dict:
        """
        This is the method that executes the post of the status.

        No checks, no validations, just the action.
        """

        if self._instance_type == MastodonHelper.TYPE_MASTODON:
            published = self._mastodon.status_post(
                status=status_post.status,
                in_reply_to_id=status_post.in_reply_to_id,
                media_ids=status_post.media_ids,
                sensitive=status_post.sensitive,
                visibility=status_post.visibility,
                spoiler_text=status_post.spoiler_text,
                language=status_post.language,
                idempotency_key=status_post.idempotency_key,
                scheduled_at=status_post.scheduled_at,
                poll=status_post.poll,
                # media_ids=posted_media if posted_media else None # yapf: disable
            )
        elif self._instance_type == MastodonHelper.TYPE_PLEROMA:
            published = self._mastodon.status_post(
                status=status_post.status,
                in_reply_to_id=status_post.in_reply_to_id,
                media_ids=status_post.media_ids,
                sensitive=status_post.sensitive,
                visibility=status_post.visibility,
                spoiler_text=status_post.spoiler_text,
                language=status_post.language,
                idempotency_key=status_post.idempotency_key,
                content_type=status_post.content_type,
                scheduled_at=status_post.scheduled_at,
                poll=status_post.poll,
                quote_id=status_post.quote_id,
                # media_ids=posted_media if posted_media else None # yapf: disable
            )
        elif self._instance_type == MastodonHelper.TYPE_FIREFISH:
            published = self._mastodon.status_post(
                status=status_post.status,
                in_reply_to_id=status_post.in_reply_to_id,
                media_ids=status_post.media_ids,
                sensitive=status_post.sensitive,
                visibility=status_post.visibility,
                spoiler_text=status_post.spoiler_text,
                language=status_post.language,
                idempotency_key=status_post.idempotency_key,
                content_type=status_post.content_type,
                scheduled_at=status_post.scheduled_at,
                poll=status_post.poll,
                quote_id=status_post.quote_id,
                # media_ids=posted_media if posted_media else None # yapf: disable
            )
        else:
            raise RuntimeError(f"Unknown instance type {self._instance_type}")
        return published

    def __slice_status_if_longer_than_defined(self, status: str) -> str:
        max_length = self._connection_params.status_params.max_length
        if len(status) > max_length:
            self._logger.info(
                f"The status post is longer than the max length of {max_length}. Cutting..."
            )
            status = status[:max_length - 3] + "..."

        return status


class PublisherException(BaseException):
    pass

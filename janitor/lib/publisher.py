from pyxavi.config import Config
from pyxavi.media import Media
from janitor.objects.queue_item import QueueItem
from .queue import Queue
from .formatter import Formatter
from mastodon import Mastodon
from .mastodon_helper import MastodonHelper
import logging


class Publisher:
    '''
    Publisher

    It is responsible to publish the queued status posts.
    '''

    DEFAULT_MAX_LENGTH = 500

    def __init__(self, config: Config, mastodon: Mastodon) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
        self._queue = Queue(config)
        self._formatter = Formatter(config)
        self._mastodon = mastodon

    def publish_one(self, item: QueueItem) -> dict:
        # Translate the Message to StatusPost
        status_post = self._formatter.build_status_post(item.message)

        # Publish the StatusPost
        if not self._config.get("app.run_control.dry_run"):
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
            instance_type = MastodonHelper.valid_or_raise(
                self._config.get("mastodon.instance_type", MastodonHelper.TYPE_MASTODON)
            )

            max_length = self._config.get(
                "mastodon.status_post.max_length", self.DEFAULT_MAX_LENGTH
            )
            if len(status_post.status) > max_length:
                self._logger.info(
                    f"The status post is longer than the max length of {max_length}. Cutting..."
                )
                status_post.status = status_post.status[:max_length - 3] + "..."

            if instance_type == MastodonHelper.TYPE_MASTODON:
                self._logger.info("Publishing new post for Mastodon instance type")
                return self._mastodon.status_post(
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
            elif instance_type == MastodonHelper.TYPE_PLEROMA:
                self._logger.info("Publishing new post for Pleroma instance type")
                return self._mastodon.status_post(
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

    def _post_media(self, media_file: str, description: str) -> dict:
        try:
            downloaded = Media().download_from_url(
                media_file, self._config.get("publisher.media_storage")
            )
            return self._mastodon.media_post(
                downloaded["file"], mime_type=downloaded["mime_type"], description=description
            )
        except Exception as e:
            self._logger.exception(e)

    def publish_all_from_queue(self) -> None:
        if self._queue.is_empty():
            self._logger.info("The queue is empty, skipping.")
            return

        for queued_post in self._queue.get_all():
            self.publish_one(queued_post)

        self._logger.info("Cleaning stored queue")
        if not self._config.get("app.run_control.dry_run"):
            self._queue.clean()
            self._queue.save()

    def publish_older_from_queue(self) -> None:
        if self._queue.is_empty():
            self._logger.info("The queue is empty, skipping.")
            return

        self.publish_one(self._queue.pop())

        if not self._config.get("app.run_control.dry_run"):
            self._queue.save()

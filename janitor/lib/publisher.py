from pyxavi.config import Config
from pyxavi.media import Media
from janitor.objects.queue_item import QueueItem
from janitor.objects.status_post import StatusPost
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

    def publish_one(self, item: QueueItem) -> dict:
        # Translate the Message to StatusPost
        status_post = self._formatter.build_status_post(item.message)

        # Publish the StatusPost
        if self._config.get("app.run_control.dry_run"):
            self._logger.debug("It's a Dry Run, stopping here.")
        else:
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
            instance_type = MastodonHelper.valid_or_raise(self._connection_params.instance_type)
            self._logger.debug(f"Instance type is valid: {instance_type}")

            max_length = self._connection_params.status_params.max_length
            if len(status_post.status) > max_length:
                self._logger.info(
                    f"The status post is longer than the max length of {max_length}. Cutting..."
                )
                status_post.status = status_post.status[:max_length - 3] + "..."

            retry = 0
            published = None
            while published is None:
                try:
                    self._logger.info(
                        f"Publishing new post (retry: {retry}) for " +
                        f"instance type {instance_type}"
                    )
                    return self._do_status_post(
                        status_post=status_post, instance_type=instance_type
                    )
                except Exception as e:
                    self._logger.exception(e)
                    self._logger.debug(f"sleeping {self.SLEEP_TIME} seconds")
                    time.sleep(self.SLEEP_TIME)
                    retry += 1
                    if retry >= self.MAX_RETRIES:
                        self._logger.error(
                            f"MAX RETRIES of {self.MAX_RETRIES} is reached. Stop trying."
                        )
                        raise ConnectionError(f"Could not publish the post: {e}")

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

        while not self._queue.is_empty():
            queued_post = self._queue.pop()
            self.publish_one(queued_post)

        if not self._config.get("app.run_control.dry_run"):
            self._queue.save()

    def publish_older_from_queue(self) -> None:
        if self._queue.is_empty():
            self._logger.info("The queue is empty, skipping.")
            return

        self.publish_one(self._queue.pop())

        if not self._config.get("app.run_control.dry_run"):
            self._queue.save()
    
    def _do_status_post(self, status_post: StatusPost, instance_type: str = None) -> dict:
        """
        This is the method that executes the post of the status.

        No checks, no validations, just the action.
        """
        if instance_type is None:
            instance_type = MastodonHelper.TYPE_MASTODON

        if instance_type == MastodonHelper.TYPE_MASTODON:
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
        elif instance_type == MastodonHelper.TYPE_PLEROMA:
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
        elif instance_type == MastodonHelper.TYPE_FIREFISH:
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
        return published
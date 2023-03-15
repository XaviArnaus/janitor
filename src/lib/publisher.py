from pyxavi.config import Config
from pyxavi.media import Media
from ..objects.queue_item import QueueItem
from .queue import Queue
from .formater import Formater
# from mastodon import Mastodon 
from akkoma import Akkoma as Mastodon
import logging

class Publisher:
    '''
    Publisher

    It is responsible to publish the queued status posts.
    '''
    def __init__(self, config: Config, mastodon: Mastodon) -> None:
        self._config = config
        self._logger = logging.getLogger(config.get("logger.name"))
        self._queue = Queue(config)
        self._formater = Formater(config)
        self._mastodon = mastodon

    def publish_one(self, item: QueueItem) -> dict:
        # Translate the Message to StatusPost
        status_post = self._formater.build_status_post(item.message)

        # Publish the StatusPost
        if not self._config.get("run_control.dry_run"):
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
            self._logger.info("Publishing new post")
            return self._mastodon.status_post(
                status = status_post.status,
                in_reply_to_id = status_post.in_reply_to_id,
                media_ids = status_post.media_ids,
                sensitive = status_post.sensitive,
                visibility = status_post.visibility,
                spoiler_text = status_post.spoiler_text,
                language = status_post.language,
                idempotency_key = status_post.idempotency_key,
                content_type = status_post.content_type,
                scheduled_at = status_post.scheduled_at,
                poll = status_post.poll,
                quote_id = status_post.quote_id,
                # media_ids=posted_media if posted_media else None
            )
    
    def _post_media(self, media_file: str, description: str) -> dict:
        try:
            downloaded = Media().download_from_url(media_file, self._config.get("publisher.media_storage"))
            return self._mastodon.media_post(
                downloaded["file"],
                mime_type=downloaded["mime_type"],
                description=description
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
        if not self._config.get("run_control.dry_run"):
            self._queue.clean()
            self._queue.save()

    
    def publish_older_from_queue(self) -> None:
        if self._queue.is_empty():
            self._logger.info("The queue is empty, skipping.")
            return

        self.publish_one(self._queue.pop())

        if not self._config.get("run_control.dry_run"):
            self._queue.save()



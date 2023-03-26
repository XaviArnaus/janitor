from __future__ import annotations
from pyxavi.config import Config
from mastodon import Mastodon
import logging
import os


class MastodonHelper:

    TYPE_MASTODON = "mastodon"
    TYPE_PLEROMA = "pleroma"

    VALID_TYPES = [TYPE_MASTODON, TYPE_PLEROMA]

    FEATURE_SET_BY_INSTANCE_TYPE = {
        TYPE_MASTODON: "mainline",
        TYPE_PLEROMA: "pleroma"
    }

    def get_instance(config: Config) -> Mastodon:
        logger = logging.getLogger(config.get("logger.name"))
        instance_type = MastodonHelper.valid_or_raise(
            config.get("app.instance_type", MastodonHelper.TYPE_MASTODON)
        )

        # All actions are done under a Mastodon API instance
        logger.info("Starting new Mastodon API instance")
        if (os.path.exists(config.get("app.credentials.user_file"))):
            logger.debug("Reusing stored User Credentials")
            mastodon = Mastodon(
                access_token=config.get("app.credentials.user_file"),
                feature_set=MastodonHelper.FEATURE_SET_BY_INSTANCE_TYPE[instance_type]
            )
        else:
            logger.debug("Using Client Credentials")
            mastodon = Mastodon(
                client_id=config.get("app.credentials.client_file"),
                api_base_url=config.get("app.api_base_url"),
                feature_set=MastodonHelper.FEATURE_SET_BY_INSTANCE_TYPE[instance_type]
            )

            # Logging in is required for all individual runs
            logger.debug("Logging in")
            mastodon.log_in(
                config.get("app.credentials.user.email"),
                config.get("app.credentials.user.password"),
                to_file=config.get("app.credentials.user_file")
            )

        return mastodon

    def valid_or_raise(value: str) -> str:
        if value not in MastodonHelper.VALID_TYPES:
            raise RuntimeError(f"Value [{value}] is not a valid instance type")

        return value

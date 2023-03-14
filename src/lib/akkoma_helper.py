from pyxavi.config import Config
from akkoma import Akkoma
import logging
import os

class AkkomaHelper:
    def get_instance(config: Config) -> Akkoma:
        logger = logging.getLogger(config.get("logger.name"))

        # All actions are done under a Akkoma API instance
        logger.info("Starting new Akkoma API instance")
        if (os.path.exists(config.get("app.user_credentials"))):
            logger.debug("Reusing stored User Credentials")
            akkoma = Akkoma(
                access_token = config.get("app.user_credentials")
            )
        else:
            logger.debug("Using Client Credentials")
            akkoma = Akkoma(
                client_id = config.get("app.client_credentials"),
                api_base_url = config.get("app.api_base_url")
            )

            # Logging in is required for all individual runs
            logger.debug("Logging in")
            akkoma.log_in(
                grant_type = 'password',
                username = config.get("app.user.email"),
                password = config.get("app.user.password"),
                to_file = config.get("app.user_credentials")
            )

        return akkoma
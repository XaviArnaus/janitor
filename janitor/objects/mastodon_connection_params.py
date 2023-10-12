from __future__ import annotations


class MastodonConnectionParams():

    TYPE_MASTODON = "mastodon"
    TYPE_PLEROMA = "pleroma"
    TYPE_FIREFISH = "firefish"

    VALID_TYPES = [TYPE_MASTODON, TYPE_PLEROMA, TYPE_FIREFISH]

    instance_type: str
    api_base_url: str
    credentials: MastodonCredentials

    def __init__(
        self,
        instance_type: str = None,
        api_base_url: str = None,
        credentials: MastodonCredentials = None
    ) -> None:
        self.instance_type = instance_type if instance_type is not None else self.TYPE_MASTODON
        self.api_base_url = api_base_url
        self.credentials = credentials

    def to_dict(self) -> dict:
        return {
            "instance_type": self.instance_type,
            "api_base_url": self.api_base_url,
            "credentials": self.credentials.to_dict()
        }

    @staticmethod
    def from_dict(connection_params_dict: dict) -> MastodonConnectionParams:
        return MastodonConnectionParams(
            instance_type=connection_params_dict["instance_type"]
            if "instance_type" in connection_params_dict else None,
            api_base_url=connection_params_dict["api_base_url"]
            if "api_base_url" in connection_params_dict else None,
            credentials=MastodonCredentials.from_dict(connection_params_dict["credentials"])
            if "credentials" in connection_params_dict else None
        )


class MastodonCredentials():

    user_file: str
    client_file: str
    user: MastodonUser

    def __init__(
        self,
        user_file: str = None,
        client_file: str = None,
        user: MastodonUser = None
    ) -> None:
        self.user_file = user_file
        self.client_file = client_file
        self.user = user

    def to_dict(self) -> dict:
        return {
            "user_file": self.user_file,
            "client_file": self.client_file,
            "user": self.user.to_dict()
        }

    @staticmethod
    def from_dict(credentials_dict: dict) -> MastodonCredentials:
        return MastodonCredentials(
            user_file=credentials_dict["user_file"]
            if "user_file" in credentials_dict else None,
            client_file=credentials_dict["client_file"]
            if "client_file" in credentials_dict else None,
            user=MastodonUser.from_dict(credentials_dict["user"])
            if "user" in credentials_dict else None
        )


class MastodonUser():

    email: str
    password: str

    def __init__(self, email: str = None, password: str = None) -> None:
        self.email = email
        self.password = password

    def to_dict(self) -> dict:
        return {"email": self.email, "password": self.password}

    @staticmethod
    def from_dict(credentials_dict: dict) -> MastodonUser:
        return MastodonUser(
            email=credentials_dict["email"] if "email" in credentials_dict else None,
            password=credentials_dict["password"] if "password" in credentials_dict else None
        )

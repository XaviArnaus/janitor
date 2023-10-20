from janitor.objects.mastodon_connection_params import\
    MastodonConnectionParams, MastodonCredentials, MastodonUser, MastodonStatusParams
from janitor.objects.status_post import StatusPostContentType, StatusPostVisibility
from unittest import TestCase
import pytest


def test_instantiate_minimal():
    instance = MastodonConnectionParams()

    assert isinstance(instance, MastodonConnectionParams)


def test_to_dict_minimal():
    d = MastodonConnectionParams().to_dict()

    assert d["app_name"] is None
    assert d["instance_type"] == MastodonConnectionParams.TYPE_MASTODON
    assert d["api_base_url"] is None
    assert d["credentials"] is None
    assert isinstance(d["status_params"], dict)
    assert d["status_params"]["max_length"] == MastodonStatusParams.DEFAULT_MAX_LENGTH
    assert d["status_params"]["content_type"] == MastodonStatusParams.DEFAULT_CONTENT_TYPE
    assert d["status_params"]["visibility"] == MastodonStatusParams.DEFAULT_VISIBILITY
    assert d["status_params"]["username_to_dm"] is None


def test_from_dict_minimal():
    instance = MastodonConnectionParams.from_dict({})

    assert instance.app_name == None
    assert instance.instance_type == MastodonConnectionParams.TYPE_MASTODON
    assert instance.api_base_url is None
    assert instance.credentials is None
    assert isinstance(instance.status_params, MastodonStatusParams)
    assert instance.status_params.max_length == MastodonStatusParams.DEFAULT_MAX_LENGTH
    assert instance.status_params.content_type == MastodonStatusParams.DEFAULT_CONTENT_TYPE
    assert instance.status_params.visibility == MastodonStatusParams.DEFAULT_VISIBILITY
    assert instance.status_params.username_to_dm is None


def test_instantiate_with_app_name():
    test_app_name = "hola"
    instance = MastodonConnectionParams(app_name=test_app_name)

    assert instance.app_name == test_app_name


def test_instantiate_with_instance_type():
    instance = MastodonConnectionParams(instance_type=MastodonConnectionParams.TYPE_FIREFISH)

    assert instance.instance_type == MastodonConnectionParams.TYPE_FIREFISH


def test_instantiate_without_instace_type_defers_to_mastodon():
    instance = MastodonConnectionParams()

    assert instance.instance_type == MastodonConnectionParams.TYPE_MASTODON


def test_instantiate_with_api_base_url():
    test_api_base_url = "https://talamanca.social"

    instance = MastodonConnectionParams(api_base_url=test_api_base_url)

    assert instance.api_base_url == test_api_base_url


def test_instantiate_with_credentials_defaults():
    test_credentials = MastodonCredentials()
    assert isinstance(test_credentials, MastodonCredentials)

    instance = MastodonConnectionParams(credentials=test_credentials)

    assert instance.credentials == test_credentials
    assert instance.credentials.client_file == MastodonCredentials.DEFAULT_CLIENT_FILE
    assert instance.credentials.user_file == MastodonCredentials.DEFAULT_USER_FILE
    assert instance.credentials.user is None


def test_instantiate_with_credentials_values():
    test_client_file = "aaa"
    test_user_file = "bbb"
    test_credentials = MastodonCredentials.from_dict(
        {
            "client_file": test_client_file, "user_file": test_user_file
        }
    )
    assert isinstance(test_credentials, MastodonCredentials)

    instance = MastodonConnectionParams(credentials=test_credentials)

    assert instance.credentials == test_credentials
    assert instance.credentials.client_file == test_client_file
    assert instance.credentials.user_file == test_user_file
    assert instance.credentials.user is None

    d = instance.credentials.to_dict()
    assert d["client_file"] == test_client_file
    assert d["user_file"] == test_user_file
    assert d["user"] is None


def test_instantiate_with_credentials_and_user_values():
    test_user_email = "xavi@talamanca"
    test_user_password = "pass"
    test_credentials = MastodonCredentials.from_dict(
        {"user": {
            "email": test_user_email, "password": test_user_password
        }}
    )
    assert isinstance(test_credentials, MastodonCredentials)
    assert isinstance(test_credentials.user, MastodonUser)

    instance = MastodonConnectionParams(credentials=test_credentials)

    assert instance.credentials == test_credentials
    assert instance.credentials.client_file == MastodonCredentials.DEFAULT_CLIENT_FILE
    assert instance.credentials.user_file == MastodonCredentials.DEFAULT_USER_FILE
    assert instance.credentials.user.email == test_user_email
    assert instance.credentials.user.password == test_user_password

    d = instance.credentials.to_dict()
    assert d["user"]["email"] == test_user_email
    assert d["user"]["password"] == test_user_password


@pytest.mark.parametrize(
    argnames=(
        'max_length',
        'content_type',
        'visibility',
        'username_to_dm',
        'expected_length',
        'expected_content_type',
        'expected_visibility',
        'expected_username_to_dm',
        'expected_exception'
    ),
    argvalues=[
        (
            None,
            None,
            None,
            None,
            MastodonStatusParams.DEFAULT_MAX_LENGTH,
            MastodonStatusParams.DEFAULT_CONTENT_TYPE,
            MastodonStatusParams.DEFAULT_VISIBILITY,
            None,
            False
        ),
        (
            400,
            None,
            None,
            None,
            400,
            MastodonStatusParams.DEFAULT_CONTENT_TYPE,
            MastodonStatusParams.DEFAULT_VISIBILITY,
            None,
            False
        ),
        (
            None,
            StatusPostContentType.MARKDOWN,
            None,
            None,
            MastodonStatusParams.DEFAULT_MAX_LENGTH,
            StatusPostContentType.MARKDOWN,
            MastodonStatusParams.DEFAULT_VISIBILITY,
            None,
            False
        ),
        (
            None,
            "handwritten",
            None,
            None,
            MastodonStatusParams.DEFAULT_MAX_LENGTH,
            None,
            MastodonStatusParams.DEFAULT_VISIBILITY,
            None, (StatusPostContentType, RuntimeError)
        ),
        (
            None,
            None,
            StatusPostVisibility.PRIVATE,
            None,
            MastodonStatusParams.DEFAULT_MAX_LENGTH,
            MastodonStatusParams.DEFAULT_CONTENT_TYPE,
            StatusPostVisibility.PRIVATE,
            None,
            False
        ),
        (
            None,
            None,
            "invisible",
            None,
            MastodonStatusParams.DEFAULT_MAX_LENGTH,
            MastodonStatusParams.DEFAULT_CONTENT_TYPE,
            None,
            None, (StatusPostVisibility, RuntimeError)
        ),
        (
            None,
            None,
            StatusPostVisibility.DIRECT,
            None,
            MastodonStatusParams.DEFAULT_MAX_LENGTH,
            MastodonStatusParams.DEFAULT_CONTENT_TYPE,
            None,
            None, (MastodonStatusParams, ValueError)
        ),
        (
            None,
            None,
            StatusPostVisibility.DIRECT,
            "@user",
            MastodonStatusParams.DEFAULT_MAX_LENGTH,
            MastodonStatusParams.DEFAULT_CONTENT_TYPE,
            StatusPostVisibility.DIRECT,
            "@user",
            False
        ),
    ],
)
def test_instantiate_with_status_post_with_values(
    max_length,
    content_type,
    visibility,
    username_to_dm,
    expected_length,
    expected_content_type,
    expected_visibility,
    expected_username_to_dm,
    expected_exception
):
    if expected_exception:
        who, what = expected_exception
        with TestCase.assertRaises(who, what):
            _ = MastodonStatusParams(
                max_length=max_length,
                content_type=content_type,
                visibility=visibility,
                username_to_dm=username_to_dm
            )
    else:
        status_params = MastodonStatusParams(
            max_length=max_length,
            content_type=content_type,
            visibility=visibility,
            username_to_dm=username_to_dm
        )

        assert status_params.max_length == expected_length
        assert status_params.content_type == expected_content_type
        assert status_params.visibility == expected_visibility
        assert status_params.username_to_dm == expected_username_to_dm

        instance = MastodonConnectionParams.from_dict(
            {
                "status_params": {
                    "max_length": max_length,
                    "content_type": content_type,
                    "visibility": visibility,
                    "username_to_dm": username_to_dm,
                }
            }
        )

        assert instance.status_params.max_length == expected_length
        assert instance.status_params.content_type == expected_content_type
        assert instance.status_params.visibility == expected_visibility
        assert instance.status_params.username_to_dm == expected_username_to_dm

        d = instance.to_dict()

        assert d["status_params"]["max_length"] == expected_length
        assert d["status_params"]["content_type"] == expected_content_type
        assert d["status_params"]["visibility"] == expected_visibility
        assert d["status_params"]["username_to_dm"] == expected_username_to_dm

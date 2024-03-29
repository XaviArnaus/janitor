from pyxavi.terminal_color import TerminalColor
from pyxavi.config import Config
from janitor.lib.system_info import SystemInfo
from janitor.lib.system_info_templater import SystemInfoTemplater
from janitor.lib.publisher import Publisher
from janitor.objects.message import Message, MessageType
from janitor.runners.runner_protocol import RunnerProtocol
from definitions import ROOT_DIR
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import logging

app = Flask(__name__)
api = Api(app)

DEFAULT_MESSAGE_TYPE = str(MessageType.NONE)
MASTODON_NAMED_ACCOUNT = "default"
# MASTODON_NAMED_ACCOUNT = "test"


class Listen(RunnerProtocol):

    def __init__(
        self, config: Config = None, logger: logging = None, params: dict = None
    ) -> None:
        self._config = config
        self._logger = logger

        # Make that Flask only logs from Warning on:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

    def run(self):
        api.add_resource(
            ListenSysInfo,
            '/sysinfo',
            resource_class_kwargs={
                "config": self._config, "logger": self._logger
            }
        )
        api.add_resource(
            ListenMessage,
            '/message',
            resource_class_kwargs={
                "config": self._config, "logger": self._logger
            }
        )

        app.run(
            debug=self._config.get("app.service.listen.debug"),
            host=self._config.get("app.service.listen.host"),
            port=self._config.get("app.service.listen.port")
        )


class ListenSysInfo(Resource):
    '''
    Listener from remote SysInfo Report requests to log
    '''

    def __init__(self, config: Config = None, logger: logging = None) -> None:
        self._config = config
        self._logger = logger
        self._current_flask_app = app
        self._sys_info = SystemInfo(self._config)
        self._parser = reqparse.RequestParser()
        self._parser.add_argument(
            'sys_data', type=dict, required=True, help='No sys_data provided', location='json'
        )

        super(ListenSysInfo, self).__init__()

    def post(self):
        """
        This is going to receive the POST request
        """

        self._logger.info(
            f"{TerminalColor.MAGENTA}System Info Listener{TerminalColor.END}" +
            f" received a request from {request.remote_addr}"
        )

        # Get the data
        args = self._parser.parse_args()
        if "sys_data" in args:
            sys_data = args["sys_data"]
        else:
            return {
                "error": "Expected dict under a \"sys_data\" variable was not present."
            }, 400

        # If there is no issue, just stop here.
        if not self._sys_info.crossed_thresholds(sys_data, ["hostname"]):
            self._logger.info(
                f"{TerminalColor.CYAN}No issues found. Ending here.{TerminalColor.END}"
            )
            return 200

        # Make it a message
        message = SystemInfoTemplater(self._config).process_report(sys_data)

        # Publish the message
        self._logger.debug("Publishing a report")
        Publisher(
            config=self._config, named_account=MASTODON_NAMED_ACCOUNT, base_path=ROOT_DIR
        ).publish_message(message=message)

        return 200


class ListenMessage(Resource):
    '''
    Listener from remote Message requests to log
    '''

    def __init__(self, config: Config = None, logger: logging = None) -> None:
        self._config = config
        self._logger = logger
        self._current_flask_app = app
        self._parser = reqparse.RequestParser()
        self._parser.add_argument(
            'summary',
            # type = str,
            # required = True,
            # help = 'No message provided',
            location='form'
        )
        self._parser.add_argument(
            'message',
            # type = str,
            # required = True,
            # help = 'No message provided',
            location='form'
        )
        self._parser.add_argument(
            'hostname',
            # type = str,
            # required = True,
            # help = 'No hostname provided',
            location='form'
        )
        self._parser.add_argument(
            'message_type',
            # type = str,
            # required = True,
            # help = 'No message provided',
            location='form'
        )

        super(ListenMessage, self).__init__()

    def post(self):
        """
        This is going to receive the POST request
        """

        self._logger.info(
            f"{TerminalColor.MAGENTA}Message Listener{TerminalColor.END}" +
            f" received a request from {request.remote_addr}"
        )

        # Get the data
        args = self._parser.parse_args()
        if "summary" in args and args["summary"] is not None:
            summary = args["summary"]
        else:
            summary = None
        if "message_type" in args and args["message_type"] is not None:
            message_type = args["message_type"]
        else:
            message_type = DEFAULT_MESSAGE_TYPE
        if "message" in args and args["message"] is not None:
            text = args["message"]
        else:
            return {
                "error": "Expected string under a \"message\" variable was not present."
            }, 400
        if "hostname" in args and args["hostname"] is not None:
            hostname = args["hostname"]
        else:
            return {
                "error": "Expected string under a \"hostname\" variable was not present."
            }, 400

        # Build the message
        icon = MessageType.icon_per_type(message_type)
        if not summary:
            message = Message(text=f"{icon} from {hostname}:\n\n{text}")
        else:
            message = Message(summary=f"{icon} {hostname}:\n\n{summary}", text=f"{text}")

        # Publish the message
        self._logger.debug("Publishing a message")
        Publisher(
            config=self._config, named_account=MASTODON_NAMED_ACCOUNT, base_path=ROOT_DIR
        ).publish_message(message=message)
        return 200

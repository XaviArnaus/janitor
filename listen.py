from pyxavi.config import Config
from pyxavi.logger import Logger
from janitor.lib.system_info import SystemInfo
from janitor.lib.system_info_templater import SystemInfoTemplater
from janitor.lib.publisher import Publisher
from janitor.lib.mastodon_helper import MastodonHelper
from janitor.objects.queue_item import QueueItem
from janitor.objects.message import Message, MessageType
from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)


class ListenSysInfo(Resource):
    '''
    Listener from remote SysInfo Report requests to log
    '''

    def __init__(self):
        self._config = Config()
        self._logger = Logger(self._config).getLogger()
        self._sys_info = SystemInfo(self._config)
        self._parser = reqparse.RequestParser()
        self._parser.add_argument(
            'sys_data', type=dict, required=True, help='No sys_data provided', location='json'
        )
        self._logger.info("Init SysInfo Listener")

        super(ListenSysInfo, self).__init__()

    def post(self):
        """
        This is going to receive the POST request
        """

        self._logger.info("Run SysInfo Listener app")

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
            self._logger.info("No issues found. Ending here.")
            return 200

        # Make it a message
        message = SystemInfoTemplater(self._config).process_report(sys_data)

        # Publish the queue
        mastodon = MastodonHelper.get_instance(self._config)
        publisher = Publisher(self._config, mastodon)
        self._logger.info("Publishing one message")
        publisher.publish_one(QueueItem(message))

        self._logger.info("End.")
        return 200


class ListenMessage(Resource):
    '''
    Listener from remote Message requests to log
    '''

    def __init__(self):
        self._config = Config()
        self._logger = Logger(self._config).getLogger()
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
            'type',
            # type = str,
            # required = True,
            # help = 'No message provided',
            location='form'
        )
        self._logger.info("Init Message Listener Listener")

        super(ListenMessage, self).__init__()

    def post(self):
        """
        This is going to receive the POST request
        """

        self._logger.info("Run Message Listener app")

        # Get the data
        args = self._parser.parse_args()
        if "summary" in args:
            summary = args["summary"]
        else:
            summary = None
        if "type" in args:
            message_type = args["type"]
        else:
            message_type = MessageType.NONE
        if "message" in args:
            text = args["message"]
        else:
            return {
                "error": "Expected string under a \"message\" variable was not present."
            }, 400
        if "hostname" in args:
            hostname = args["hostname"]
        else:
            return {
                "error": "Expected string under a \"hostname\" variable was not present."
            }, 400

        # Build the message
        icon = MessageType.icon_per_type(message_type)
        if not summary:
            message = Message(text=f"{icon} {hostname}:\n\n{text}")
        else:
            message = Message(summary=f"{icon} {hostname}:\n\n{summary}", text=f"{text}")

        # Publish the queue
        mastodon = MastodonHelper.get_instance(self._config)
        publisher = Publisher(self._config, mastodon)
        self._logger.info("Publishing one message")
        publisher.publish_one(QueueItem(message))

        self._logger.info("End.")
        return 200


api.add_resource(ListenSysInfo, '/sysinfo')
api.add_resource(ListenMessage, '/message')

if __name__ == '__main__':
    app.run(
        host=Config().get("app.service.listen.host"),
        port=Config().get("app.service.listen.port")
    )

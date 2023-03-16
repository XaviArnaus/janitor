from pyxavi.config import Config
from pyxavi.logger import Logger
from src.lib.system_info import SystemInfo
from src.lib.system_info_templater import SystemInfoTemplater
from src.lib.queue import Queue
from src.lib.publisher import Publisher
from src.lib.mastodon_helper import MastodonHelper
from src.objects.queue_item import QueueItem
from flask import Flask
from flask_restful import Resource, Api, reqparse
from pyxavi.debugger import dd

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument(
    'sys_data',
    type = dict,
    required = True,
    help = 'No sys_data provided',
    location = 'json'
)

class Listen(Resource):
    '''
    Listener from remote requests to log
    '''
    def __init__(self):
        self._config = Config()
        self._logger = Logger(self._config).getLogger()
        self._sys_info = SystemInfo(self._config)
        self._queue = Queue(self._config)
        self._logger.info("Init Listener")

        super(Listen, self).__init__()

    def post(self):
        """
        This is going to receive the POST request
        """

        self._logger.info("Run local app")

        # Get the data
        args = parser.parse_args()
        if "sys_data" in args:
            sys_data = args["sys_data"]
        else:
            return { "error": "Expected dict under a \"sys_data\" variable was not present." }, 400

        # If there is no issue, just stop here.
        if not self._sys_info.crossed_thressholds(sys_data):
            self._logger.info("No issues found. Ending here.")
            return 200

        # Make it a message
        message = SystemInfoTemplater(self._config).process_report({
            **{
                "hostname": self._sys_info.get_hostname()
            },
            **sys_data
        })

        # Add it into the queue and save
        self._logger.debug("Adding message into the queue")
        self._queue.append(QueueItem(message))
        self._queue.save()

        # Publish the queue
        akkoma = MastodonHelper.get_instance(self._config)
        publisher = Publisher(self._config, akkoma)
        self._logger.info("Publishing the whole queue")
        publisher.publish_all_from_queue()

        self._logger.info("End.")
        return 200
    
api.add_resource(Listen, '/sysinfo')

if __name__ == '__main__':
    app.run(debug=True)
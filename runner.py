from pyxavi.config import Config
from pyxavi.logger import Logger
from main import Main

class Runner:
    '''
    Main runner of the app
    '''
    def init(self):
        self._config = Config()
        self._logger = Logger(self._config).getLogger()
        self._logger.info("Init Runner")

        return self

    def run(self):
        self._logger.info("Run app")
        echo = Main(self._config)
        echo.run()
        self._logger.info("End.")

if __name__ == '__main__':
    Runner().init().run()


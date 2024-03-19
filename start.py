import speedtest
import time
import yaml
import os
from database import Database
import logging

# create logger
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
console_handler.setFormatter(formatter)
# add ch to logger
logger.addHandler(console_handler)


db_config: dict = {}
DEFAULT_DELAY = 3600


class ScriptExeption(Exception):
    pass


class Config:
    """Bot config base class """

    def __init__(self, filename):
        """Init config, set attributes """

        config = os.path.dirname(os.path.abspath(__file__)) + "/" + filename
        with open(config, 'r') as config:
            settings = yaml.safe_load(config)

        if not settings:
            raise ScriptExeption("Config file empty or has wrong format")

        for key, value in settings.items():
            setattr(self, key, value)

        print("DEBUG: Config file has been read")
        logger.info('LOGGER: Config file has been read')

    def add_setting(self, key, value):
        """ Add setting to config """
        setattr(self, key, value)


class Speedcheck():

    def __init__(self) -> None:
        try:
            self.attempt = speedtest.Speedtest(secure=True)
        except Exception as init_speedtest_error:
            raise ScriptExeption(init_speedtest_error)

    def _test(self):
        self.attempt.get_best_server()
        self.attempt.download()
        self.attempt.upload()

    def get_results(self, format=None):
        self.format = format
        self._test()
        if self.format is None:
            return self.attempt.results
        if self.format == "dict":
            return self.attempt.results.dict()
        if self.format == "json":
            return self.attempt.results.json()
        if self.format == "csv":
            return self.attempt.results.csv()
        print("DEBUG: Speedtest result collected")
        logger.info('LOGGER: Speedtest result collected')


def db_save_result(data, **db_config):

    try:
        db = Database(**db_config)
    except Exception as db_init_error:
        raise ScriptExeption('Unable to make connection to DB due to: %s'
                             % db_init_error)

    try:
        cursor = db.cursor
        query = ("INSERT INTO speedtest "
                 "(result) "
                 "VALUES (%s)")
        values = (data, )
        cursor.execute(query, values)
        db.commit()
    except Exception as db_cursor_error:
        raise ScriptExeption("Unable to work with DB cursor due to: %s"
                             % db_cursor_error)
    finally:
        db.close()


if __name__ == "__main__":

    logger.info('Starting...')
    config: Config = None
    try:
        config = Config('config.yml')
    except Exception as read_config_error:
        logger.critical("Config read error: %s", read_config_error)

    for key, value in config.__dict__.items():
        if 'db_' in key:
            db_config.update({key.split('_')[1]: value})
        if value is None:
            logger.critical('DB variable is empty: %s: %s', key, value)
            exit(1)

    if not config.delay:
        config.add_setting('delay', DEFAULT_DELAY)

    try:
        speedcheck = Speedcheck()
    except Exception as speedcheck_init_error:
        logger.critical('Exit due to: %s', speedcheck_init_error)
        exit(1)

    while True:
        try:
            data = speedcheck.get_results('json')
            db_save_result(data, **db_config)
        except Exception as speedcheck_results:
            logger.critical('Error while serving Speedtest results: %s',
                            speedcheck_results)
            exit(1)
        logger.info('Collecting and saving completed. Waiting for %s seconds',
                    config.delay)
        time.sleep(config.delay)

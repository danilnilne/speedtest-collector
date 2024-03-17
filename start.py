import speedtest
import time
import os
from database import Database

DEFAULT_DELAY = 120


class ScriptExeption(Exception):
    pass


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


def init_config() -> list[dict]:

    app_config: dict = {
        'delay': os.getenv('DELAY')
    }
    db_config: dict = {
        'db_user': os.getenv('DB_USER'),
        'db_password': os.getenv('DB_PASSWORD'),
        'db_host': os.getenv('DB_HOST'),
        'db_database': os.getenv('DB_DATABASE'),
        'db_raise_on_warnings': os.getenv('DB_RAISE_ON_WARN')
    }
    for key, value in db_config.items():
        if value is None:
            raise ScriptExeption('DB variable is empty: %s: \'%s\''
                                 % (key, value))
    return app_config, db_config


def db_save_result(result, **db_config):

    try:
        db = Database(**db_config)
    except Exception as db_init_error:
        raise ScriptExeption('Unable to make connection to DB due to: %s'
                             % db_init_error)

    try:
        cursor = db.cursor
        query = ("INSERT INTO `%s` (`id`, `result`) "
                 "VALUES (CURRENT_TIMESTAMP, %s)"
                 % (db_config['db_database'], result))
        cursor.execute(query)
        db.commit()
    except Exception as db_cursor_error:
        raise ScriptExeption("Unable to work with DB cursor due to: %s"
                             % db_cursor_error)
    finally:
        db.close()


if __name__ == "__main__":

    try:
        app_config, db_config = init_config()
    except Exception as init_config_error:
        print("Config init error: %s" % init_config_error)
        exit(1)

    try:
        speedcheck = Speedcheck()
    except Exception as speedcheck_init_error:
        print("Exit due to: %s" % speedcheck_init_error)
        exit(1)

    while True:
        try:
            result = speedcheck.get_results()
            print(result)
            db_save_result(result, **db_config)
        except Exception as speedcheck_results:
            print("Error while serve Speedtest results: %s"
                  % speedcheck_results)
        time.sleep(app_config['delay'])

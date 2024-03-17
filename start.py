import speedtest
import time
import os
from database import Database


app_config: dict = {}
db_config: dict = {}

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

    app_config.update({
        'delay': int(os.getenv('DELAY', DEFAULT_DELAY)),
        'table': os.getenv('DB_TABLE', 'speedtest')
    })

    db_config.update({
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_DATABASE'),
        'raise_on_warnings': bool(os.getenv('DB_RAISE_ON_WARN', ''))
    })

    for key, value in db_config.items():
        if value is None:
            raise ScriptExeption('DB variable is empty: %s: \'%s\''
                                 % (key, value))


def db_save_result(data, **db_config):

    try:
        db = Database(**db_config)
    except Exception as db_init_error:
        raise ScriptExeption('Unable to make connection to DB due to: %s'
                             % db_init_error)

    try:
        cursor = db.cursor
        #query = ('INSERT INTO %s (id, result) VALUES '
        #         '(CURRENT_TIMESTAMP, (%s))' % (app_config['table'], data))

        query = ("INSERT INTO speedtest (id, result) "
                 "VALUES (%s, %s)")
        values = ('CURRENT_TIMESTAMP', str(data))

        print(query, values)
        cursor.execute(query, values)
        db.commit()
    except Exception as db_cursor_error:
        raise ScriptExeption("Unable to work with DB cursor due to: %s"
                             % db_cursor_error)
    finally:
        db.close()


if __name__ == "__main__":

    try:
        init_config()
        print("debug: Init config completed")
    except Exception as init_config_error:
        print("Config init error: %s" % init_config_error)
        exit(1)

    try:
        speedcheck = Speedcheck()
        print("debug: Iinit DB completed")
    except Exception as speedcheck_init_error:
        print("Exit due to: %s" % speedcheck_init_error)
        exit(1)

    while True:
        print("debug: in 'While' loop")
        try:
            data = speedcheck.get_results('json')
            print(data)
            db_save_result(data, **db_config)
            print("debug: Saved to db")
        except Exception as speedcheck_results:
            print("Error while serve Speedtest results: %s"
                  % speedcheck_results)
            exit(1)
        time.sleep(app_config['delay'])

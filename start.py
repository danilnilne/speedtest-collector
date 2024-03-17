import speedtest
import os
import time

DEFAULT_DELAY = 120


class ScriptExeption(Exception):
    pass


class Speedcheck():

    def __init__(self) -> None:
        try:
            self.attempt = speedtest.Speedtest()
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


def init_config() -> dict[str, any]:
    pass


if __name__ == "__main__":

    try:
        speedcheck = Speedcheck()
    except Exception as speedcheck_init_error:
        print("Exit due to: %s" % speedcheck_init_error)
        exit(1)

    while True:
        try:
            print(speedcheck.get_results())
        except Exception as speedcheck_get_results:
            print("Error while getting Speedtest results: %s"
                  % speedcheck_get_results)
        time.sleep(DEFAULT_DELAY)

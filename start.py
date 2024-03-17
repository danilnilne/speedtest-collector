import speedtest
import os
import time

DEFAULT_DELAY = 600


class ScriptExeption(Exception):
    pass


class Speedcheck():

    def __init__(self, format=None) -> None:
        self.format = format
        try:
            self.attempt = speedtest.Speedtest()
            self.attempt.download()
            self.attempt.upload()
        except Exception as init_speedtest_error:
            raise ScriptExeption(init_speedtest_error)

    def get_results(self):
        if self.format is None:
            return self.attempt.results
        if self.format == "dict":
            return self.attempt.results.dict()
        if self.format == "json":
            return self.attempt.results.json()
        if self.format == "csv":
            return self.attempt.results.csv()

def init_config() -> dict[str, any]:


if __name__ == "__main__":
    db_config = {}

    """
    while True:
        if not config:
            try:
                config = Config('config.yml')
            except Exception as init_config_error:
                print(f"ERROR: {init_config_error}")
        else:
            try:
                st = Speedcheck()
                # Save results to db /file
                print(st.get_results())
            except Exception as work_line_error:
                print(f"ERROR: {work_line_error}")

        try:
            config.delay
        except AttributeError:
            config.add_setting("delay", DEFAULT_DELAY)

        time.sleep(config.delay)
    """
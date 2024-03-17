import mysql.connector
from mysql.connector import errorcode


class ScriptExeption(Exception):
    pass


class Database:

    def __init__(self, **db_config) -> None:
        try:
            self._conn = mysql.connector.connect(**db_config)
            self._cursor = self._conn.cursor()
            self._is_connected = self._conn.is_connected()
        except mysql.connector.Error as db_error:
            if db_error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise ScriptExeption("Incorrect user name or password")
            elif db_error.errno == errorcode.ER_BAD_DB_ERROR:
                raise ScriptExeption("Database does not exist")
            else:
                raise ScriptExeption(db_error)

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    @property
    def is_connected(self):
        return self._is_connected

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

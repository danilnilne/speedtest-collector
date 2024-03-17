import mysql.connector
from mysql.connector import errorcode


class ScriptExeption(Exception):
    pass


class Database:

    def __init__(self, config) -> None:
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


if __name__ == "__main__":
    try:
        db = Database()
    except Exception as error:
        print(f"Unable to make connection to DB due to: {error}")
        exit(1)

    try:
        cursor = db.cursor
        sql_code = ("INSERT INTO `speedtest` (`id`, `result`) VALUES (CURRENT_TIMESTAMP, '123')")
        cursor.execute(sql_code)
        db.commit()

        with cursor:
            result = cursor.execute("SELECT * FROM speedtest")
            rows = cursor.fetchall()
            for rows in rows:
                print(f"#->: {rows}")
        db.close()
    except Exception as cursor_error:
        print(f"Unable to work with DB cursor due to: {cursor_error}")
        exit(1)

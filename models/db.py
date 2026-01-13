import sqlite3

class DB:
    """
    Class for connecting to the currency_exchange database
    """
    def __init__(self, db_path="currency_exchange.db"):
        self._db_path = db_path

    def connect_to_db(self):
        """
        Returns a new connection to the db
        """
        connection = sqlite3.connect(self._db_path)
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection
    
    def get_cursor(self):
        """
        Returns a tuple (conn, cursor) for working with the DB
        """
        conn = self.connect_to_db()
        cursor = conn.cursor()
        return conn, cursor

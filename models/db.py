import sqlite3

class DB:
    """
    Класс для подключения к базе данных currency_exchange
    """
    def __init__(self, db_path="currency_exchange.db"):
        self._db_path = db_path

    def connect_to_db(self):
        """
        Возвращает новое соединение с бд
        """
        connection = sqlite3.connect(self._db_path)
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection
    
    def get_cursor(self):
        """
        Возвращает кортеж (conn, cursor) для работы с БД
        """
        conn = self.connect_to_db()
        cursor = conn.cursor()
        return conn, cursor

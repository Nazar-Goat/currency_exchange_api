import sqlite3

class DatabaseCreator:
    """
    Класс создает базу данных с таблицами и заполняет их базовыми значениями 
    """

    def __init__(self, db_path="currency_exchange.db"):
        self._db_path = db_path

    def create_table_currencies(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Currencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            fullname TEXT NOT NULL,
            sign TEXT NOT NULL
        );
        """)

    def create_table_exchange_rates(self, cursor):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ExchangeRates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            baseCurrencyId INTEGER NOT NULL,
            targetCurrencyId INTEGER NOT NULL,
            rate DECIMAL(20,6) NOT NULL,
            UNIQUE(baseCurrencyId, targetCurrencyId),
            FOREIGN KEY(baseCurrencyId) REFERENCES Currencies(id),
            FOREIGN KEY(targetCurrencyId) REFERENCES Currencies(id)
        );
        """)

    def insert_currencies(self, cursor):
        currencies = [
            ('USD', 'United States dollar', '$'),
            ('EUR', 'Euro', '€'),
            ('RUB', 'Russian ruble', '₽'),
            ('AUD', 'Australian dollar', 'A$'),
            ('JPY', 'Japanese yen', '¥'),
        ]

        for code, fullname, sign in currencies:
            try:
                cursor.execute("""
                INSERT INTO Currencies (code, fullname, sign)
                VALUES (?, ?, ?);
                """, (code, fullname, sign))
            except sqlite3.IntegrityError:
                pass

    def insert_exchange_rates(self, cursor):
        usd_id = self.get_currency_id('USD', cursor)
        eur_id = self.get_currency_id('EUR', cursor)
        rub_id = self.get_currency_id('RUB', cursor)

        exchange_rates = [
            (usd_id, eur_id, 0.91),
            (usd_id, rub_id, 93.45),
            (eur_id, rub_id, 102.55),
        ]

        for base_id, target_id, rate in exchange_rates:
            try:
                cursor.execute("""
                INSERT INTO ExchangeRates (baseCurrencyId, targetCurrencyId, rate)
                VALUES (?, ?, ?);
                """, (base_id, target_id, rate))
            except sqlite3.IntegrityError:
                pass

    def get_currency_id(self, cur_code, cursor):
        cursor.execute("SELECT id FROM Currencies WHERE code = ?;", (cur_code,))
        result = cursor.fetchone()
        return result[0] if result else None

    def init_all(self):
        """
        Полная инициализация: создаёт таблицы и заполняет начальными данными
        """
        with sqlite3.connect(self._db_path) as db:
            cursor = db.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            self.create_table_currencies(cursor)
            self.create_table_exchange_rates(cursor)
            self.insert_currencies(cursor)
            self.insert_exchange_rates(cursor)
            db.commit()

if __name__ == "__main__":
    db_creator = DatabaseCreator()
    db_creator.init_all()
    

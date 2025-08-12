from models.db import DB
import sqlite3

class ExchangeRatesDAO:
    """
    DAO class for ExchangeRates table
    """
    def __init__(self, db: DB):
        self._db = db

    def get_all(self):
        conn, cursor = self._db.get_cursor()
        try:
            cursor.execute("""
                SELECT id, baseCurrencyId, targetCurrencyId, rate
                FROM ExchangeRates;
            """)
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "base_currency_id": row[1],
                    "target_currency_id": row[2],
                    "rate": row[3]
                }
                for row in rows
            ]
        finally:
            conn.close()

    def get_exchange_rate(self, base_id: int, target_id: int):
        conn, cursor = self._db.get_cursor()
        try:
            cursor.execute(
                """
                SELECT id, baseCurrencyId, targetCurrencyId, rate
                FROM ExchangeRates
                WHERE baseCurrencyId = ? AND targetCurrencyId = ?;
                """,
                (base_id, target_id)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "base_currency_id": row[1],
                    "target_currency_id": row[2],
                    "rate": row[3]
                }
            return None
        finally:
            conn.close()

    def insert(self, base_id: int, target_id: int, rate: float):
        conn, cursor = self._db.get_cursor()
        try:
            cursor.execute("""
                INSERT INTO ExchangeRates (baseCurrencyId, targetCurrencyId, rate)
                VALUES (?, ?, ?);
            """, (base_id, target_id, rate))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(
                f"Rate from {base_id} to {target_id} already exists or currency IDs invalid."
            ) from e
        finally:
            conn.close()

    def set_exchange_rate(self, base_id: int, target_id: int, rate: float):
        conn, cursor = self._db.get_cursor()
        try:
            cursor.execute("""
                UPDATE ExchangeRates
                SET rate = ?
                WHERE baseCurrencyId = ? AND targetCurrencyId = ?;
            """, (rate, base_id, target_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
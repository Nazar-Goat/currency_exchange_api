from models.db import DB
import sqlite3

class CurrencyDAO:
    """
    DAO class for Currency table
    """
    def __init__(self, db: DB):
        self._db = db

    def get_all_currencies(self):
        conn, cursor = self._db.get_cursor()
        try: 
            cursor.execute("SELECT id, code, fullname, sign FROM Currencies;")
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "code": row[1],
                    "fullname": row[2],
                    "sign": row[3]
                }
                for row in rows
            ]
        finally:
            conn.close()

    def get_currency_by_code(self, code: str):
        conn, cursor = self._db.get_cursor()
        try:
            cursor.execute(
                "SELECT id, code, fullname, sign FROM Currencies WHERE code = ?;",
                (code.upper(),)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "code": row[1],
                    "fullname": row[2],
                    "sign": row[3]
                }
            return None
        finally:
            conn.close()

    def get_currency_by_id(self, currency_id: int):
        conn, cursor = self._db.get_cursor()
        try:
            cursor.execute(
                "SELECT id, code, fullname, sign FROM Currencies WHERE id = ?;",
                (currency_id,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "code": row[1],
                    "fullname": row[2],
                    "sign": row[3]
                }
            return None
        finally:
            conn.close()

    def insert(self, code: str, fullname: str, sign: str):
        conn, cursor = self._db.get_cursor()
        try:
            cursor.execute(
                "INSERT INTO Currencies (code, fullname, sign) VALUES (?, ?, ?);",
                (code.upper(), fullname, sign)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Currency with code '{code}' already exists.") from e
        finally:
            conn.close()

    def update_by_code(self, code: str, fullname: str, sign: str):
        conn, cursor = self._db.get_cursor()
        try:
            cursor.execute(
                "UPDATE Currencies SET fullname = ?, sign = ? WHERE code = ?;",
                (fullname, sign, code.upper())
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
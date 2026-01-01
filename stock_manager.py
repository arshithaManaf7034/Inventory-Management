from datetime import datetime
import sqlite3


class StockManager:
    def __init__(self, db):
        self.db = db

    def stock_in(self, product_id, qty):
        try:
            self.db.cursor.execute(
                "SELECT quantity FROM stock WHERE product_id=?",
                (product_id,)
            )
            row = self.db.cursor.fetchone()

            if row:
                new_qty = row[0] + qty
                self.db.cursor.execute(
                    "UPDATE stock SET quantity=? WHERE product_id=?",
                    (new_qty, product_id)
                )
            else:
                self.db.cursor.execute(
                    "INSERT INTO stock VALUES (?, ?)",
                    (product_id, qty)
                )

            self._log_transaction(product_id, "IN", qty)
            self.db.conn.commit()
            print("Stock added successfully.")

        except sqlite3.Error:
            print("Error while adding stock.")

    def stock_out(self, product_id, qty):
        try:
            self.db.cursor.execute(
                "SELECT quantity FROM stock WHERE product_id=?",
                (product_id,)
            )
            row = self.db.cursor.fetchone()

            if not row or row[0] < qty:
                print("Insufficient stock.")
                return

            new_qty = row[0] - qty
            self.db.cursor.execute(
                "UPDATE stock SET quantity=? WHERE product_id=?",
                (new_qty, product_id)
            )

            self._log_transaction(product_id, "OUT", qty)
            self.db.conn.commit()
            print("Stock reduced successfully.")

        except sqlite3.Error:
            print("Error while reducing stock.")

    def _log_transaction(self, pid, ttype, qty):
        self.db.cursor.execute(
            "INSERT INTO transactions (product_id, type, quantity, date) VALUES (?, ?, ?, ?)",
            (pid, ttype, qty, datetime.now())
        )

from datetime import datetime
import sqlite3


class ReportManager:
    def __init__(self, db):
        self.db = db

    def stock_report(self):
        self.db.cursor.execute("""
            SELECT p.id, p.name, IFNULL(s.quantity, 0)
            FROM products p
            LEFT JOIN stock s ON p.id = s.product_id
        """)
        rows = self.db.cursor.fetchall()

        if not rows:
            print("No stock data found.")
            return

        print("\nSTOCK REPORT")
        print("-" * 55)
        print(f"{'ID':<5} {'Product Name':<25} {'Quantity':<10}")
        print("-" * 55)

        for pid, name, qty in rows:
            print(f"{pid:<5} {name:<25} {qty:<10}")

            print("-" * 55)


    def transaction_report(self):
        self.db.cursor.execute("""
        SELECT product_id, type, quantity, date
        FROM transactions
        ORDER BY date
        """)
        rows = self.db.cursor.fetchall()

        if not rows:
            print("No transactions found.")
            return

        print("\nTRANSACTION REPORT")
        print("-" * 75)
        print(f"{'Product ID':<12} {'Type':<8} {'Quantity':<10} {'Date'}")
        print("-" * 75)

        for pid, ttype, qty, date in rows:
            print(f"{pid:<12} {ttype:<8} {qty:<10} {date}")

            print("-" * 75)


    def export_report_txt(self):
        file_name = "inventory_report.txt"

        try:
            with open(file_name, "w") as f:
                f.write("INVENTORY MANAGEMENT REPORT\n")
                f.write("=" * 40 + "\n")
                f.write(f"Generated on: {datetime.now()}\n\n")

                # -------- STOCK REPORT --------
                f.write("STOCK REPORT\n")
                f.write("-" * 40 + "\n")

                self.db.cursor.execute("""
                    SELECT p.id, p.name, IFNULL(s.quantity, 0)
                    FROM products p
                    LEFT JOIN stock s ON p.id = s.product_id
                """)
                stock_data = self.db.cursor.fetchall()

                if not stock_data:
                    f.write("No stock data available.\n")
                else:
                    for pid, name, qty in stock_data:
                        f.write(f"Product ID: {pid}, Name: {name}, Quantity: {qty}\n")

                # -------- TRANSACTION REPORT --------
                f.write("\nTRANSACTION REPORT\n")
                f.write("-" * 40 + "\n")

                self.db.cursor.execute("""
                    SELECT product_id, type, quantity, date
                    FROM transactions
                """)
                trans_data = self.db.cursor.fetchall()

                if not trans_data:
                    f.write("No transactions available.\n")
                else:
                    for t in trans_data:
                        f.write(f"{t}\n")

            print(f"Report exported successfully as {file_name}")

        except Exception as e:
            print("Error exporting report:", e)

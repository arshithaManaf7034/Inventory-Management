import sqlite3


class SupplierManager:
    def __init__(self, db):
        self.db = db

    def add_supplier(self, sid, name, phone, email):
        try:
            self.db.cursor.execute(
                "INSERT INTO suppliers VALUES (?, ?, ?, ?)",
                (sid, name.strip(), phone.strip(), email.strip())
            )
            self.db.conn.commit()
            print("Supplier added successfully.")
        except sqlite3.IntegrityError:
            print("Supplier already exists.")

    def view_suppliers(self):
        self.db.cursor.execute("SELECT * FROM suppliers")
        return self.db.cursor.fetchall()


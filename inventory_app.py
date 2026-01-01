import sqlite3
from database import Database
from supplier import SupplierManager
from stock_manager import StockManager
from reportmanager import ReportManager



# ===================== USER MANAGER =====================
print(">>> inventory_app.py STARTED <<<")

class UserManager:
    def __init__(self, db):
        self.db = db

    def admin_exists(self):
        self.db.cursor.execute("SELECT 1 FROM users WHERE role='admin'")
        return self.db.cursor.fetchone() is not None

    def register(self, uid, uname, pwd, role):
        if role == "admin" and self.admin_exists():
            print("Admin already exists. Register as staff.")
            return
        try:
            self.db.cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?)",
                (uid, uname.strip(), pwd.strip(), role.strip())
            )
            self.db.conn.commit()
            print("Registration successful.")
        except sqlite3.IntegrityError:
            print("User ID or Username already exists.")

    def login(self, uname, pwd):
        self.db.cursor.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (uname.strip(), pwd.strip())
        )
        result = self.db.cursor.fetchone()
        return result[0] if result else None


# ===================== CATEGORY MANAGER =====================

class CategoryManager: 
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RESET = "\033[0m"
    
    def __init__(self, db):
        self.db = db
    def get_demand_indicator(self, requirement_rate):
        if requirement_rate >= 70:
            return f"{self.RED}HIGH{self.RESET}"
        elif requirement_rate >= 40:
            return f"{self.YELLOW}MEDIUM{self.RESET}"
        else:
            return f"{self.GREEN}LOW{self.RESET}"



    def add_category(self, cid, name):
        try:
            self.db.cursor.execute(
                "INSERT INTO categories VALUES (?, ?)",
                (cid, name.strip())
            )
            self.db.conn.commit()
            print("Category added.")
        except sqlite3.IntegrityError:
            print("Category already exists.")

    def view_categories(self):
        self.db.cursor.execute("SELECT * FROM categories")
        return self.db.cursor.fetchall()
    
    def delete_category(self, cid):
        try:
            self.db.cursor.execute(
            "DELETE FROM categories WHERE id = ?",
            (cid,)
        )
            if self.db.cursor.rowcount == 0:
                print("Category ID not found.")
            else:
                self.db.conn.commit()
                print("Category deleted successfully.")
        except Exception as e:
            print("Error deleting category:", e)

    def update_category(self, cid, new_name):
        try:
            self.db.cursor.execute(
            "UPDATE categories SET name=? WHERE id=?",
            (new_name.strip(), cid)
            )
            if self.db.cursor.rowcount == 0:
                print("Category ID not found.")
            else:
                self.db.conn.commit()
                print("Category updated successfully.")
        except Exception as e:
            print("Error updating category:", e)
    def category_product_analysis(self, category_id):
        query = """
            SELECT 
                p.id,
                p.name,
                IFNULL(s.quantity, 0) AS stock_qty,
                IFNULL(t.total_sales, 0) AS total_sales
            FROM products p
            LEFT JOIN stock s ON p.id = s.product_id
            LEFT JOIN (
                SELECT product_id, SUM(quantity) AS total_sales
                FROM transactions
                WHERE type = 'OUT'
                GROUP BY product_id
            ) t ON p.id = t.product_id
            WHERE p.category_id = ?
            """
        self.db.cursor.execute(query, (category_id,))
        return self.db.cursor.fetchall()
    



# ===================== PRODUCT MANAGER =====================

class ProductManager:
    def __init__(self, db):
        self.db = db

    def add_product(self, pid, name, price, cid):
        self.db.cursor.execute(
            "INSERT INTO products VALUES (?, ?, ?, ?)",
            (pid, name.strip(), price, cid)
        )
        self.db.conn.commit()
        print("Product added.")

    def view_products(self):
        self.db.cursor.execute("""
            SELECT p.id, p.name, p.price, c.name
            FROM products p
            JOIN categories c ON p.category_id = c.id
        """)
        return self.db.cursor.fetchall()
    def delete_product(self, pid):
        try:
            self.db.cursor.execute(
            "DELETE FROM products WHERE id = ?",
            (pid,)
            )
            if self.db.cursor.rowcount == 0:
                print("Product ID not found.")
            else:
                self.db.conn.commit()
                print("Product deleted successfully.")
        except Exception as e:
            print("Error deleting product:", e)
    def update_product(self, pid, new_name, new_price, new_cid):
        try:
            self.db.cursor.execute(
            """
            UPDATE products
            SET name=?, price=?, category_id=?
            WHERE id=?
            """,
            (new_name.strip(), new_price, new_cid, pid)
            )
            if self.db.cursor.rowcount == 0:
                print("Product ID not found.")
            else:
                self.db.conn.commit()
                print("Product updated successfully.")
        except Exception as e:
            print("Error updating product:", e)




# ===================== MENUS (UI LAYER) =====================

def category_menu(cat_mgr):
    while True:
        print("""
--- CATEGORY MENU ---
1. Add Category
2. View Categories
3. Edit Category
4. Delete Category
5. View Category Product Analysis
6. Back
""")
        ch = input("Choice: ")

        if ch == "1":
            cid = input("Category ID (number only): ")

            if not cid.isdigit():
                print("Invalid input! Category ID must be a number.")
                continue

            name = input("Category Name: ")
            cat_mgr.add_category(int(cid), name)

        elif ch == "2":
            categories = cat_mgr.view_categories()
            if not categories:
                print("No categories found.")
            else:
                print("\nID | Category Name")
                print("-" * 25)
                for c in categories:
                    print(f"{c[0]} | {c[1]}")

        elif ch == "3":
            cid = input("Enter Category ID to edit: ")
            if not cid.isdigit():
                print("ID must be numeric.")
                continue
            new_name = input("Enter new category name: ")
            cat_mgr.update_category(int(cid), new_name)

        elif ch == "4":
            cid = input("Enter Category ID to delete: ")
            if not cid.isdigit():
                print("ID must be numeric.")
                continue
            if input("Confirm delete (yes/no): ").lower() == "yes":
                cat_mgr.delete_category(int(cid))
        elif ch == "5":
            cid = input("Enter Category ID: ")
            if not cid.isdigit():
                print("ID must be numeric.")
                continue

            data = cat_mgr.category_product_analysis(int(cid))

            if not data:
                print("No products found for this category.")
                continue

            total_category_sales = sum(row[3] for row in data)

            print("\nProduct Analysis")
            print("ID | Name | Stock | Sales | Sales% | Req% | Demand")
            print("-" * 75)

            for pid, name, stock, sales in data:
                sales_rate = (
                    (sales / total_category_sales) * 100
                    if total_category_sales > 0 else 0
                )

                requirement_rate = (
                    (sales / (stock + sales)) * 100
                    if (stock + sales) > 0 else 0
                 )

                demand = cat_mgr.get_demand_indicator(requirement_rate)


                print(
                        f"{pid} | {name} | {stock} | {sales} | "
                        f"{sales_rate:.2f}% | {requirement_rate:.2f}% | {demand}"
                )

            
        elif ch == "6":
            break



def product_menu(prod_mgr):
    while True:
        print("""
--- PRODUCT MENU ---
1. Add Product
2. View Products
3. Edit Product
4. Delete Product
5. Back
""")
        ch = input("Choice: ")

        if ch == "1":
            prod_mgr.add_product(
                int(input("Product ID: ")),
                input("Product Name: "),
                float(input("Price: ")),
                int(input("Category ID: "))
            )
        elif ch == "2":
            products = prod_mgr.view_products()

            if not products:
                print("No products found.")
            else:
                print("\nPRODUCT LIST")
                print("-" * 65)
                print(f"{'ID':<5} {'Name':<20} {'Price':<10} {'Category':<20}")
                print("-" * 65)

                for pid, name, price, category in products:
                    print(f"{pid:<5} {name:<20} {price:<10.2f} {category:<20}")

                    print("-" * 65)
        elif ch == "3":
                try:
                    pid = int(input("Product ID to edit: "))
                    new_name = input("New Product Name: ")
                    new_price = float(input("New Price: "))
                    new_cid = int(input("New Category ID: "))
                    prod_mgr.update_product(pid, new_name, new_price, new_cid)
                except ValueError:
                    print("Invalid input.")
        elif ch == "4":
            pid = input("Product ID to delete: ")
            if not pid.isdigit():
                print("ID must be numeric.")
                continue
            if input("Confirm delete (yes/no): ").lower() == "yes":
                prod_mgr.delete_product(int(pid))

        elif ch == "5":
            break


def supplier_menu(supplier_mgr):
    while True:
        print("""
--- SUPPLIER MENU ---
1. Add Supplier
2. View Suppliers
3. Back
""")
        ch = input("Choice: ")

        if ch == "1":
            supplier_mgr.add_supplier(
                int(input("Supplier ID: ")),
                input("Name: "),
                input("Phone: "),
                input("Email: ")
            )
        
        elif ch == "2":
            suppliers = supplier_mgr.view_suppliers()

            if not suppliers:
                print("No suppliers found.")
            else:
                print("\nSUPPLIER LIST")
                print("-" * 70)
                print(f"{'ID':<5} {'Name':<20} {'Phone':<15} {'Email':<25}")
                print("-" * 70)

                for sid, name, phone, email in suppliers:
                    print(f"{sid:<5} {name:<20} {phone:<15} {email:<25}")

                    print("-" * 70)



        elif ch == "3":
            break

def report_menu(report_mgr):
    while True:
        print("""
--- REPORTS ---
1. Stock Report
2. Transaction Report
3. Export Report (TXT)
4. Back
""")
        ch = input("Choice: ")

        if ch == "1":
            report_mgr.stock_report()
        elif ch == "2":
            report_mgr.transaction_report()
        elif ch == "3":
            report_mgr.export_report_txt()
        elif ch == "4":
            break
def purchase_menu(stock_mgr):
    try:
        pid = int(input("Product ID: "))
        qty = int(input("Quantity: "))
        stock_mgr.stock_in(pid, qty)
    except ValueError:
        print("Invalid input. Only numbers allowed.")
def sale_menu(stock_mgr):
    try:
        pid = int(input("Product ID: "))
        qty = int(input("Quantity: "))
        stock_mgr.stock_out(pid, qty)
    except ValueError:
        print("Invalid input. Only numbers allowed.")



def admin_menu(cat_mgr, prod_mgr, supplier_mgr, stock_mgr, report_mgr):
    while True:
        print("""
--- ADMIN MENU ---
1. Manage Categories
2. Manage Products
3. Manage Suppliers
4. Purchase (Stock IN)
5. Sale (Stock OUT)
6. Reports
7. Logout
""")
        ch = input("Choice: ")

        if ch == "1":
            category_menu(cat_mgr)
        elif ch == "2":
            product_menu(prod_mgr)
        elif ch == "3":
            supplier_menu(supplier_mgr)
        elif ch == "4":
            purchase_menu(stock_mgr)
        elif ch == "5":
            sale_menu(stock_mgr)
        elif ch == "6":
            report_menu(report_mgr)
        elif ch == "7":
            break


def staff_menu(prod_mgr):
    while True:
        print("""
--- STAFF MENU ---
1. View Products
2. Logout
""")
        ch = input("Choice: ")

        if ch == "1":
            for p in prod_mgr.view_products():
                print(p)
        elif ch == "2":
            break


# ===================== MAIN =====================

def main():
    db = Database()
    user_mgr = UserManager(db)
    cat_mgr = CategoryManager(db)
    prod_mgr = ProductManager(db)
    supplier_mgr = SupplierManager(db)
    stock_mgr = StockManager(db)
    report_mgr = ReportManager(db)

    while True:
        try:
            user_type = input("Are you a new user? (yes/no/exit): ").strip().lower()

            if user_type == "yes":
                try:
                    uid = int(input("User ID (number only): "))
                except ValueError:
                    print("User ID must be a number.")
                    continue

                uname = input("Username: ").strip()
                pwd = input("Password: ").strip()
                role = input("Role (admin/staff): ").strip().lower()

                if not uname or not pwd:
                    print("Username and password cannot be empty.")
                    continue

                user_mgr.register(uid, uname, pwd, role)

            elif user_type == "no":
                uname = input("Username: ").strip()
                pwd = input("Password: ").strip()

                if not uname or not pwd:
                    print("Username and password cannot be empty.")
                    continue

                role = user_mgr.login(uname, pwd)

                if role == "admin":
                    admin_menu(
                        cat_mgr,
                        prod_mgr,
                        supplier_mgr,
                        stock_mgr,
                        report_mgr
                    )
                elif role == "staff":
                    staff_menu(prod_mgr)
                else:
                    print("Invalid username or password.")

            elif user_type == "exit":
                print("Exiting application.")
                db.close()
                break

            else:
                print("Invalid option. Please enter yes, no, or exit.")

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            continue

        except Exception as e:
            print("Unexpected error:", e)
            continue
if __name__ == "__main__":
    main()
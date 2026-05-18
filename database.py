import sqlite3


class FinanceDatabase:
    def __init__(self, db_name="finance.db"):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                UNIQUE(name, type)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
        """)

        default_categories = [
            ("Salary", "Income"),
            ("Freelance", "Income"),
            ("Food", "Expense"),
            ("Rent", "Expense"),
            ("Transport", "Expense"),
            ("Shopping", "Expense"),
        ]

        for name, type_ in default_categories:
            cur.execute(
                "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
                (name, type_)
            )

        conn.commit()
        conn.close()

    def get_categories(self):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, type
            FROM categories
            ORDER BY type, name
        """)

        rows = cur.fetchall()
        conn.close()
        return rows

    def add_category(self, name, type_):
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO categories (name, type) VALUES (?, ?)",
                (name.strip(), type_)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("This category already exists.")
        finally:
            conn.close()

    def delete_category(self, category_id):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM transactions WHERE category_id = ?", (category_id,))
        count = cur.fetchone()[0]

        if count > 0:
            conn.close()
            raise ValueError("This category is used by transactions and cannot be deleted.")

        cur.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        conn.close()

    def add_transaction(self, date, type_, category_id, amount, description):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO transactions (date, type, category_id, amount, description)
            VALUES (?, ?, ?, ?, ?)
        """, (date, type_, category_id, float(amount), description))

        conn.commit()
        conn.close()

    def get_transactions(self):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                t.id,
                t.date,
                t.type,
                c.name,
                t.amount,
                COALESCE(t.description, '')
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            ORDER BY t.date ASC, t.id ASC
        """)

        rows = cur.fetchall()
        conn.close()
        return rows

    def update_transaction(self, transaction_id, date, type_, category_id, amount, description):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE transactions
            SET date = ?, type = ?, category_id = ?, amount = ?, description = ?
            WHERE id = ?
        """, (date, type_, category_id, float(amount), description, transaction_id))

        conn.commit()
        conn.close()

    def delete_transaction(self, transaction_id):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))

        conn.commit()
        conn.close()
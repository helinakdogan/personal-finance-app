"""Database layer for the Flowance application.

Provides FinanceDatabase, a thin wrapper around SQLite that exposes
create / read / update / delete operations for categories and transactions.
All SQL is parameterised; no raw string interpolation is used.
"""

import sqlite3


class FinanceDatabase:
    """Manages the SQLite database for categories and transactions.

    A new connection is opened and closed for every operation so that
    concurrent access from multiple windows does not share state.
    """

    def __init__(self, db_name="finance.db"):
        """Initialise with the path to the SQLite database file."""
        self.db_name = db_name

    def get_connection(self):
        """Open and return a new SQLite connection."""
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """Create the schema and seed default categories if they do not exist.

        Called once at application startup. INSERT OR IGNORE prevents
        duplicate default categories on subsequent launches.
        """
        conn = self.get_connection()
        cur = conn.cursor()

        # UNIQUE(name, type) lets the same label exist once per type (e.g. an Income "Other"
        # and an Expense "Other") while blocking exact duplicates.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                UNIQUE(name, type)
            )
        """)

        # FOREIGN KEY ties each transaction to a category; delete_category relies on this link.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                type        TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                amount      REAL NOT NULL,
                description TEXT,
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
        """)

        default_categories = [
            ("Salary",    "Income"),
            ("Freelance", "Income"),
            ("Food",      "Expense"),
            ("Rent",      "Expense"),
            ("Transport", "Expense"),
            ("Shopping",  "Expense"),
        ]

        # INSERT OR IGNORE skips any default that already exists, so re-running on every
        # startup never creates duplicates and never errors on the UNIQUE constraint.
        for name, type_ in default_categories:
            cur.execute(
                "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
                (name, type_)
            )

        conn.commit()
        conn.close()

    def get_categories(self):
        """Return all categories as a list of (id, name, type) tuples, ordered by type then name."""
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
        """Insert a new category.

        Raises ValueError if a category with the same name and type already exists.
        """
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO categories (name, type) VALUES (?, ?)",
                (name.strip(), type_)
            )
            conn.commit()
        # The UNIQUE(name, type) index throws IntegrityError on a duplicate; convert it to a
        # ValueError so the UI layer can show a friendly warning instead of crashing.
        except sqlite3.IntegrityError:
            raise ValueError(
                f'A "{type_}" category named "{name}" already exists.'
            )
        finally:
            conn.close()

    def delete_category(self, category_id):
        """Delete a category by its ID.

        Raises ValueError if the category is referenced by one or more transactions,
        as deleting it would violate referential integrity.
        """
        conn = self.get_connection()
        cur = conn.cursor()

        # Count transactions pointing at this category first; deleting a referenced category
        # would orphan those rows and break the foreign-key relationship.
        cur.execute(
            "SELECT COUNT(*) FROM transactions WHERE category_id = ?",
            (category_id,)
        )
        count = cur.fetchone()[0]

        if count > 0:
            conn.close()
            raise ValueError(
                "This category cannot be deleted because it is referenced "
                "by existing transactions."
            )

        cur.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        conn.close()

    def add_transaction(self, date, type_, category_id, amount, description):
        """Insert a new transaction record."""
        conn = self.get_connection()
        cur = conn.cursor()

        # Parameterised query (the ? placeholders) prevents SQL injection from user input.
        cur.execute("""
            INSERT INTO transactions (date, type, category_id, amount, description)
            VALUES (?, ?, ?, ?, ?)
        """, (date, type_, category_id, float(amount), description))

        conn.commit()
        conn.close()

    def get_transactions(self):
        """Return all transactions joined with their category names.

        Each row is a tuple of (id, date, type, category_name, amount, description),
        ordered by date then insertion order.
        """
        conn = self.get_connection()
        cur = conn.cursor()

        # JOIN resolves category_id to its readable name so the UI never has to look it up.
        # COALESCE turns a NULL description into an empty string for safe display.
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
        """Update all fields of an existing transaction identified by transaction_id."""
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
        """Permanently remove a transaction by its ID."""
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))

        conn.commit()
        conn.close()

import tkinter as tk
from tkinter import ttk

from database import FinanceDatabase
from windows.dashboard import DashboardWindow
from windows.add_expense import AddExpenseWindow
from windows.add_income import AddIncomeWindow
from windows.history import HistoryWindow
from windows.reports import ReportsWindow
from windows.categories import CategoriesWindow


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance")
        self.geometry("300x380")
        self.resizable(False, False)

        self.db = FinanceDatabase()
        self.db.create_tables()

        self._windows = {}

        self.build_ui()

    def build_ui(self):
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Personal Finance", font=("Tahoma", 16)).pack(pady=(0, 20))

        ttk.Separator(container).pack(fill="x", pady=(0, 10))

        ttk.Button(container, text="Dashboard", command=self.open_dashboard).pack(fill="x", pady=4)
        ttk.Button(container, text="Add Expense", command=self.open_add_expense).pack(fill="x", pady=4)
        ttk.Button(container, text="Add Income", command=self.open_add_income).pack(fill="x", pady=4)
        ttk.Button(container, text="Transactions", command=self.open_history).pack(fill="x", pady=4)
        ttk.Button(container, text="Reports", command=self.open_reports).pack(fill="x", pady=4)
        ttk.Button(container, text="Categories", command=self.open_categories).pack(fill="x", pady=4)

        ttk.Separator(container).pack(fill="x", pady=(10, 10))

        ttk.Button(container, text="Exit", command=self.destroy).pack(fill="x", pady=4)

    def _open_window(self, key, window_class):
        if key in self._windows and self._windows[key].winfo_exists():
            self._windows[key].lift()
            self._windows[key].focus_set()
            return

        self._windows[key] = window_class(self, self.db)

    def open_dashboard(self):
        self._open_window("dashboard", DashboardWindow)

    def open_add_expense(self):
        self._open_window("add_expense", AddExpenseWindow)

    def open_add_income(self):
        self._open_window("add_income", AddIncomeWindow)

    def open_history(self):
        self._open_window("history", HistoryWindow)

    def open_reports(self):
        self._open_window("reports", ReportsWindow)

    def open_categories(self):
        self._open_window("categories", CategoriesWindow)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
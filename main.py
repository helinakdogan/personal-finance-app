"""Application entry point for Flowance.

MainApp is the root tk.Tk window.  It initialises the database, builds the
navigation grid of ActionCards, and manages a registry of child windows so
that each feature window can only be opened once at a time.
"""

import tkinter as tk

from database import FinanceDatabase
from windows.dashboard import DashboardWindow
from windows.add_expense import AddExpenseWindow
from windows.add_income import AddIncomeWindow
from windows.history import HistoryWindow
from windows.reports import ReportsWindow
from windows.categories import CategoriesWindow
from windows.custom_components import ActionCard
from windows.custom_components.theme import (
    BG_PAGE as BG, SURFACE, TEXT, MUTED, SOFT, CYAN, BLUE, PURPLE, PINK, SLATE, FONT
)
from PIL import Image, ImageTk

APP_NAME = "Flowance"


class MainApp(tk.Tk):
    """Root application window for Flowance.

    Initialises the database, renders the navigation grid of ActionCards,
    and maintains a registry of child windows so that each screen can be
    opened at most once at a time.
    """

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.iconphoto(True, tk.PhotoImage(file="assets/logo_icon.png"))
        self.geometry("960x640")
        self.minsize(840, 580)
        self.configure(bg=BG)

        # Open the database and ensure schema + default categories exist before any window needs them.
        self.db = FinanceDatabase()
        self.db.create_tables()

        # Registry keyed by window name; lets _open_window guarantee one instance per feature.
        self._windows = {}
        self.build_ui()

    def build_ui(self):
        """Construct the logo header and the six-card navigation grid."""
        # Make the single root cell stretch so the page frame fills the window on resize.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        page = tk.Frame(self, bg=BG)
        page.grid(row=0, column=0, sticky="nsew", padx=64, pady=48)
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        header = tk.Frame(page, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 38))
        header.grid_columnconfigure(0, weight=1)

        image = Image.open("assets/logo.png")
        image.thumbnail((180, 60))

        self.logo = ImageTk.PhotoImage(image)

        logo_label = tk.Label(
            header,
            image=self.logo,
            bg=BG
        )
        logo_label.grid(row=0, column=0, sticky="w")

        title = tk.Label(
            header,
            text="Your money,\nclearly organized.",
            bg=BG,
            fg=TEXT,
            font=(FONT, 40, "bold"),
            justify="left"
        )
        title.grid(row=1, column=0, sticky="w", pady=(10, 10))

        subtitle = tk.Label(
            header,
            text="A simple desktop workspace for income, expenses, categories and reports.",
            bg=BG,
            fg=MUTED,
            font=(FONT, 13),
            justify="left"
        )
        subtitle.grid(row=2, column=0, sticky="w")

        close_btn = tk.Button(
            header,
            text="Close",
            command=self.destroy,
            bg=SOFT,
            fg=TEXT,
            activebackground="#E5E7EB",
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            font=(FONT, 10),
            cursor="hand2"
        )
        close_btn.grid(row=0, column=1, sticky="ne")

        grid = tk.Frame(page, bg=BG)
        grid.grid(row=1, column=0, sticky="nsew")
        # uniform="cards" forces all three columns to equal width so the cards line up evenly.
        for i in range(3):
            grid.grid_columnconfigure(i, weight=1, uniform="cards")

        # Single source of truth for the nav cards: (title, subtitle, accent colour, click handler).
        actions = [
            ("Dashboard", "See balance, totals and recent activity.", BLUE, self.open_dashboard),
            ("Add Expense", "Record spending with category and note.", PINK, self.open_add_expense),
            ("Add Income", "Add salary, freelance or other income.", CYAN, self.open_add_income),
            ("Transactions", "Review, edit and delete records.", SLATE, self.open_history),
            ("Reports", "View charts and monthly insights.", PURPLE, self.open_reports),
            ("Categories", "Manage labels for cleaner tracking.", BLUE, self.open_categories),
        ]

        for index, (title, subtitle, accent, command) in enumerate(actions):
            card = ActionCard(grid, title, subtitle, accent, command)
            # Lay out 3 cards per row: integer division picks the row, modulo picks the column.
            card.grid(
                row=index // 3,
                column=index % 3,
                sticky="nsew",
                padx=10,
                pady=10,
                ipady=10
            )

    def _open_window(self, key, window_class):
        """Open a child window, or focus it if it is already open.

        Parameters
        ----------
        key : str
            Unique identifier for the window type (e.g. 'dashboard').
        window_class : type
            The Toplevel subclass to instantiate when no existing window is found.
        """
        # If a window of this type is already open, bring it to front instead of opening a duplicate.
        # winfo_exists() guards against a stale reference left behind after the user closed it.
        if key in self._windows and self._windows[key].winfo_exists():
            self._windows[key].lift()
            self._windows[key].focus_set()
            return

        # No live window for this key: create one and remember it in the registry.
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

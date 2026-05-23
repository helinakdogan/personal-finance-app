import tkinter as tk

from database import FinanceDatabase
from windows.dashboard import DashboardWindow
from windows.add_expense import AddExpenseWindow
from windows.add_income import AddIncomeWindow
from windows.history import HistoryWindow
from windows.reports import ReportsWindow
from windows.categories import CategoriesWindow
from PIL import Image, ImageTk

APP_NAME = "Flowance"

BG = "#F8FAFC"
SURFACE = "#FFFFFF"

TEXT = "#0F172A"
MUTED = "#64748B"

SOFT = "#F1F5F9"

CYAN = "#7DD3FC"
BLUE = "#60A5FA"
PURPLE = "#818CF8"
PINK = "#F9A8D4"

SLATE = "#94A3B8"
FONT = "Inter"




class ActionCard(tk.Frame):
    def __init__(self, parent, title, subtitle, accent, command):
        super().__init__(parent, bg=SURFACE, cursor="hand2")

        self.command = command
        self.accent = accent
        self.default_bg = SURFACE
        self.hover_bg = "#F8FAFC"

        self.configure(padx=22, pady=20)

        self.dot = tk.Frame(self, bg=accent, width=9, height=9)
        self.dot.grid(row=0, column=0, sticky="w", pady=(0, 18))
        self.dot.grid_propagate(False)

        self.title_label = tk.Label(
            self,
            text=title,
            bg=SURFACE,
            fg=TEXT,
            font=(FONT, 15, "bold"),
            anchor="w"
        )
        self.title_label.grid(row=1, column=0, sticky="w")

        self.subtitle_label = tk.Label(
            self,
            text=subtitle,
            bg=SURFACE,
            fg=MUTED,
            font=(FONT, 10),
            anchor="w",
            justify="left",
            wraplength=180
        )
        self.subtitle_label.grid(row=2, column=0, sticky="w", pady=(8, 0))

        self.grid_columnconfigure(0, weight=1)

        for widget in (self, self.dot, self.title_label, self.subtitle_label):
            widget.bind("<Button-1>", self.on_click)
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)

    def on_click(self, event=None):
        self.command()

    def on_enter(self, event=None):
        self.configure(bg=self.hover_bg)
        self.title_label.configure(bg=self.hover_bg, fg=self.accent)
        self.subtitle_label.configure(bg=self.hover_bg)

    def on_leave(self, event=None):
        self.configure(bg=self.default_bg)
        self.title_label.configure(bg=self.default_bg, fg=TEXT)
        self.subtitle_label.configure(bg=self.default_bg)


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.iconphoto(True, tk.PhotoImage(file="assets/logo_icon.png"))
        self.geometry("1100x740")
        self.minsize(920, 640)
        self.configure(bg=BG)

        self.db = FinanceDatabase()
        self.db.create_tables()

        self._windows = {}
        self.build_ui()

    def build_ui(self):
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
        for i in range(3):
            grid.grid_columnconfigure(i, weight=1, uniform="cards")


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
            card.grid(
                row=index // 3,
                column=index % 3,
                sticky="nsew",
                padx=10,
                pady=10,
                ipady=10
            )

      

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
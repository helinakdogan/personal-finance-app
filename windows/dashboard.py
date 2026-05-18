import tkinter as tk
from tkinter import ttk


BG = "#F8FAFC"
SURFACE = "#FFFFFF"
TEXT = "#0F172A"
MUTED = "#64748B"
SOFT = "#F1F5F9"

BLUE = "#60A5FA"
CYAN = "#7DD3FC"
PURPLE = "#818CF8"
PINK = "#F9A8D4"

FONT = "Inter"


class SummaryCard(tk.Frame):
    def __init__(self, parent, label, value_var, accent):
        super().__init__(parent, bg=SURFACE, padx=22, pady=18)

        self.dot = tk.Frame(self, bg=accent, width=9, height=9)
        self.dot.grid(row=0, column=0, sticky="w", pady=(0, 16))
        self.dot.grid_propagate(False)

        tk.Label(
            self,
            text=label,
            bg=SURFACE,
            fg=MUTED,
            font=(FONT, 10),
            anchor="w"
        ).grid(row=1, column=0, sticky="w")

        tk.Label(
            self,
            textvariable=value_var,
            bg=SURFACE,
            fg=TEXT,
            font=(FONT, 20, "bold"),
            anchor="w"
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))

        self.grid_columnconfigure(0, weight=1)


class DashboardWindow(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)

        self.title("Dashboard")
        self.iconphoto(True, tk.PhotoImage(file="assets/logo_icon.png"))
        self.geometry("820x560")
        self.minsize(720, 500)
        self.configure(bg=BG)

        self.db = db

        self.var_income = tk.StringVar(value="₺0.00")
        self.var_expense = tk.StringVar(value="₺0.00")
        self.var_balance = tk.StringVar(value="₺0.00")

        self.build_ui()
        self.load_data()

    def build_ui(self):
        page = tk.Frame(self, bg=BG)
        page.pack(fill="both", expand=True, padx=42, pady=34)

        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)

        header = tk.Frame(page, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 28))
        header.grid_columnconfigure(0, weight=1)

        tk.Label(
            header,
            text="Dashboard",
            bg=BG,
            fg=TEXT,
            font=(FONT, 32, "bold")
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            header,
            text="A quick overview of your income, expenses and latest transactions.",
            bg=BG,
            fg=MUTED,
            font=(FONT, 12)
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

        refresh_btn = tk.Button(
            header,
            text="Refresh",
            command=self.load_data,
            bg=SOFT,
            fg=TEXT,
            activebackground="#E2E8F0",
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            font=(FONT, 10),
            cursor="hand2"
        )
        refresh_btn.grid(row=0, column=1, sticky="ne")

        summary = tk.Frame(page, bg=BG)
        summary.grid(row=1, column=0, sticky="ew", pady=(0, 28))

        for i in range(3):
            summary.grid_columnconfigure(i, weight=1, uniform="summary")

        SummaryCard(summary, "Total Income", self.var_income, CYAN).grid(
            row=0, column=0, sticky="nsew", padx=(0, 10)
        )
        SummaryCard(summary, "Total Expenses", self.var_expense, PINK).grid(
            row=0, column=1, sticky="nsew", padx=10
        )
        SummaryCard(summary, "Balance", self.var_balance, PURPLE).grid(
            row=0, column=2, sticky="nsew", padx=(10, 0)
        )

        recent_section = tk.Frame(page, bg=SURFACE, padx=22, pady=20)
        recent_section.grid(row=2, column=0, sticky="nsew")
        recent_section.grid_columnconfigure(0, weight=1)
        recent_section.grid_rowconfigure(1, weight=1)

        tk.Label(
            recent_section,
            text="Recent Transactions",
            bg=SURFACE,
            fg=TEXT,
            font=(FONT, 16, "bold")
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            recent_section,
            text="Last 5 records added to your finance history.",
            bg=SURFACE,
            fg=MUTED,
            font=(FONT, 10)
        ).grid(row=0, column=1, sticky="e")

        table_frame = tk.Frame(recent_section, bg=SURFACE)
        table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(18, 0))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()

        style.layout("Flowance.Treeview", [
        ("Flowance.Treeview.treearea", {"sticky": "nswe"})
        ])
        
        
        style.configure(
            "Flowance.Treeview",
            font=(FONT, 10),
            rowheight=32,
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=TEXT,
            borderwidth=0,
            relief="flat"
        )
        style.configure(
            "Flowance.Treeview.Heading",
            font=(FONT, 10, "bold"),
            foreground=MUTED,
            background=SURFACE,
            borderwidth=0
        )
        style.map(
            "Flowance.Treeview",
            background=[("selected", "#EEF2FF")],
            foreground=[("selected", TEXT)]
        )

        self.tv = ttk.Treeview(
            table_frame,
            height=5,
            show="headings",
            style="Flowance.Treeview"
        )
        self.tv["columns"] = ("date", "type", "category", "amount")
        self.tv["selectmode"] = "none"

        headings = {
            "date": ("Date", 160, "w"),
            "type": ("Type", 160, "w"),
            "category": ("Category", 220, "w"),
            "amount": ("Amount", 160, "w"),
        }

        for column, (label, width, anchor) in headings.items():
            self.tv.heading(column, text=label, anchor="w")
            self.tv.column(column, width=width, anchor=anchor, stretch=True)
    
        self.tv.grid(row=0, column=0, sticky="nsew")

    def load_data(self):
        transactions = self.db.get_transactions()

        total_income = 0
        total_expense = 0

        for t in transactions:
            if t[2] == "Income":
                total_income += t[4]
            elif t[2] == "Expense":
                total_expense += t[4]

        balance = total_income - total_expense

        self.var_income.set(f"₺{total_income:.2f}")
        self.var_expense.set(f"₺{total_expense:.2f}")
        self.var_balance.set(f"₺{balance:.2f}")

        for item in self.tv.get_children():
            self.tv.delete(item)

        recent = transactions[-5:]
        for t in recent:
            self.tv.insert(
                parent="",
                index="end",
                values=(t[1], t[2], t[3], f"₺{t[4]:.2f}")
            )
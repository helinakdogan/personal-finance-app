import tkinter as tk
from tkinter import ttk


class DashboardWindow(tk.Toplevel):

    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Dashboard")
        self.geometry("420x370")
        self.resizable(False, False)

        self.db = db

        self.var_income  = tk.StringVar(value="₺0.00")
        self.var_expense = tk.StringVar(value="₺0.00")
        self.var_balance = tk.StringVar(value="₺0.00")

        self.build_ui()
        self.load_data()

    def build_ui(self):
        container = ttk.Frame(self, padding=10)
        container.pack(fill="both", expand=True)

        frm_summary = ttk.LabelFrame(container, text="Summary")
        frm_summary.pack(fill="x", pady=(0, 10))
        frm_summary.columnconfigure(0, weight=1)
        frm_summary.columnconfigure(1, weight=1)

        lbl_pad = {"padx": (10, 5), "pady": 6, "sticky": "w"}
        val_pad = {"padx": (5, 10), "pady": 6, "sticky": "e"}

        ttk.Label(frm_summary, text="Total Income:").grid(row=0, column=0, **lbl_pad)
        ttk.Label(frm_summary, textvariable=self.var_income).grid(row=0, column=1, **val_pad)

        ttk.Label(frm_summary, text="Total Expenses:").grid(row=1, column=0, **lbl_pad)
        ttk.Label(frm_summary, textvariable=self.var_expense).grid(row=1, column=1, **val_pad)

        ttk.Separator(frm_summary).grid(row=2, column=0, columnspan=2, sticky="ew", padx=10)

        ttk.Label(frm_summary, text="Balance:", font=("Tahoma", 10, "bold")).grid(row=3, column=0, **lbl_pad)
        ttk.Label(frm_summary, textvariable=self.var_balance, font=("Tahoma", 10, "bold")).grid(row=3, column=1, **val_pad)

        frm_recent = ttk.LabelFrame(container, text="Recent Transactions (Last 5)")
        frm_recent.pack(fill="both", expand=True, pady=(0, 10))

        self.tv = ttk.Treeview(frm_recent, height=5, show="headings")
        self.tv["columns"] = ("date", "type", "category", "amount")
        self.tv["selectmode"] = "none"

        self.tv.heading("date",     text="Date",     anchor="center")
        self.tv.heading("type",     text="Type",     anchor="center")
        self.tv.heading("category", text="Category", anchor="w")
        self.tv.heading("amount",   text="Amount",   anchor="e")

        self.tv.column("date",     width=90,  anchor="center")
        self.tv.column("type",     width=70,  anchor="center")
        self.tv.column("category", width=120, anchor="w")
        self.tv.column("amount",   width=90,  anchor="e")

        self.tv.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Button(container, text="Refresh", command=self.load_data).pack()

    def load_data(self):
        transactions = self.db.get_transactions()

        total_income  = 0
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
            self.tv.insert(parent="", index="end", values=(t[1], t[2], t[3], f"₺{t[4]:.2f}"))

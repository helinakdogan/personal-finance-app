import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ReportsWindow(tk.Toplevel):

    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Reports")
        self.geometry("600x480")

        self.db = db

        self.build_ui()
        self.draw_charts()

    def build_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_pie = ttk.Frame(self.notebook)
        self.tab_bar = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_pie, text="Expenses by Category")
        self.notebook.add(self.tab_bar, text="Monthly Overview")

        ttk.Button(self, text="Refresh", command=self.draw_charts).pack(pady=(0, 10))

    def draw_charts(self):
        self.draw_pie_chart()
        self.draw_bar_chart()

    def draw_pie_chart(self):
        for widget in self.tab_pie.winfo_children():
            widget.destroy()

        transactions = self.db.get_transactions()
        expenses = [t for t in transactions if t[2] == "Expense"]

        totals = {}
        for t in expenses:
            totals[t[3]] = totals.get(t[3], 0) + t[4]

        fig = Figure(figsize=(5, 4))
        ax  = fig.add_subplot(111)

        if totals:
            ax.pie(totals.values(), labels=totals.keys(), autopct="%1.1f%%")
            ax.set_title("Expenses by Category")
        else:
            ax.text(0.5, 0.5, "No expense data available", ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_title("Expenses by Category")

        canvas = FigureCanvasTkAgg(fig, master=self.tab_pie)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw_bar_chart(self):
        for widget in self.tab_bar.winfo_children():
            widget.destroy()

        transactions = self.db.get_transactions()

        monthly = {}
        for t in transactions:
            month = t[1][:7]
            if month not in monthly:
                monthly[month] = {"Income": 0.0, "Expense": 0.0}
            monthly[month][t[2]] += t[4]

        months   = sorted(monthly.keys())
        incomes  = [monthly[m]["Income"]  for m in months]
        expenses = [monthly[m]["Expense"] for m in months]

        fig = Figure(figsize=(5, 4))
        ax  = fig.add_subplot(111)

        if months:
            x     = list(range(len(months)))
            width = 0.35
            ax.bar([i - width / 2 for i in x], incomes,  width, label="Income")
            ax.bar([i + width / 2 for i in x], expenses, width, label="Expense")
            ax.set_xticks(x)
            ax.set_xticklabels(months, rotation=45, ha="right")
            ax.set_title("Monthly Income vs Expense")
            ax.legend()
            fig.tight_layout()
        else:
            ax.text(0.5, 0.5, "No transaction data available", ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_title("Monthly Income vs Expense")

        canvas = FigureCanvasTkAgg(fig, master=self.tab_bar)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

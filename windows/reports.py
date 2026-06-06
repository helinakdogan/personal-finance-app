"""Reports window — visual analysis of income and expenses.

Two chart views are available, selectable via tab buttons:
  - Expenses by Category: a pie chart showing the share of each expense label.
  - Monthly Overview: a grouped bar chart comparing income and expenses per month.

Matplotlib figures are rendered inside a FigureCanvasTkAgg widget embedded
directly in the Tkinter layout.  Switching tabs destroys the previous canvas
and draws a fresh figure.
"""

import tkinter as tk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from windows.custom_components.theme import (
    SURFACE, TEXT, MUTED, INPUT, INPUT_HOVER,
    PURPLE, CYAN, PINK, GREEN, SLATE, FONT
)

BG = SURFACE


class ReportsWindow(tk.Toplevel):
    """Displays income and expense analysis via pie and bar charts.

    Parameters
    ----------
    parent : tk.Tk
        The root application window.
    db : FinanceDatabase
        The shared database instance used to fetch transaction data.
    """

    def __init__(self, parent, db):
        super().__init__(parent)

        self.title("Reports")
        self.geometry("960x660")
        self.minsize(820, 560)
        self.configure(bg=BG)

        self.db = db
        self.active_tab = tk.StringVar(value="category")
        self.chart_canvas = None

        self.build_ui()
        self.draw_charts()

    def build_ui(self):
        """Construct the header, tab buttons, and chart container."""
        page = tk.Frame(self, bg=BG)
        page.pack(fill="both", expand=True, padx=58, pady=46)
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)

        header = tk.Frame(page, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 32))
        header.grid_columnconfigure(0, weight=1)

        accent = tk.Frame(header, bg=PURPLE, width=10, height=10)
        accent.grid(row=0, column=0, sticky="w", pady=(0, 14))
        accent.grid_propagate(False)

        tk.Label(
            header,
            text="Reports",
            bg=BG,
            fg=TEXT,
            font=(FONT, 36, "bold")
        ).grid(row=1, column=0, sticky="w")

        tk.Label(
            header,
            text="Visualize your spending by category and compare monthly income versus expenses.",
            bg=BG,
            fg=MUTED,
            font=(FONT, 13)
        ).grid(row=2, column=0, sticky="w", pady=(10, 0))

        refresh_btn = self.create_button(
            header,
            "Refresh",
            self.draw_charts,
            bg=INPUT,
            fg=TEXT
        )
        refresh_btn.grid(row=1, column=1, sticky="e")

        tabs = tk.Frame(page, bg=BG)
        tabs.grid(row=1, column=0, sticky="w", pady=(0, 24))

        self.category_btn = self.create_tab_button(tabs, "Expenses by Category", "category")
        self.category_btn.pack(side="left", padx=(0, 10))

        self.monthly_btn = self.create_tab_button(tabs, "Monthly Overview", "monthly")
        self.monthly_btn.pack(side="left")

        chart_area = tk.Frame(page, bg=SURFACE)
        chart_area.grid(row=2, column=0, sticky="nsew")
        chart_area.grid_columnconfigure(0, weight=1)
        chart_area.grid_rowconfigure(0, weight=1)

        self.chart_container = tk.Frame(chart_area, bg=SURFACE)
        self.chart_container.grid(row=0, column=0, sticky="nsew")

        self.update_tab_styles()

    def create_button(self, parent, text, command, bg, fg):
        """Create and return a standard action button."""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=INPUT_HOVER,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            padx=24,
            pady=12,
            font=(FONT, 10, "bold"),
            cursor="hand2"
        )

    def create_tab_button(self, parent, text, value):
        """Create and return a tab toggle button for the given chart view."""
        return tk.Button(
            parent,
            text=text,
            command=lambda: self.switch_tab(value),
            relief="flat",
            bd=0,
            padx=20,
            pady=11,
            font=(FONT, 10, "bold"),
            cursor="hand2"
        )

    def switch_tab(self, value):
        """Set the active tab and redraw the corresponding chart."""
        self.active_tab.set(value)
        self.update_tab_styles()
        self.draw_charts()

    def update_tab_styles(self):
        """Apply active/inactive visual state to the tab buttons."""
        active = self.active_tab.get()

        buttons = [
            (self.category_btn, "category"),
            (self.monthly_btn, "monthly"),
        ]

        for button, value in buttons:
            if active == value:
                button.configure(
                    bg=TEXT, fg="#FFFFFF",
                    activebackground="#1E293B", activeforeground="#FFFFFF"
                )
            else:
                button.configure(
                    bg=INPUT, fg=TEXT,
                    activebackground=INPUT_HOVER, activeforeground=TEXT
                )

    def clear_chart(self):
        """Destroy all widgets inside the chart container and reset the canvas reference."""
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        self.chart_canvas = None

    def draw_charts(self):
        """Dispatch to the appropriate chart method based on the active tab."""
        if self.active_tab.get() == "category":
            self.draw_pie_chart()
        else:
            self.draw_bar_chart()

    def style_figure(self, fig, ax):
        """Apply the application colour theme to a Matplotlib Figure and Axes pair."""
        fig.patch.set_facecolor(SURFACE)
        ax.set_facecolor(SURFACE)
        ax.title.set_color(TEXT)
        ax.tick_params(colors=MUTED)

        for spine in ax.spines.values():
            spine.set_visible(False)

    def show_empty_state(self, title, message):
        """Render a placeholder message when no data is available for the active chart."""
        self.clear_chart()

        empty = tk.Frame(self.chart_container, bg=SURFACE)
        empty.pack(fill="both", expand=True)

        tk.Label(
            empty,
            text=title,
            bg=SURFACE,
            fg=TEXT,
            font=(FONT, 22, "bold")
        ).pack(anchor="center", pady=(150, 10))

        tk.Label(
            empty,
            text=message,
            bg=SURFACE,
            fg=MUTED,
            font=(FONT, 12)
        ).pack(anchor="center")

    def draw_pie_chart(self):
        """Render a pie chart showing the expense total for each category."""
        self.clear_chart()

        transactions = self.db.get_transactions()
        expenses = [t for t in transactions if t[2] == "Expense"]

        totals = {}
        for t in expenses:
            totals[t[3]] = totals.get(t[3], 0) + float(t[4])

        if not totals:
            self.show_empty_state(
                "No expense data yet",
                "Add expenses first to see category distribution."
            )
            return

        fig = Figure(figsize=(7.6, 4.6), dpi=100)
        ax = fig.add_subplot(111)
        self.style_figure(fig, ax)

        colors = [PINK, PURPLE, CYAN, GREEN, SLATE, "#C4B5FD", "#BAE6FD", "#FBCFE8"]

        wedges, texts, autotexts = ax.pie(
            totals.values(),
            labels=totals.keys(),
            autopct="%1.1f%%",
            startangle=90,
            colors=colors[:len(totals)],
            textprops={"color": TEXT, "fontsize": 9, "fontname": FONT},
            wedgeprops={"linewidth": 2, "edgecolor": SURFACE}
        )

        for autotext in autotexts:
            autotext.set_color(TEXT)
            autotext.set_fontsize(9)

        ax.set_title("Expenses by Category", fontsize=16, fontweight="bold", pad=20)
        ax.axis("equal")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.chart_canvas = canvas

    def draw_bar_chart(self):
        """Render a grouped bar chart comparing monthly income and expenses."""
        self.clear_chart()

        transactions = self.db.get_transactions()

        monthly = {}
        for t in transactions:
            month = t[1][:7]  # YYYY-MM key extracted from the full YYYY-MM-DD date

            if month not in monthly:
                monthly[month] = {"Income": 0.0, "Expense": 0.0}

            monthly[month][t[2]] += float(t[4])

        if not monthly:
            self.show_empty_state(
                "No monthly data yet",
                "Add income or expenses first to generate reports."
            )
            return

        months = sorted(monthly.keys())
        incomes = [monthly[m]["Income"] for m in months]
        expenses = [monthly[m]["Expense"] for m in months]

        fig = Figure(figsize=(7.6, 4.6), dpi=100)
        ax = fig.add_subplot(111)
        self.style_figure(fig, ax)

        x = list(range(len(months)))
        width = 0.35

        ax.bar([i - width / 2 for i in x], incomes,  width, label="Income",  color=GREEN)
        ax.bar([i + width / 2 for i in x], expenses, width, label="Expense", color=PINK)

        ax.set_title("Monthly Income vs Expense", fontsize=16, fontweight="bold", pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(months, rotation=0, ha="center")
        ax.tick_params(axis="x", labelsize=9)
        ax.tick_params(axis="y", labelsize=9)
        ax.grid(axis="y", color=INPUT, linewidth=1)
        ax.legend(frameon=False, loc="upper right", fontsize=10)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.chart_canvas = canvas

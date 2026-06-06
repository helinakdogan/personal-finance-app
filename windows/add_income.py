"""Add Income window — form for recording a new income transaction.

Mirrors AddExpenseWindow in structure; category list is filtered to
Income-type entries only.  Validation is handled by TransactionValidator.
"""

import tkinter as tk
from tkinter import messagebox as msg
from datetime import date, datetime

from validators import TransactionValidator, ValidationError
from windows.custom_components import SelectBox, DateInput
from windows.custom_components.theme import (
    SURFACE, TEXT, MUTED, INPUT, INPUT_HOVER, CYAN as GREEN, SOFT_GREEN, FONT
)

BG = SURFACE


class AddIncomeWindow(tk.Toplevel):
    """Form window for recording a new income transaction.

    Mirrors AddExpenseWindow in structure; the category list is filtered to
    Income-type entries only and the date picker highlight uses SOFT_GREEN
    instead of SOFT_PINK.

    Parameters
    ----------
    parent : tk.Tk
        The root application window.
    db : FinanceDatabase
        The shared database instance used to persist the new transaction.
    """

    def __init__(self, parent, db):
        super().__init__(parent)

        self.title("Add Income")
        self.iconphoto(True, tk.PhotoImage(file="assets/logo_icon.png"))
        self.geometry("760x640")
        self.minsize(680, 560)
        self.configure(bg=BG)

        self.db = db

        self.var_amount = tk.StringVar()
        self.var_category = tk.StringVar()
        self.var_date = tk.StringVar(value=date.today().strftime("%m.%d.%Y"))
        self.var_description = tk.StringVar()

        self.categories = []

        self.build_ui()
        self.load_categories()

    def build_ui(self):
        """Construct the header and form fields: amount, source category, date, and note."""
        page = tk.Frame(self, bg=BG)
        page.pack(fill="both", expand=True, padx=58, pady=46)
        page.grid_columnconfigure(0, weight=1)

        header = tk.Frame(page, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 36))
        header.grid_columnconfigure(0, weight=1)

        accent = tk.Frame(header, bg=GREEN, width=10, height=10)
        accent.grid(row=0, column=0, sticky="w", pady=(0, 14))
        accent.grid_propagate(False)

        tk.Label(
            header,
            text="Add Income",
            bg=BG,
            fg=TEXT,
            font=(FONT, 36, "bold")
        ).grid(row=1, column=0, sticky="w")

        tk.Label(
            header,
            text="Add salary, freelance income or other sources.",
            bg=BG,
            fg=MUTED,
            font=(FONT, 13)
        ).grid(row=2, column=0, sticky="w", pady=(10, 0))

        form = tk.Frame(page, bg=SURFACE)
        form.grid(row=1, column=0, sticky="nsew")
        form.grid_columnconfigure(0, weight=1)

        self.amount_entry = self.create_input(form, 0, "Amount*", self.var_amount, "Example: 15000")
        self.category_box = self.create_select(form, 1, "Source*", self.var_category)
        self.date_entry = self.create_date_input(form, 2, "Date*")
        self.note_entry = self.create_input(form, 3, "Note", self.var_description)

        actions = tk.Frame(form, bg=SURFACE)
        actions.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        actions.grid_columnconfigure(0, weight=1)

        self.create_button(actions, "Clear", self.clear_form, bg=INPUT, fg=TEXT).grid(row=0, column=0, sticky="w")
        self.create_button(actions, "Save Income", self.on_save, bg=TEXT, fg="#FFFFFF").grid(row=0, column=1, sticky="e")

    def create_button(self, parent, text, command, bg, fg):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground="#1E293B" if fg == "#FFFFFF" else INPUT_HOVER,
            activeforeground=fg,
            relief="flat",
            bd=0,
            padx=24,
            pady=13,
            font=(FONT, 11, "bold"),
            cursor="hand2"
        )

    def create_field_wrapper(self, parent, row, label):
        wrapper = tk.Frame(parent, bg=SURFACE)
        wrapper.grid(row=row, column=0, sticky="ew", pady=(0, 22))
        wrapper.grid_columnconfigure(0, weight=1)

        tk.Label(
            wrapper,
            text=label,
            bg=SURFACE,
            fg=TEXT,
            font=(FONT, 11, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        return wrapper

    def create_input(self, parent, row, label, variable, helper=""):
        wrapper = self.create_field_wrapper(parent, row, label)

        entry_box = tk.Frame(wrapper, bg=INPUT)
        entry_box.grid(row=1, column=0, sticky="ew")
        entry_box.grid_columnconfigure(0, weight=1)

        entry = tk.Entry(
            entry_box,
            textvariable=variable,
            bg=INPUT,
            fg=TEXT,
            relief="flat",
            bd=0,
            font=(FONT, 12),
            insertbackground=TEXT
        )
        entry.grid(row=0, column=0, sticky="ew", padx=16, pady=13)

        if helper:
            tk.Label(
                wrapper,
                text=helper,
                bg=SURFACE,
                fg=MUTED,
                font=(FONT, 9)
            ).grid(row=2, column=0, sticky="w", pady=(6, 0))

        return entry

    def create_select(self, parent, row, label, variable):
        wrapper = self.create_field_wrapper(parent, row, label)

        select = SelectBox(wrapper, variable, empty_text="No sources")
        select.grid(row=1, column=0, sticky="ew")

        return select

    def create_date_input(self, parent, row, label):
        wrapper = self.create_field_wrapper(parent, row, label)

        date_input = DateInput(wrapper, self.var_date, today_bg=SOFT_GREEN)
        date_input.grid(row=1, column=0, sticky="ew")

        tk.Label(
            wrapper,
            text="MM.DD.YYYY",
            bg=SURFACE,
            fg=MUTED,
            font=(FONT, 9)
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))

        return date_input

    def load_categories(self):
        """Populate the source dropdown with all Income-type categories."""
        self.categories = [c for c in self.db.get_categories() if c[2] == "Income"]
        names = [c[1] for c in self.categories]

        self.category_box.set_values(names)

        if names:
            self.var_category.set(names[0])
        else:
            self.var_category.set("No source")

    def convert_date_for_db(self, value):
        """Convert a user-facing MM.DD.YYYY date string to the database YYYY-MM-DD format."""
        parsed = datetime.strptime(value, "%m.%d.%Y")
        return parsed.strftime("%Y-%m-%d")

    def clear_form(self):
        """Reset all form fields to their default values."""
        self.var_amount.set("")
        self.var_description.set("")
        self.var_date.set(date.today().strftime("%m.%d.%Y"))

        if self.categories:
            self.var_category.set(self.categories[0][1])

    def on_save(self):
        """Validate all fields and write the new income record to the database."""
        try:
            db_date = self.convert_date_for_db(self.var_date.get())

            clean = TransactionValidator.validate(
                db_date,
                "Income",
                self.var_category.get(),
                self.var_amount.get(),
                self.var_description.get(),
            )

            category_id = None
            for c in self.categories:
                if c[1] == clean[2]:
                    category_id = c[0]
                    break

            if category_id is None:
                msg.showwarning("Validation Error", "Selected source was not found.", parent=self)
                return

            self.db.add_transaction(clean[0], clean[1], category_id, clean[3], clean[4])
            msg.showinfo("Success", "Income added successfully.", parent=self)
            self.clear_form()

        except ValueError:
            msg.showwarning("Validation Error", "Date must be in MM.DD.YYYY format.", parent=self)
        except ValidationError as e:
            msg.showwarning("Validation Error", str(e), parent=self)
        except Exception as e:
            msg.showerror("System Error", str(e), parent=self)

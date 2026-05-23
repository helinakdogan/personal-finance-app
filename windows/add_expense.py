import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
from datetime import date

from validators import TransactionValidator, ValidationError


BG = "#FFFFFF"
SURFACE = "#FFFFFF"
TEXT = "#0F172A"
MUTED = "#64748B"
INPUT = "#F3F6FA"
INPUT_HOVER = "#EEF2F7"
PINK = "#F9A8D4"

FONT = "Inter"


class AddExpenseWindow(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)

        self.title("Add Expense")
        self.iconphoto(True, tk.PhotoImage(file="assets/logo_icon.png"))
        self.geometry("880x740")
        self.minsize(760, 640)
        self.configure(bg=BG)

        self.db = db

        self.var_amount = tk.StringVar()
        self.var_category = tk.StringVar()
        self.var_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.var_description = tk.StringVar()

        self.categories = []

        self.build_ui()
        self.load_categories()

    def build_ui(self):
        page = tk.Frame(self, bg=BG)
        page.pack(fill="both", expand=True, padx=58, pady=46)
        page.grid_columnconfigure(0, weight=1)

        header = tk.Frame(page, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 36))
        header.grid_columnconfigure(0, weight=1)

        accent = tk.Frame(header, bg=PINK, width=10, height=10)
        accent.grid(row=0, column=0, sticky="w", pady=(0, 14))
        accent.grid_propagate(False)

        tk.Label(
            header,
            text="Add Expense",
            bg=BG,
            fg=TEXT,
            font=(FONT, 36, "bold")
        ).grid(row=1, column=0, sticky="w")

        tk.Label(
            header,
            text="Record a new spending item with category, date and note.",
            bg=BG,
            fg=MUTED,
            font=(FONT, 13)
        ).grid(row=2, column=0, sticky="w", pady=(10, 0))

        form = tk.Frame(page, bg=SURFACE)
        form.grid(row=1, column=0, sticky="nsew")
        form.grid_columnconfigure(0, weight=1)

        self.amount_entry = self.create_input(form, 0, "Amount*", self.var_amount, "Example: 250")
        self.category_box = self.create_select(form, 1, "Category*", self.var_category)
        self.date_entry = self.create_date_input(form, 2, "Date*", self.var_date)
        self.note_entry = self.create_input(form, 3, "Note", self.var_description)

        actions = tk.Frame(form, bg=SURFACE)
        actions.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        actions.grid_columnconfigure(0, weight=1)

        self.create_button(actions, "Clear", self.clear_form, bg=INPUT, fg=TEXT).grid(row=0, column=0, sticky="w")
        self.create_button(actions, "Save Expense", self.on_save, bg=TEXT, fg="#FFFFFF").grid(row=0, column=1, sticky="e")

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

        combo = ttk.Combobox(
            wrapper,
            textvariable=variable,
            state="readonly",
            font=(FONT, 11)
        )
        combo.grid(row=1, column=0, sticky="ew", ipady=6)

        return combo

    def create_date_input(self, parent, row, label, variable):
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

        tk.Label(
            wrapper,
            text="YYYY-MM-DD",
            bg=SURFACE,
            fg=MUTED,
            font=(FONT, 9)
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))

        return entry

    def load_categories(self):
        self.categories = [c for c in self.db.get_categories() if c[2] == "Expense"]
        names = [c[1] for c in self.categories]

        self.category_box["values"] = names

        if names:
            self.var_category.set(names[0])
        else:
            self.var_category.set("No category")

    def clear_form(self):
        self.var_amount.set("")
        self.var_description.set("")
        self.var_date.set(date.today().strftime("%Y-%m-%d"))

        if self.categories:
            self.var_category.set(self.categories[0][1])

    def on_save(self):
        try:
            clean = TransactionValidator.validate(
                self.var_date.get(),
                "Expense",
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
                msg.showwarning("Validation Error", "Selected category was not found.", parent=self)
                return

            self.db.add_transaction(clean[0], clean[1], category_id, clean[3], clean[4])
            msg.showinfo("Success", "Expense added successfully.", parent=self)
            self.clear_form()

        except ValidationError as e:
            msg.showwarning("Validation Error", str(e), parent=self)
        except Exception as e:
            msg.showerror("System Error", str(e), parent=self)

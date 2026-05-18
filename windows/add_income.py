import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
from datetime import date

from validators import TransactionValidator, ValidationError


class AddIncomeWindow(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Add Income")
        self.geometry("360x280")
        self.resizable(False, False)

        self.db = db

        self.var_amount = tk.StringVar()
        self.var_category = tk.StringVar()
        self.var_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.var_description = tk.StringVar()

        self.categories = []

        self.build_ui()
        self.load_categories()

    def build_ui(self):
        frame = ttk.LabelFrame(self, text="Add Income")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)

        ttk.Label(frame, text="Amount:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        ttk.Entry(frame, textvariable=self.var_amount).grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(frame, text="Source:").grid(row=1, column=0, padx=8, pady=8, sticky="e")
        self.cmb_category = ttk.Combobox(frame, textvariable=self.var_category, state="readonly")
        self.cmb_category.grid(row=1, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(frame, text="Date:").grid(row=2, column=0, padx=8, pady=8, sticky="e")
        ttk.Entry(frame, textvariable=self.var_date).grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(frame, text="Note:").grid(row=3, column=0, padx=8, pady=8, sticky="e")
        ttk.Entry(frame, textvariable=self.var_description).grid(row=3, column=1, padx=8, pady=8, sticky="ew")

        ttk.Button(frame, text="Save", command=self.on_save).grid(row=4, column=1, padx=8, pady=12, sticky="e")

    def load_categories(self):
        self.categories = [c for c in self.db.get_categories() if c[2] == "Income"]
        names = [c[1] for c in self.categories]
        self.cmb_category["values"] = names

        if names:
            self.var_category.set(names[0])

    def on_save(self):
        try:
            clean = TransactionValidator.validate(
                self.var_date.get(),
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
            self.var_amount.set("")
            self.var_description.set("")

        except ValidationError as e:
            msg.showwarning("Validation Error", str(e), parent=self)
        except Exception as e:
            msg.showerror("System Error", str(e), parent=self)
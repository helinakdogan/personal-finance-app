import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg

from validators import TransactionValidator, ValidationError


BG = "#FFFFFF"
SURFACE = "#FFFFFF"
TEXT = "#0F172A"
MUTED = "#64748B"
INPUT = "#F3F6FA"
INPUT_HOVER = "#EEF2F7"
SLATE = "#94A3B8"

FONT = "Inter"


class HistoryWindow(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)

        self.title("Transaction History")
        self.iconphoto(True, tk.PhotoImage(file="assets/logo_icon.png"))
        self.geometry("1080x720")
        self.minsize(880, 600)
        self.configure(bg=BG)

        self.db = db

        self.build_ui()
        self.load_transactions()

    def build_ui(self):
        page = tk.Frame(self, bg=BG)
        page.pack(fill="both", expand=True, padx=58, pady=46)
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        header = tk.Frame(page, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 34))
        header.grid_columnconfigure(0, weight=1)

        accent = tk.Frame(header, bg=SLATE, width=10, height=10)
        accent.grid(row=0, column=0, sticky="w", pady=(0, 14))
        accent.grid_propagate(False)

        tk.Label(
            header,
            text="Transactions",
            bg=BG,
            fg=TEXT,
            font=(FONT, 36, "bold")
        ).grid(row=1, column=0, sticky="w")

        tk.Label(
            header,
            text="View, edit and delete your income and expense records.",
            bg=BG,
            fg=MUTED,
            font=(FONT, 13)
        ).grid(row=2, column=0, sticky="w", pady=(10, 0))

        refresh_btn = self.create_button(
            header,
            "Refresh",
            self.load_transactions,
            bg=INPUT,
            fg=TEXT
        )
        refresh_btn.grid(row=1, column=1, sticky="e")

        table_area = tk.Frame(page, bg=SURFACE)
        table_area.grid(row=1, column=0, sticky="nsew")
        table_area.grid_columnconfigure(0, weight=1)
        table_area.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Flowance.Treeview",
            font=(FONT, 10),
            rowheight=34,
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=TEXT,
            borderwidth=0,
            relief="flat"
        )

        style.configure(
            "Flowance.Treeview.Heading",
            font=(FONT, 10, "bold"),
            background=SURFACE,
            foreground=MUTED,
            borderwidth=0,
            relief="flat"
        )

        style.map(
            "Flowance.Treeview",
            background=[("selected", INPUT)],
            foreground=[("selected", TEXT)]
        )

        self.tv = ttk.Treeview(
            table_area,
            show="headings",
            style="Flowance.Treeview",
            height=12
        )

        self.tv["columns"] = ("date", "type", "category", "amount", "description")
        self.tv["selectmode"] = "browse"

        columns = {
            "date": ("Date", 130, "w"),
            "type": ("Type", 110, "w"),
            "category": ("Category", 170, "w"),
            "amount": ("Amount", 130, "w"),
            "description": ("Description", 280, "w"),
        }

        for key, (label, width, anchor) in columns.items():
            self.tv.heading(key, text=label, anchor="w")
            self.tv.column(key, width=width, anchor=anchor, stretch=True)

        self.tv.grid(row=0, column=0, sticky="nsew")

        actions = tk.Frame(page, bg=BG)
        actions.grid(row=2, column=0, sticky="ew", pady=(24, 0))
        actions.grid_columnconfigure(0, weight=1)

        hint = tk.Label(
            actions,
            text="Select a transaction to edit or delete.",
            bg=BG,
            fg=MUTED,
            font=(FONT, 10)
        )
        hint.grid(row=0, column=0, sticky="w")

        self.btn_edit = self.create_button(
            actions,
            "Edit",
            self.on_edit,
            bg=INPUT,
            fg=TEXT,
            disabled=True
        )
        self.btn_edit.grid(row=0, column=1, sticky="e", padx=(0, 10))

        self.btn_delete = self.create_button(
            actions,
            "Delete",
            self.on_delete,
            bg=TEXT,
            fg="#FFFFFF",
            disabled=True
        )
        self.btn_delete.grid(row=0, column=2, sticky="e")

        self.tv.bind("<<TreeviewSelect>>", self.on_item_select)
        self.tv.bind("<Double-1>", self.on_edit)
        self.tv.bind("<Delete>", self.on_delete)

    def create_button(self, parent, text, command, bg, fg, disabled=False):
        btn = tk.Button(
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
            pady=12,
            font=(FONT, 10, "bold"),
            cursor="hand2"
        )

        if disabled:
            btn.configure(state="disabled")

        return btn

    def load_transactions(self):
        for item in self.tv.get_children():
            self.tv.delete(item)

        for t in self.db.get_transactions():
            self.tv.insert(
                parent="",
                index="end",
                iid=t[0],
                values=(
                    t[1],
                    t[2],
                    t[3],
                    f"₺{float(t[4]):.2f}",
                    t[5]
                )
            )

        self.btn_edit.configure(state="disabled")
        self.btn_delete.configure(state="disabled")

    def on_item_select(self, event=None):
        state = "normal" if self.tv.selection() else "disabled"
        self.btn_edit.configure(state=state)
        self.btn_delete.configure(state=state)

    def on_delete(self, event=None):
        selection = self.tv.selection()
        if not selection:
            return

        answer = msg.askyesno("Confirm Delete", "Delete this transaction?", parent=self)

        if answer:
            for iid in selection:
                self.db.delete_transaction(int(iid))
                self.tv.delete(iid)

            self.btn_edit.configure(state="disabled")
            self.btn_delete.configure(state="disabled")

    def on_edit(self, event=None):
        selection = self.tv.selection()
        if not selection:
            return

        iid = selection[0]
        values = self.tv.item(iid)["values"]

        amount = str(values[3]).replace("₺", "").replace(",", "").strip()

        edit_win = EditTransactionWindow(
            parent=self,
            db=self.db,
            transaction_id=int(iid),
            date=values[0],
            type_=values[1],
            category=values[2],
            amount=amount,
            description=values[4],
        )

        edit_win.grab_set()
        self.wait_window(edit_win)
        self.load_transactions()


class EditTransactionWindow(tk.Toplevel):
    def __init__(self, parent, db, transaction_id, date, type_, category, amount, description):
        super().__init__(parent)

        self.title("Edit Transaction")
        self.geometry("600x660")
        self.minsize(540, 600)
        self.configure(bg=BG)

        self.db = db
        self.transaction_id = transaction_id

        self.var_date = tk.StringVar(value=date)
        self.var_type = tk.StringVar(value=type_)
        self.var_category = tk.StringVar(value=category)
        self.var_amount = tk.StringVar(value=str(amount))
        self.var_description = tk.StringVar(value=description)

        self._categories = self.db.get_categories()

        self.build_ui()

    def build_ui(self):
        page = tk.Frame(self, bg=BG)
        page.pack(fill="both", expand=True, padx=42, pady=34)
        page.grid_columnconfigure(0, weight=1)

        accent = tk.Frame(page, bg=SLATE, width=10, height=10)
        accent.grid(row=0, column=0, sticky="w", pady=(0, 14))
        accent.grid_propagate(False)

        tk.Label(
            page,
            text="Edit Transaction",
            bg=BG,
            fg=TEXT,
            font=(FONT, 30, "bold")
        ).grid(row=1, column=0, sticky="w")

        tk.Label(
            page,
            text="Update the selected finance record.",
            bg=BG,
            fg=MUTED,
            font=(FONT, 12)
        ).grid(row=2, column=0, sticky="w", pady=(8, 28))

        form = tk.Frame(page, bg=SURFACE)
        form.grid(row=3, column=0, sticky="ew")
        form.grid_columnconfigure(0, weight=1)

        self.create_input(form, 0, "Date", self.var_date, "YYYY-MM-DD")
        self.cmb_type = self.create_select(form, 1, "Type", self.var_type, ["Income", "Expense"])
        self.cmb_type.bind("<<ComboboxSelected>>", self.on_type_change)
        self.cmb_category = self.create_select(form, 2, "Category", self.var_category, [])
        self.create_input(form, 3, "Amount", self.var_amount)
        self.create_input(form, 4, "Description", self.var_description)

        actions = tk.Frame(page, bg=BG)
        actions.grid(row=4, column=0, sticky="ew", pady=(24, 0))
        actions.grid_columnconfigure(0, weight=1)

        cancel_btn = self.create_button(actions, "Cancel", self.destroy, bg=INPUT, fg=TEXT)
        cancel_btn.grid(row=0, column=0, sticky="w")

        update_btn = self.create_button(actions, "Update", self.on_update, bg=TEXT, fg="#FFFFFF")
        update_btn.grid(row=0, column=1, sticky="e")

        self._refresh_categories()

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
            pady=12,
            font=(FONT, 10, "bold"),
            cursor="hand2"
        )

    def create_field_wrapper(self, parent, row, label):
        wrapper = tk.Frame(parent, bg=SURFACE)
        wrapper.grid(row=row, column=0, sticky="ew", pady=(0, 18))
        wrapper.grid_columnconfigure(0, weight=1)

        tk.Label(
            wrapper,
            text=label,
            bg=SURFACE,
            fg=TEXT,
            font=(FONT, 10, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 7))

        return wrapper

    def create_input(self, parent, row, label, variable, helper=""):
        wrapper = self.create_field_wrapper(parent, row, label)

        box = tk.Frame(wrapper, bg=INPUT)
        box.grid(row=1, column=0, sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        entry = tk.Entry(
            box,
            textvariable=variable,
            bg=INPUT,
            fg=TEXT,
            relief="flat",
            bd=0,
            font=(FONT, 11),
            insertbackground=TEXT
        )
        entry.grid(row=0, column=0, sticky="ew", padx=16, pady=12)

        if helper:
            tk.Label(
                wrapper,
                text=helper,
                bg=SURFACE,
                fg=MUTED,
                font=(FONT, 9)
            ).grid(row=2, column=0, sticky="w", pady=(5, 0))

        return entry

    def create_select(self, parent, row, label, variable, values):
        wrapper = self.create_field_wrapper(parent, row, label)

        combo = ttk.Combobox(
            wrapper,
            textvariable=variable,
            values=values,
            state="readonly",
            font=(FONT, 11)
        )
        combo.grid(row=1, column=0, sticky="ew", ipady=5)

        return combo

    def _refresh_categories(self, event=None):
        current_type = self.var_type.get()

        filtered = []
        for c in self._categories:
            if c[2] == current_type:
                filtered.append(c[1])

        self.cmb_category["values"] = filtered

        if self.var_category.get() not in filtered:
            if filtered:
                self.var_category.set(filtered[0])
            else:
                self.var_category.set("")

    def on_type_change(self, event=None):
        self._refresh_categories()

    def on_update(self):
        try:
            clean = TransactionValidator.validate(
                self.var_date.get(),
                self.var_type.get(),
                self.var_category.get(),
                self.var_amount.get(),
                self.var_description.get(),
            )

            category_id = None
            for c in self._categories:
                if c[1] == self.var_category.get():
                    category_id = c[0]
                    break

            if category_id is None:
                msg.showwarning("Validation Error", "Selected category was not found.", parent=self)
                return

            self.db.update_transaction(
                self.transaction_id,
                clean[0],
                clean[1],
                category_id,
                clean[3],
                clean[4],
            )

            self.destroy()

        except ValidationError as e:
            msg.showwarning("Validation Error", str(e), parent=self)
        except Exception as e:
            msg.showerror("System Error", f"An unexpected error occurred: {e}", parent=self)

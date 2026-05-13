import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg

from validators import TransactionValidator, ValidationError


class HistoryWindow(tk.Toplevel):

    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Transaction History")
        self.geometry("620x400")

        self.db = db

        self.build_ui()
        self.load_transactions()

    def build_ui(self):
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        tv_frame = tk.Frame(container)
        tv_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tv = ttk.Treeview(tv_frame, height=15, show="headings")
        self.tv["columns"] = ("date", "type", "category", "amount", "description")
        self.tv["selectmode"] = "browse"

        self.tv_scroll = ttk.Scrollbar(tv_frame, orient="vertical", command=self.tv.yview)
        self.tv.configure(yscrollcommand=self.tv_scroll.set)

        self.tv.heading("date",        text="Date",        anchor="center")
        self.tv.heading("type",        text="Type",        anchor="center")
        self.tv.heading("category",    text="Category",    anchor="w")
        self.tv.heading("amount",      text="Amount",      anchor="e")
        self.tv.heading("description", text="Description", anchor="w")

        self.tv.column("date",        width=95,  anchor="center")
        self.tv.column("type",        width=70,  anchor="center")
        self.tv.column("category",    width=110, anchor="w")
        self.tv.column("amount",      width=90,  anchor="e")
        self.tv.column("description", width=195, anchor="w")

        self.tv_scroll.pack(side="right", fill="y")
        self.tv.pack(side="left", fill="both", expand=True)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 6))

        self.btn_edit   = ttk.Button(btn_frame, text="Edit",   state="disabled", command=self.on_edit)
        self.btn_delete = ttk.Button(btn_frame, text="Delete", state="disabled", command=self.on_delete)
        self.btn_edit.pack(side="left",  padx=(0, 5))
        self.btn_delete.pack(side="left")

        tk.Label(self, text="Double-click or Edit: modify  |  Delete key: remove", fg="gray").pack(side="bottom", pady=4)

        self.tv.bind("<<TreeviewSelect>>", self.on_item_select)
        self.tv.bind("<Double-1>",         self.on_edit)
        self.tv.bind("<Delete>",           self.on_delete)

    def load_transactions(self):
        for item in self.tv.get_children():
            self.tv.delete(item)

        for t in self.db.get_transactions():
            self.tv.insert(parent="", index="end", iid=t[0], values=(t[1], t[2], t[3], t[4], t[5]))

    def on_item_select(self, event):
        if self.tv.selection():
            self.btn_edit.configure(state="normal")
            self.btn_delete.configure(state="normal")
        else:
            self.btn_edit.configure(state="disabled")
            self.btn_delete.configure(state="disabled")

    def on_delete(self, event=None):
        if not self.tv.selection():
            return

        answer = msg.askyesno("Confirm Delete", "Delete this transaction?", parent=self)
        if answer:
            for iid in self.tv.selection():
                self.db.delete_transaction(int(iid))
                self.tv.delete(iid)
            self.btn_edit.configure(state="disabled")
            self.btn_delete.configure(state="disabled")

    def on_edit(self, event=None):
        if event is not None:
            region = self.tv.identify("region", event.x, event.y)
            if region != "cell":
                return

        selection = self.tv.selection()
        if not selection:
            return

        iid    = selection[0]
        values = self.tv.item(iid)["values"]

        edit_win = EditTransactionWindow(
            parent=self,
            db=self.db,
            transaction_id=int(iid),
            date=values[0],
            type_=values[1],
            category=values[2],
            amount=values[3],
            description=values[4],
        )
        edit_win.grab_set()
        self.wait_window(edit_win)
        self.load_transactions()


class EditTransactionWindow(tk.Toplevel):

    def __init__(self, parent, db, transaction_id, date, type_, category, amount, description):
        super().__init__(parent)
        self.title("Edit Transaction")
        self.resizable(False, False)

        self.db             = db
        self.transaction_id = transaction_id

        self.var_date        = tk.StringVar(value=date)
        self.var_type        = tk.StringVar(value=type_)
        self.var_category    = tk.StringVar(value=category)
        self.var_amount      = tk.StringVar(value=str(amount))
        self.var_description = tk.StringVar(value=description)

        self._categories = self.db.get_categories()

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def build_ui(self):
        main_frame = ttk.LabelFrame(self, text="Edit Transaction")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        main_frame.columnconfigure(0, weight=1, uniform="eq")
        main_frame.columnconfigure(1, weight=3, uniform="eq")

        lbl_pad = {"padx": (10, 5), "pady": 6, "sticky": "e"}
        ent_pad = {"padx": (5, 10), "pady": 6, "sticky": "ew"}

        ttk.Label(main_frame, text="Date:").grid(row=0, column=0, **lbl_pad)
        ttk.Entry(main_frame, textvariable=self.var_date, width=30).grid(row=0, column=1, **ent_pad)

        ttk.Label(main_frame, text="Type:").grid(row=1, column=0, **lbl_pad)
        self.cmb_type = ttk.Combobox(main_frame, textvariable=self.var_type,
                                     values=["Income", "Expense"], state="readonly", width=28)
        self.cmb_type.grid(row=1, column=1, **ent_pad)
        self.cmb_type.bind("<<ComboboxSelected>>", self.on_type_change)

        ttk.Label(main_frame, text="Category:").grid(row=2, column=0, **lbl_pad)
        self.cmb_category = ttk.Combobox(main_frame, textvariable=self.var_category,
                                         state="readonly", width=28)
        self.cmb_category.grid(row=2, column=1, **ent_pad)

        ttk.Label(main_frame, text="Amount:").grid(row=3, column=0, **lbl_pad)
        ttk.Entry(main_frame, textvariable=self.var_amount, width=30).grid(row=3, column=1, **ent_pad)

        ttk.Label(main_frame, text="Description:").grid(row=4, column=0, **lbl_pad)
        ttk.Entry(main_frame, textvariable=self.var_description, width=30).grid(row=4, column=1, **ent_pad)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, sticky="e", padx=10, pady=(6, 12))

        ttk.Button(btn_frame, text="Update", command=self.on_update).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left")

        self._refresh_categories()

    def _refresh_categories(self):
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

    def on_type_change(self, event):
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

            cat_id = None
            for c in self._categories:
                if c[1] == self.var_category.get():
                    cat_id = c[0]
                    break

            if cat_id is None:
                msg.showwarning("Validation Error", "Selected category was not found.", parent=self)
                return

            self.db.update_transaction(
                self.transaction_id,
                clean[0],
                clean[1],
                cat_id,
                clean[3],
                clean[4],
            )
            self.destroy()

        except ValidationError as e:
            msg.showwarning("Validation Error", str(e), parent=self)
        except Exception as e:
            msg.showerror("System Error", f"An unexpected error occurred: {e}", parent=self)

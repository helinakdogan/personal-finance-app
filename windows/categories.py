import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg


class CategoriesWindow(tk.Toplevel):

    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Categories")
        self.geometry("340x400")
        self.resizable(False, False)

        self.db = db

        self.var_name = tk.StringVar()
        self.var_type = tk.StringVar(value="Expense")

        self.build_ui()
        self.load_categories()

    def build_ui(self):
        frm_add = ttk.LabelFrame(self, text="Add Category")
        frm_add.pack(fill="x", padx=10, pady=10)
        frm_add.columnconfigure(0, weight=1, uniform="eq")
        frm_add.columnconfigure(1, weight=3, uniform="eq")

        lbl_pad = {"padx": (10, 5), "pady": 6, "sticky": "e"}
        ent_pad = {"padx": (5, 10), "pady": 6, "sticky": "ew"}

        ttk.Label(frm_add, text="Name:").grid(row=0, column=0, **lbl_pad)
        self.txt_name = ttk.Entry(frm_add, textvariable=self.var_name, width=25)
        self.txt_name.grid(row=0, column=1, **ent_pad)

        ttk.Label(frm_add, text="Type:").grid(row=1, column=0, **lbl_pad)
        ttk.Combobox(frm_add, textvariable=self.var_type,
                     values=["Income", "Expense"], state="readonly", width=23).grid(row=1, column=1, **ent_pad)

        ttk.Button(frm_add, text="Add", command=self.on_add).grid(
            row=2, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 8))

        frm_list = ttk.LabelFrame(self, text="Categories")
        frm_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tv = ttk.Treeview(frm_list, height=10, show="headings")
        self.tv["columns"] = ("name", "type")
        self.tv["selectmode"] = "browse"

        self.tv.heading("name", text="Category Name", anchor="w")
        self.tv.heading("type", text="Type",          anchor="center")

        self.tv.column("name", width=180, anchor="w")
        self.tv.column("type", width=90,  anchor="center")

        self.tv.pack(fill="both", expand=True, padx=5, pady=5)

        self.btn_delete = ttk.Button(frm_list, text="Delete", state="disabled", command=self.on_delete)
        self.btn_delete.pack(side="right", padx=5, pady=(0, 5))

        self.tv.bind("<<TreeviewSelect>>", self.on_item_select)
        self.tv.bind("<Delete>", self.on_delete)

        self.txt_name.focus_set()

    def load_categories(self):
        for item in self.tv.get_children():
            self.tv.delete(item)

        for c in self.db.get_categories():
            self.tv.insert(parent="", index="end", iid=c[0], values=(c[1], c[2]))

    def on_item_select(self, event):
        if self.tv.selection():
            self.btn_delete.configure(state="normal")
        else:
            self.btn_delete.configure(state="disabled")

    def on_add(self):
        name = self.var_name.get().strip()
        type_ = self.var_type.get()

        if not name:
            msg.showwarning("Validation Error", "Category name cannot be empty.", parent=self)
            return

        try:
            self.db.add_category(name, type_)
            self.var_name.set("")
            self.load_categories()
            self.txt_name.focus_set()
        except ValueError as e:
            msg.showwarning("Validation Error", str(e), parent=self)

    def on_delete(self, event=None):
        if not self.tv.selection():
            return

        answer = msg.askyesno("Confirm Delete", "Delete this category?", parent=self)
        if answer:
            for iid in self.tv.selection():
                self.db.delete_category(int(iid))
                self.tv.delete(iid)
            self.btn_delete.configure(state="disabled")

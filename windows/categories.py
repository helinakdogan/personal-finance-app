"""Categories window — create and delete income/expense category labels.

Category names must be unique per type; the constraint is enforced at the
database level (UNIQUE index) and surfaced to the user via a warning dialog.
Deletion is blocked when a category is referenced by existing transactions.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg

from windows.custom_components import SelectBox
from windows.custom_components.theme import (
    SURFACE, TEXT, MUTED, INPUT, INPUT_HOVER, BLUE, FONT
)

BG = SURFACE


class CategoriesWindow(tk.Toplevel):
    """Screen for creating and deleting income and expense category labels.

    Parameters
    ----------
    parent : tk.Tk
        The root application window.
    db : FinanceDatabase
        The shared database instance used to persist and query categories.
    """

    def __init__(self, parent, db):
        super().__init__(parent)

        self.title("Categories")
        self.iconphoto(True, tk.PhotoImage(file="assets/logo_icon.png"))
        self.geometry("760x620")
        self.minsize(680, 520)
        self.configure(bg=BG)

        self.db = db

        self.var_name = tk.StringVar()
        self.var_type = tk.StringVar(value="Expense")

        self.build_ui()
        self.load_categories()

    def build_ui(self):
        """Construct the name input, type selector, Add button, and category table."""
        page = tk.Frame(self, bg=BG)
        page.pack(fill="both", expand=True, padx=58, pady=46)
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)

        header = tk.Frame(page, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 34))
        header.grid_columnconfigure(0, weight=1)

        accent = tk.Frame(header, bg=BLUE, width=10, height=10)
        accent.grid(row=0, column=0, sticky="w", pady=(0, 14))
        accent.grid_propagate(False)

        tk.Label(
            header,
            text="Categories",
            bg=BG,
            fg=TEXT,
            font=(FONT, 36, "bold")
        ).grid(row=1, column=0, sticky="w")

        tk.Label(
            header,
            text="Create and manage labels for income sources and expense categories.",
            bg=BG,
            fg=MUTED,
            font=(FONT, 13)
        ).grid(row=2, column=0, sticky="w", pady=(10, 0))

        form = tk.Frame(page, bg=SURFACE)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 34))
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        name_area = tk.Frame(form, bg=SURFACE)
        name_area.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        name_area.grid_columnconfigure(0, weight=1)

        tk.Label(
            name_area,
            text="Category Name*",
            bg=SURFACE,
            fg=TEXT,
            font=(FONT, 11, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        name_box = tk.Frame(name_area, bg=INPUT)
        name_box.grid(row=1, column=0, sticky="ew")
        name_box.grid_columnconfigure(0, weight=1)

        self.txt_name = tk.Entry(
            name_box,
            textvariable=self.var_name,
            bg=INPUT,
            fg=TEXT,
            relief="flat",
            bd=0,
            font=(FONT, 12),
            insertbackground=TEXT
        )
        self.txt_name.grid(row=0, column=0, sticky="ew", padx=16, pady=13)

        type_area = tk.Frame(form, bg=SURFACE)
        type_area.grid(row=0, column=1, sticky="ew", padx=(12, 0))
        type_area.grid_columnconfigure(0, weight=1)

        tk.Label(
            type_area,
            text="Type*",
            bg=SURFACE,
            fg=TEXT,
            font=(FONT, 11, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.type_select = SelectBox(
            type_area,
            self.var_type,
            values=["Income", "Expense"]
        )
        self.type_select.grid(row=1, column=0, sticky="ew")

        add_btn = self.create_button(
            form,
            "Add Category",
            self.on_add,
            bg=TEXT,
            fg="#FFFFFF"
        )
        add_btn.grid(row=1, column=1, sticky="e", pady=(22, 0))

        list_area = tk.Frame(page, bg=SURFACE)
        list_area.grid(row=2, column=0, sticky="nsew")
        list_area.grid_columnconfigure(0, weight=1)
        list_area.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")

        style.layout("Flowance.Category.Treeview", [
            ("Flowance.Category.Treeview.treearea", {"sticky": "nswe"})
        ])

        style.configure(
            "Flowance.Category.Treeview",
            font=(FONT, 10),
            rowheight=34,
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=TEXT,
            borderwidth=0,
            relief="flat"
        )

        style.configure(
            "Flowance.Category.Treeview.Heading",
            font=(FONT, 10, "bold"),
            background=SURFACE,
            foreground=MUTED,
            borderwidth=0,
            relief="flat"
        )

        style.map(
            "Flowance.Category.Treeview",
            background=[("selected", INPUT)],
            foreground=[("selected", TEXT)]
        )

        self.tv = ttk.Treeview(
            list_area,
            height=10,
            show="headings",
            style="Flowance.Category.Treeview"
        )

        self.tv["columns"] = ("name", "type")
        self.tv["selectmode"] = "browse"

        columns = {
            "name": ("Category Name", 420, "w"),
            "type": ("Type", 180, "w"),
        }

        for key, (label, width, anchor) in columns.items():
            self.tv.heading(key, text=label, anchor="w")
            self.tv.column(key, width=width, anchor=anchor, stretch=True)

        self.tv.grid(row=0, column=0, sticky="nsew")

        bottom = tk.Frame(page, bg=BG)
        bottom.grid(row=3, column=0, sticky="ew", pady=(24, 0))
        bottom.grid_columnconfigure(0, weight=1)

        tk.Label(
            bottom,
            text="Select a category to delete it.",
            bg=BG,
            fg=MUTED,
            font=(FONT, 10)
        ).grid(row=0, column=0, sticky="w")

        self.btn_delete = self.create_button(
            bottom,
            "Delete",
            self.on_delete,
            bg=TEXT,
            fg="#FFFFFF",
            disabled=True
        )
        self.btn_delete.grid(row=0, column=1, sticky="e")

        self.tv.bind("<<TreeviewSelect>>", self.on_item_select)
        self.tv.bind("<Delete>", self.on_delete)

        self.txt_name.focus_set()

    def create_button(self, parent, text, command, bg, fg, disabled=False):
        """Create and return a styled action button.

        Parameters
        ----------
        disabled : bool
            When True the button is rendered in a disabled state initially.
        """
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

    def load_categories(self):
        """Clear the Treeview and reload all categories from the database."""
        for item in self.tv.get_children():
            self.tv.delete(item)

        # iid set to the category id (index 0) so on_delete can remove the right DB row directly.
        for category in self.db.get_categories():
            self.tv.insert(
                parent="",
                index="end",
                iid=category[0],
                values=(category[1], category[2])
            )

        self.btn_delete.configure(state="disabled")

    def on_item_select(self, event=None):
        """Enable the Delete button when a row is selected; disable it otherwise."""
        state = "normal" if self.tv.selection() else "disabled"
        self.btn_delete.configure(state=state)

    def on_add(self):
        """Validate the name field and insert a new category into the database."""
        name = self.var_name.get().strip()  # strip() so a name of only spaces counts as empty.
        type_ = self.var_type.get()

        if not name:
            msg.showwarning("Validation Error", "Category name cannot be empty.", parent=self)
            return

        try:
            self.db.add_category(name, type_)
            # Success: clear the field, refresh the list, and refocus for fast repeated entry.
            self.var_name.set("")
            self.load_categories()
            self.txt_name.focus_set()
        # add_category raises ValueError on a duplicate name+type; show it as a warning.
        except ValueError as e:
            msg.showwarning("Validation Error", str(e), parent=self)

    def on_delete(self, event=None):
        """Prompt the user and delete the selected category if confirmed.

        Deletion is blocked by FinanceDatabase when the category is still
        referenced by one or more transactions.
        """
        selection = self.tv.selection()
        if not selection:
            return

        answer = msg.askyesno("Confirm Delete", "Delete this category?", parent=self)

        if answer:
            for iid in selection:
                try:
                    # delete_category refuses categories still used by transactions and raises
                    # ValueError; only drop the table row once the DB delete succeeds.
                    self.db.delete_category(int(iid))
                    self.tv.delete(iid)
                except ValueError as e:
                    msg.showwarning("Delete Error", str(e), parent=self)

            self.btn_delete.configure(state="disabled")

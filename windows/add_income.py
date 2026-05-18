import tkinter as tk
from tkinter import messagebox as msg
from datetime import date, datetime
import calendar

from validators import TransactionValidator, ValidationError


BG = "#FFFFFF"
SURFACE = "#FFFFFF"
TEXT = "#0F172A"
MUTED = "#64748B"
INPUT = "#F3F6FA"
INPUT_HOVER = "#EEF2F7"

GREEN = "#7DD3FC"
SOFT_GREEN = "#ECFDF5"

FONT = "Inter"


class SelectBox(tk.Frame):
    def __init__(self, parent, variable, values=None):
        super().__init__(parent, bg=INPUT, cursor="hand2")
        self.variable = variable
        self.values = values or []
        self.menu = None

        self.label = tk.Label(
            self,
            textvariable=self.variable,
            bg=INPUT,
            fg=TEXT,
            font=(FONT, 12),
            anchor="w",
            padx=16,
            pady=13,
            cursor="hand2"
        )
        self.label.pack(side="left", fill="x", expand=True)

        self.arrow = tk.Label(
            self,
            text="⌄",
            bg=INPUT,
            fg=MUTED,
            font=(FONT, 15),
            padx=16,
            cursor="hand2"
        )
        self.arrow.pack(side="right")

        for widget in (self, self.label, self.arrow):
            widget.bind("<Button-1>", self.open_menu)
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)

    def set_values(self, values):
        self.values = values

    def on_enter(self, event=None):
        self.configure(bg=INPUT_HOVER)
        self.label.configure(bg=INPUT_HOVER)
        self.arrow.configure(bg=INPUT_HOVER)

    def on_leave(self, event=None):
        self.configure(bg=INPUT)
        self.label.configure(bg=INPUT)
        self.arrow.configure(bg=INPUT)

    def open_menu(self, event=None):
        if self.menu and self.menu.winfo_exists():
            self.menu.destroy()
            return

        self.menu = tk.Toplevel(self)
        self.menu.overrideredirect(True)
        self.menu.configure(bg=SURFACE)

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4
        width = self.winfo_width()
        height = max(46, len(self.values) * 44)

        self.menu.geometry(f"{width}x{height}+{x}+{y}")

        if not self.values:
            tk.Label(
                self.menu,
                text="No sources",
                bg=SURFACE,
                fg=MUTED,
                font=(FONT, 11),
                anchor="w",
                padx=16,
                pady=12
            ).pack(fill="x")
            return

        for value in self.values:
            item = tk.Label(
                self.menu,
                text=value,
                bg=SURFACE,
                fg=TEXT,
                font=(FONT, 11),
                anchor="w",
                padx=16,
                pady=12,
                cursor="hand2"
            )
            item.pack(fill="x")
            item.bind("<Button-1>", lambda e, v=value: self.select(v))
            item.bind("<Enter>", lambda e, w=item: w.configure(bg=INPUT))
            item.bind("<Leave>", lambda e, w=item: w.configure(bg=SURFACE))

        self.menu.lift()

    def select(self, value):
        self.variable.set(value)
        self.close_menu()

    def close_menu(self):
        if self.menu and self.menu.winfo_exists():
            self.menu.destroy()


class DatePickerPopup(tk.Toplevel):
    def __init__(self, parent, selected_date, on_select):
        super().__init__(parent)

        self.on_select = on_select

        try:
            parsed = datetime.strptime(selected_date, "%m.%d.%Y").date()
        except ValueError:
            parsed = date.today()

        self.year = parsed.year
        self.month = parsed.month

        self.overrideredirect(True)
        self.configure(bg=SURFACE)

        x = parent.winfo_rootx()
        y = parent.winfo_rooty() + parent.winfo_height() + 6
        self.geometry(f"260x270+{x}+{y}")

        self.container = tk.Frame(self, bg=SURFACE, padx=12, pady=10)
        self.container.pack(fill="both", expand=True)

        self.render_calendar()
        self.lift()

    def render_calendar(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        header = tk.Frame(self.container, bg=SURFACE)
        header.pack(fill="x", pady=(0, 16))
        header.grid_columnconfigure(1, weight=1)

        tk.Button(
            header,
            text="‹",
            command=self.prev_month,
            bg=INPUT,
            fg=TEXT,
            relief="flat",
            bd=0,
            font=(FONT, 9),
            width=3,
            cursor="hand2"
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            header,
            text=f"{calendar.month_name[self.month]} {self.year}",
            bg=SURFACE,
            fg=TEXT,
            font=(FONT, 11, "bold")
        ).grid(row=0, column=1)

        tk.Button(
            header,
            text="›",
            command=self.next_month,
            bg=INPUT,
            fg=TEXT,
            relief="flat",
            bd=0,
            font=(FONT, 9),
            width=3,
            cursor="hand2"
        ).grid(row=0, column=2, sticky="e")

        days_frame = tk.Frame(self.container, bg=SURFACE)
        days_frame.pack(fill="both", expand=True)

        for i in range(7):
            days_frame.grid_columnconfigure(i, weight=1)

        for i, weekday in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
            tk.Label(
                days_frame,
                text=weekday,
                bg=SURFACE,
                fg=MUTED,
                font=(FONT, 9, "bold")
            ).grid(row=0, column=i, sticky="nsew", pady=(0, 8))

        today = date.today()
        month_data = calendar.monthcalendar(self.year, self.month)

        for row_index, week in enumerate(month_data, start=1):
            for column_index, day in enumerate(week):
                if day == 0:
                    tk.Label(days_frame, text="", bg=SURFACE).grid(
                        row=row_index,
                        column=column_index,
                        sticky="nsew",
                        padx=2,
                        pady=2
                    )
                    continue

                is_today = (
                    day == today.day
                    and self.month == today.month
                    and self.year == today.year
                )

                btn = tk.Button(
                    days_frame,
                    text=str(day),
                    command=lambda d=day: self.select_day(d),
                    bg=SOFT_GREEN if is_today else SURFACE,
                    fg=TEXT,
                    activebackground=INPUT,
                    activeforeground=TEXT,
                    relief="flat",
                    bd=0,
                    font=(FONT, 10),
                    cursor="hand2"
                )
                btn.grid(
                    row=row_index,
                    column=column_index,
                    sticky="nsew",
                    padx=2,
                    pady=2,
                    ipady=2
                )

    def prev_month(self):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.render_calendar()

    def next_month(self):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.render_calendar()

    def select_day(self, day):
        selected = date(self.year, self.month, day).strftime("%m.%d.%Y")
        self.on_select(selected)
        self.destroy()


class DateInput(tk.Frame):
    def __init__(self, parent, variable):
        super().__init__(parent, bg=INPUT)
        self.variable = variable
        self.popup = None

        self.entry = tk.Entry(
            self,
            textvariable=variable,
            bg=INPUT,
            fg=TEXT,
            relief="flat",
            bd=0,
            font=(FONT, 12),
            insertbackground=TEXT
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(16, 8), pady=13)

        self.button = tk.Button(
            self,
            text="Pick date",
            command=self.open_picker,
            bg=INPUT,
            fg=MUTED,
            activebackground=INPUT_HOVER,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            font=(FONT, 10),
            cursor="hand2",
            padx=14
        )
        self.button.pack(side="right", padx=(0, 8), pady=7)

    def open_picker(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            return

        self.popup = DatePickerPopup(self, self.variable.get(), self.variable.set)


class AddIncomeWindow(tk.Toplevel):
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

        select = SelectBox(wrapper, variable)
        select.grid(row=1, column=0, sticky="ew")

        return select

    def create_date_input(self, parent, row, label):
        wrapper = self.create_field_wrapper(parent, row, label)

        date_input = DateInput(wrapper, self.var_date)
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
        self.categories = [c for c in self.db.get_categories() if c[2] == "Income"]
        names = [c[1] for c in self.categories]

        self.category_box.set_values(names)

        if names:
            self.var_category.set(names[0])
        else:
            self.var_category.set("No source")

    def convert_date_for_db(self, value):
        parsed = datetime.strptime(value, "%m.%d.%Y")
        return parsed.strftime("%Y-%m-%d")

    def clear_form(self):
        self.var_amount.set("")
        self.var_description.set("")
        self.var_date.set(date.today().strftime("%m.%d.%Y"))

        if self.categories:
            self.var_category.set(self.categories[0][1])

    def on_save(self):
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
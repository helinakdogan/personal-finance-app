"""Date-picker widgets for the Flowance application.

DatePickerPopup renders a lightweight calendar inside a borderless Toplevel.
DateInput composes a text entry and a "Pick date" button that opens the popup.
Both widgets operate exclusively with the MM.DD.YYYY display format while the
database layer stores dates as YYYY-MM-DD.
"""

import tkinter as tk
from datetime import date, datetime
import calendar

from .theme import INPUT, INPUT_HOVER, SURFACE, TEXT, MUTED, SOFT_PINK, FONT


class DatePickerPopup(tk.Toplevel):
    """A borderless calendar popup that lets the user select a date by clicking.

    Parameters
    ----------
    parent       : tk widget  – the DateInput that owns this popup
    selected_date: str        – currently displayed date in MM.DD.YYYY format
    on_select    : callable   – receives the chosen date as a MM.DD.YYYY string
    today_bg     : str        – background colour used to highlight today's cell
    """
    def __init__(self, parent, selected_date, on_select, today_bg=SOFT_PINK):
        super().__init__(parent)

        self.on_select = on_select
        self.today_bg = today_bg

        # Open the calendar on the currently entered date; fall back to today if it's unparseable.
        try:
            parsed = datetime.strptime(selected_date, "%m.%d.%Y").date()
        except ValueError:
            parsed = date.today()

        # Track only year+month; the day grid is rebuilt from these on every navigation.
        self.year = parsed.year
        self.month = parsed.month

        self.overrideredirect(True)  # Borderless popup so it reads as a dropdown, not a window.
        self.configure(bg=SURFACE)

        # Anchor the popup directly beneath the owning DateInput using screen coordinates.
        x = parent.winfo_rootx()
        y = parent.winfo_rooty() + parent.winfo_height() + 6
        self.geometry(f"260x270+{x}+{y}")

        self.container = tk.Frame(self, bg=SURFACE, padx=12, pady=10)
        self.container.pack(fill="both", expand=True)

        self.render_calendar()
        self.lift()

    def render_calendar(self):
        # Wipe the previous month's widgets so navigating months never stacks old grids.
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
        # monthcalendar returns weeks as 7-day lists, with 0 marking days outside this month.
        month_data = calendar.monthcalendar(self.year, self.month)

        for row_index, week in enumerate(month_data, start=1):
            for column_index, day in enumerate(week):
                # A 0 is a padding cell (prev/next month); render an empty placeholder and skip it.
                if day == 0:
                    tk.Label(days_frame, text="", bg=SURFACE).grid(
                        row=row_index, column=column_index,
                        sticky="nsew", padx=2, pady=2
                    )
                    continue

                # Highlight today's cell only when the visible month/year matches the real date.
                is_today = (
                    day == today.day
                    and self.month == today.month
                    and self.year == today.year
                )

                btn = tk.Button(
                    days_frame,
                    text=str(day),
                    command=lambda d=day: self.select_day(d),
                    bg=self.today_bg if is_today else SURFACE,
                    fg=TEXT,
                    activebackground=INPUT,
                    activeforeground=TEXT,
                    relief="flat",
                    bd=0,
                    font=(FONT, 10),
                    cursor="hand2"
                )
                btn.grid(
                    row=row_index, column=column_index,
                    sticky="nsew", padx=2, pady=2, ipady=2
                )

    def prev_month(self):
        self.month -= 1
        # Wrap January back to December of the previous year.
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.render_calendar()

    def next_month(self):
        self.month += 1
        # Wrap December forward to January of the next year.
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.render_calendar()

    def select_day(self, day):
        # Build the MM.DD.YYYY string, hand it back via the callback, and close the popup.
        selected = date(self.year, self.month, day).strftime("%m.%d.%Y")
        self.on_select(selected)
        self.destroy()


class DateInput(tk.Frame):
    """A composite widget that pairs a text entry with a calendar picker button.

    The entry accepts manual keyboard input; the button opens DatePickerPopup.
    Both paths write to the same tk.StringVar in MM.DD.YYYY format.
    """

    def __init__(self, parent, variable, today_bg=SOFT_PINK):
        super().__init__(parent, bg=INPUT)
        self.variable = variable
        self.today_bg = today_bg
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
        # Toggle behaviour: a second click while the calendar is open closes it instead of reopening.
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            return

        # Pass variable.set as the callback so a picked day writes straight back into the entry.
        self.popup = DatePickerPopup(self, self.variable.get(), self.variable.set, today_bg=self.today_bg)

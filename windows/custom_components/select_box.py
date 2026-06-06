"""Custom dropdown widget that matches the Flowance visual theme.

The standard ttk.Combobox cannot be styled to match the flat, token-based
design system used throughout the application.  SelectBox reimplements the
dropdown as a tk.Frame that opens a borderless tk.Toplevel on click.
"""

import tkinter as tk

from .theme import INPUT, INPUT_HOVER, SURFACE, TEXT, MUTED, FONT


class SelectBox(tk.Frame):
    """A fully styled dropdown widget built from first-principles tk primitives.

    Parameters
    ----------
    parent      : tk widget    – parent container
    variable    : tk.StringVar – bound variable that holds the selected value
    values      : list[str]    – options shown in the dropdown menu
    on_select   : callable     – optional callback fired after a selection
    empty_text  : str          – label shown when *values* is empty
    """
    def __init__(self, parent, variable, values=None, on_select=None, empty_text="No options"):
        super().__init__(parent, bg=INPUT, cursor="hand2")
        self.variable = variable
        self.values = values or []  # `or []` guards against a None default becoming a crash later.
        self.on_select = on_select
        self.empty_text = empty_text
        self.menu = None  # Holds the open dropdown Toplevel; None means the menu is currently closed.

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

        # Bind on every child too so a click or hover anywhere on the box behaves as one widget.
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
        # Clicking while the menu is open acts as a toggle: close it and stop.
        if self.menu and self.menu.winfo_exists():
            self.menu.destroy()
            return

        # overrideredirect(True) removes the window border so the menu looks like a flat panel.
        self.menu = tk.Toplevel(self)
        self.menu.overrideredirect(True)
        self.menu.configure(bg=SURFACE)

        # Position the menu just below the box, matched to its width; rootx/rooty are screen coords.
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4
        width = self.winfo_width()
        height = max(46, len(self.values) * 44)  # ~44px per item, with a floor for the empty state.

        self.menu.geometry(f"{width}x{height}+{x}+{y}")

        if not self.values:
            tk.Label(
                self.menu,
                text=self.empty_text,
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
            # Default-argument binding (v=value, w=item) captures the current loop value;
            # without it every row's lambda would close over the final value instead.
            item.bind("<Button-1>", lambda e, v=value: self.select(v))
            item.bind("<Enter>", lambda e, w=item: w.configure(bg=INPUT))
            item.bind("<Leave>", lambda e, w=item: w.configure(bg=SURFACE))

        self.menu.lift()

    def select(self, value):
        # Write the choice into the bound variable, fire the optional callback, then close.
        self.variable.set(value)
        if self.on_select:
            self.on_select()
        self.close_menu()

    def close_menu(self):
        if self.menu and self.menu.winfo_exists():
            self.menu.destroy()

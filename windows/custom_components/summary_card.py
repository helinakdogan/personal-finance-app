"""Summary card widget used on the Dashboard window.

SummaryCard displays a single financial metric (e.g. Total Income) with a
coloured accent dot, a label, and a dynamically bound value string.
"""

import tkinter as tk

from .theme import SURFACE, TEXT, MUTED, FONT


class SummaryCard(tk.Frame):
    """A metric card composed of an accent dot, a label, and a bold value.

    Parameters
    ----------
    parent    : tk widget    – parent container
    label     : str          – descriptive text shown above the value
    value_var : tk.StringVar – bound variable updated at runtime (e.g. "₺1,200.00")
    accent    : str          – hex colour of the decorative dot
    """
    def __init__(self, parent, label, value_var, accent):
        super().__init__(parent, bg=SURFACE, padx=22, pady=18)

        self.dot = tk.Frame(self, bg=accent, width=9, height=9)
        self.dot.grid(row=0, column=0, sticky="w", pady=(0, 16))
        self.dot.grid_propagate(False)

        tk.Label(
            self,
            text=label,
            bg=SURFACE,
            fg=MUTED,
            font=(FONT, 10),
            anchor="w"
        ).grid(row=1, column=0, sticky="w")

        tk.Label(
            self,
            textvariable=value_var,
            bg=SURFACE,
            fg=TEXT,
            font=(FONT, 20, "bold"),
            anchor="w"
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))

        self.grid_columnconfigure(0, weight=1)

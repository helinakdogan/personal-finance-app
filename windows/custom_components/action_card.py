"""Action card widget used on the main navigation screen.

Each ActionCard represents a top-level feature of the application.
It displays a title, a short description, and an accent dot, and fires
a command when clicked anywhere on its surface.
"""

import tkinter as tk

from .theme import SURFACE, TEXT, MUTED, FONT


class ActionCard(tk.Frame):
    """A clickable card widget with hover colouring and an accent indicator.

    Parameters
    ----------
    parent   : tk widget – parent container
    title    : str       – primary label (feature name)
    subtitle : str       – short description displayed beneath the title
    accent   : str       – hex colour used for the dot and hovered title text
    command  : callable  – function called when the card is clicked
    """
    def __init__(self, parent, title, subtitle, accent, command):
        super().__init__(parent, bg=SURFACE, cursor="hand2")

        self.command = command
        self.accent = accent
        self.default_bg = SURFACE
        self.hover_bg = "#F8FAFC"

        self.configure(padx=22, pady=20)

        self.dot = tk.Frame(self, bg=accent, width=9, height=9)
        self.dot.grid(row=0, column=0, sticky="w", pady=(0, 18))
        self.dot.grid_propagate(False)

        self.title_label = tk.Label(
            self,
            text=title,
            bg=SURFACE,
            fg=TEXT,
            font=(FONT, 15, "bold"),
            anchor="w"
        )
        self.title_label.grid(row=1, column=0, sticky="w")

        self.subtitle_label = tk.Label(
            self,
            text=subtitle,
            bg=SURFACE,
            fg=MUTED,
            font=(FONT, 10),
            anchor="w",
            justify="left",
            wraplength=180
        )
        self.subtitle_label.grid(row=2, column=0, sticky="w", pady=(8, 0))

        self.grid_columnconfigure(0, weight=1)

        for widget in (self, self.dot, self.title_label, self.subtitle_label):
            widget.bind("<Button-1>", self.on_click)
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)

    def on_click(self, event=None):
        self.command()

    def on_enter(self, event=None):
        self.configure(bg=self.hover_bg)
        self.title_label.configure(bg=self.hover_bg, fg=self.accent)
        self.subtitle_label.configure(bg=self.hover_bg)

    def on_leave(self, event=None):
        self.configure(bg=self.default_bg)
        self.title_label.configure(bg=self.default_bg, fg=TEXT)
        self.subtitle_label.configure(bg=self.default_bg)

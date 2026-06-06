"""Centralised design tokens for the Flowance application.

All colours, accent values and the font family are defined here so that
every window and custom component shares a single source of truth.
Importing from this module avoids duplicating magic strings across files.
"""

# Base surfaces: card/panel background vs. the page behind them.
SURFACE = "#FFFFFF"
BG_PAGE = "#F8FAFC"

# Text colours: primary text, secondary/muted text, and a soft divider tone.
TEXT = "#0F172A"
MUTED = "#64748B"
SOFT = "#F1F5F9"

# Form input backgrounds: default and the slightly darker hover state.
INPUT = "#F3F6FA"
INPUT_HOVER = "#EEF2F7"

# Accent palette used for card dots, chart series and section markers.
CYAN = "#7DD3FC"
BLUE = "#60A5FA"
PURPLE = "#818CF8"
PINK = "#F9A8D4"
SLATE = "#94A3B8"
GREEN = "#7DD3A8"

# Tinted highlights for the date picker's "today" cell on the expense/income forms.
SOFT_PINK = "#FFF1F7"
SOFT_GREEN = "#ECFDF5"

FONT = "Inter"  # Single font family shared by every widget for a consistent look.

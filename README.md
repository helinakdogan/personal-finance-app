<div align="center">

<img src="assets/logo.png" width="400"/>

A local-first personal finance desktop application built with Python 3, Tkinter, and SQLite.

</div>

---

## Architecture Overview

The application follows a **layered architecture** with strict separation of concerns:
the database layer has no knowledge of the UI, the validation layer has no knowledge
of storage, and each window is self-contained.

```
┌─────────────────────────────────────────────┐
│                   main.py                   │  Entry point — root navigation window
├─────────────┬───────────────────────────────┤
│  windows/   │  custom_components/           │  Presentation layer
│  (screens)  │  (reusable UI widgets)        │
├─────────────┴───────────────────────────────┤
│              validators.py                  │  Business-rule layer
├─────────────────────────────────────────────┤
│               database.py                   │  Persistence layer (SQLite)
└─────────────────────────────────────────────┘
```

---

## Project Structure

```
personal-finance-app/
│
├── main.py                        # Application entry point; root navigation window
├── database.py                    # SQLite CRUD wrapper (FinanceDatabase)
├── validators.py                  # Field validation before any DB write
│
├── windows/
│   ├── add_expense.py             # Form: record a new expense transaction
│   ├── add_income.py              # Form: record a new income transaction
│   ├── categories.py              # Create and delete income/expense category labels
│   ├── dashboard.py               # Read-only summary: totals + last 5 transactions
│   ├── history.py                 # Full transaction ledger; inline edit and delete
│   └── reports.py                 # Pie chart (by category) + bar chart (by month)
│
├── windows/custom_components/
│   ├── __init__.py                # Re-exports all components for a clean import surface
│   ├── theme.py                   # Centralised design tokens (colours, font family)
│   ├── select_box.py              # Custom styled dropdown widget (SelectBox)
│   ├── date_picker.py             # Calendar popup and composite date entry (DateInput)
│   ├── summary_card.py            # Metric card used on the Dashboard (SummaryCard)
│   └── action_card.py             # Clickable navigation card used on MainApp (ActionCard)
│
└── assets/
    ├── logo.png                   # Header logo displayed in MainApp
    └── logo_icon.png              # Window icon applied to all Toplevel windows
```

---

## Layer Details

### `database.py` — Persistence Layer

`FinanceDatabase` wraps all SQLite access. A new connection is opened and closed
for every operation, keeping concurrent window access safe without requiring a
connection pool.

**Schema:**

```sql
categories (
    id       INTEGER PRIMARY KEY,
    name     TEXT,
    type     TEXT,
    UNIQUE(name, type)
)

transactions (
    id          INTEGER PRIMARY KEY,
    date        TEXT,          -- ISO 8601: YYYY-MM-DD
    type        TEXT,          -- 'Income' or 'Expense'
    category_id INTEGER REFERENCES categories(id),
    amount      REAL,
    description TEXT
)
```

- The `UNIQUE(name, type)` constraint enforces duplicate-free categories at the
  database level; `add_category` surfaces an `IntegrityError` as a `ValueError`.
- `delete_category` counts referencing rows before deletion to preserve
  referential integrity, since SQLite does not enforce foreign keys by default.
- All SQL uses parameterised queries; no string interpolation is used.

---

### `validators.py` — Business-Rule Layer

`TransactionValidator.validate()` is the single gate before any record reaches
the database. It strips whitespace, checks all format and range constraints, and
returns a normalised tuple `(date, type_, category, amount_float, description)`.

Every window's save handler calls this method; no screen bypasses it.

---

### `windows/` — Presentation Layer

Each screen is a `tk.Toplevel` managed by `MainApp._open_window()`, which ensures
only one instance of each window is open at a time.

| Module | Class | Responsibility |
|---|---|---|
| `add_expense.py` | `AddExpenseWindow` | Collect and validate an expense; write via `FinanceDatabase` |
| `add_income.py` | `AddIncomeWindow` | Same flow for income records |
| `categories.py` | `CategoriesWindow` | Add/delete labels; blocks deletion when referenced by transactions |
| `dashboard.py` | `DashboardWindow` | Compute income/expense totals; show last 5 transactions |
| `history.py` | `HistoryWindow`, `EditTransactionWindow` | Full ledger; `EditTransactionWindow` opens as a modal |
| `reports.py` | `ReportsWindow` | Render Matplotlib figures embedded in a `FigureCanvasTkAgg` |

---

### `windows/custom_components/` — Reusable Widget Library

Standard `ttk` widgets cannot be styled to match the flat, token-based design
system. This sub-package provides hand-built alternatives that inherit from basic
`tk` primitives.

| Widget | Replaces | Reason for custom implementation |
|---|---|---|
| `SelectBox` | `ttk.Combobox` | Full background and hover colour control; borderless dropdown |
| `DatePickerPopup` | — | Calendar rendered with a `tk.Button` grid; no external dependency |
| `DateInput` | `tk.Entry` alone | Pairs a text entry with the calendar picker in one composite widget |
| `SummaryCard` | `ttk.Frame` + labels | Encapsulates the accent dot and metric layout used on Dashboard |
| `ActionCard` | `ttk.Button` | Large clickable card with hover colour transition |

`theme.py` exports every design token — colours and the font family — so that all
components share a single source of truth. No magic strings are duplicated across
files.

---

## Data Flow — Adding a Transaction

```
User fills the Add Expense / Add Income form
        │
        ▼
DateInput converts MM.DD.YYYY → YYYY-MM-DD
        │
        ▼
TransactionValidator.validate()
  ├─ raises ValidationError  →  warning dialog shown; form stays open
  └─ returns a clean (date, type, category, amount, description) tuple
        │
        ▼
FinanceDatabase.add_transaction()
  └─ INSERT INTO transactions …
        │
        ▼
Success dialog → form fields cleared, ready for the next entry
```

---

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install matplotlib pillow

# 3. Run
python3 main.py
```

The SQLite database file (`finance.db`) is created automatically on first launch.

---

## Contributors

- Helin Akdoğan
- Koray Özcan

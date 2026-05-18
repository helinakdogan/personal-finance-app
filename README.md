<div align="center">

<img src="assets/logo.png" width="220"/>

# Flowance

Modern personal finance desktop application built with Python, Tkinter and SQLite.

</div>

---

# Overview

Flowance is a desktop finance management application designed to help users track income, expenses, categories and financial reports in a clean and modern interface.

The application allows users to:

- Add income and expense transactions
- Organize transactions with categories
- View transaction history
- Edit and delete records
- Analyze financial reports with charts
- Monitor balance and recent activity

---

# Technologies Used

- Python 3
- Tkinter
- SQLite
- Matplotlib
- PIL / Pillow

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/helinakdogan/personal-finance-app.git
```

---

## 2. Install Required Packages

```bash
pip install matplotlib pillow
```

---

## 3. Run Application

```bash
python main.py
```

---

# Project Structure

```txt
personal-finance-app/
│
├── assets/
│   └── logo.png
│
├── windows/
│   ├── dashboard.py
│   ├── add_expense.py
│   ├── add_income.py
│   ├── history.py
│   ├── reports.py
│   └── categories.py
│
├── database.py
├── validators.py
├── main.py
└── finance.db
```

---

# Features

## Dashboard
- Balance overview
- Total income and expense tracking
- Recent transaction list

## Transactions
- Add expense
- Add income
- Edit records
- Delete records

## Categories
- Create custom categories
- Separate income and expense types

## Reports
- Expense distribution pie chart
- Monthly income vs expense bar chart

---

# Database

The application uses SQLite for local data storage.

Main tables:
- transactions
- categories

---

# UI Design

Flowance uses a modern minimal UI inspired by Apple-style desktop applications.

Design characteristics:
- Soft neutral colors
- Minimal borders
- Responsive layouts
- Custom dropdown components
- Clean typography

---

# Contributors

- Helin Akdoğan
- Koray Özcan

---

# License

This project was developed for educational purposes.
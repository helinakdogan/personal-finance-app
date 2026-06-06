"""Validation layer for transaction data.

Provides TransactionValidator, which enforces all business rules
before any record is persisted to the database.
"""

from datetime import datetime


class ValidationError(Exception):
    """Raised when a transaction field fails a business-rule check."""


class TransactionValidator:
    """Validates all fields of a transaction record before persistence.

    All methods are static; no instantiation is required.
    """

    @staticmethod
    def validate(date, type_, category, amount, description=""):
        """Validate and normalise transaction fields.

        Parameters
        ----------
        date        : str  – expected in YYYY-MM-DD format
        type_       : str  – must be exactly 'Income' or 'Expense'
        category    : str  – non-empty category name
        amount      : str  – string representation of a positive number
        description : str  – optional free-text note (may be empty)

        Returns
        -------
        tuple: (date, type_, category, amount_float, description)

        Raises
        ------
        ValidationError – if any field fails its constraint
        """
        date        = date.strip()
        type_       = type_.strip()
        category    = category.strip()
        amount      = amount.strip()
        description = description.strip()

        if not date:
            raise ValidationError("Date is required.")

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError(
                "Invalid date format. Please use YYYY-MM-DD (e.g. 2026-05-15)."
            )

        if type_ not in ("Income", "Expense"):
            raise ValidationError("Transaction type must be either 'Income' or 'Expense'.")

        if not category:
            raise ValidationError("Please select a category.")

        if not amount:
            raise ValidationError("Amount is required.")

        try:
            amount_value = float(amount)
        except ValueError:
            raise ValidationError("Amount must be a valid number (e.g. 250 or 1500.50).")

        if amount_value <= 0:
            raise ValidationError("Amount must be greater than zero.")

        return date, type_, category, amount_value, description

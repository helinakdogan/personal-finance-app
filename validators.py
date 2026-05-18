from datetime import datetime


class ValidationError(Exception):
    pass


class TransactionValidator:
    @staticmethod
    def validate(date, type_, category, amount, description=""):
        date = date.strip()
        type_ = type_.strip()
        category = category.strip()
        amount = amount.strip()
        description = description.strip()

        if not date:
            raise ValidationError("Date cannot be empty.")

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Date must be in YYYY-MM-DD format.")

        if type_ not in ["Income", "Expense"]:
            raise ValidationError("Type must be Income or Expense.")

        if not category:
            raise ValidationError("Category cannot be empty.")

        if not amount:
            raise ValidationError("Amount cannot be empty.")

        try:
            amount_value = float(amount)
        except ValueError:
            raise ValidationError("Amount must be numeric.")

        if amount_value <= 0:
            raise ValidationError("Amount must be greater than 0.")

        return date, type_, category, amount_value, description
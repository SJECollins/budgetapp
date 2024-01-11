from calendar import monthrange
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save

TRANSACTION_TYPE = (
    ("Income", "Income"),
    ("Expense", "Expense"),
)

BUDGET_TYPE = (
    ("Daily", "Daily"),
    ("Weekly", "Weekly"),
    ("Monthly", "Monthly"),
    ("Yearly", "Yearly"),
)


class BankAccount(models.Model):
    """
    Model representing a bank account (e.g. Current, Savings, AIB, Revolut, etc.) for a specific user.
    Can optionally specify an account balance.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=50,
        help_text="Enter an account name (e.g. Current, Savings, BOI, Revolut, etc.)",
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Optionally, enter an account balance.",
    )

    def __str__(self):
        return self.name

    def get_balance(self):
        # Return the account balance
        total_income = 0
        total_expense = 0

        transactions = Transaction.objects.filter(user=self.user, account=self)

        for transaction in transactions:
            if transaction.income_or_expense == "Income":
                total_income += transaction.amount
            else:
                total_expense += transaction.amount

        return self.balance + total_income - total_expense


class Category(models.Model):
    """Model representing a category of transaction (e.g. Groceries, Rent, etc.) for a specific user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=50, help_text="Enter a category name (e.g. Groceries, Rent, etc.)"
    )

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """
    Model representing a transaction (e.g. €10.00 spent on Groceries on 2021-01-01) for a specific user.
    Can be either an income or an expense.
    Can be recurring (e.g. €10.00 spent on Groceries every week).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Amount of transaction."
    )
    income_or_expense = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPE,
        help_text="Choose whether this is an income or an expense.",
    )
    date = models.DateField(
        blank=True,
        null=True,
        help_text="Date of transaction. If left blank, will default to today.",
    )
    created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(
        max_length=180, blank=True, help_text="Optionally, add a short description."
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Choose a category for this transaction.",
    )
    new_category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optionally, add a new category for this transaction.",
    )
    recurring = models.BooleanField(
        default=False, help_text="Check this box if this transaction is recurring."
    )
    interval = models.CharField(
        max_length=50,
        choices=BUDGET_TYPE,
        blank=True,
        null=True,
        help_text="If this transaction is recurring, choose the interval or due date.",
    )
    due_date = models.DateField(
        blank=True,
        null=True,
        help_text="If this transaction is recurring, choose the due date or interval.",
    )
    new_transaction_created = models.BooleanField(
        default=False,
        help_text="This field is used internally to determine whether a new transaction should be created.",
    )
    previous_transaction = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="This field is used internally to link recurring transactions.",
    )
    account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Choose an account for this transaction.",
    )
    notes = models.TextField(
        blank=True, help_text="Optionally, add notes for this transaction."
    )

    def __str__(self):
        return self.income_or_expense + ": €" + str(self.amount)

    def calculate_due_date(self):
        if self.interval == "Daily":
            return self.date + timedelta(days=1)
        elif self.interval == "Weekly":
            return self.date + timedelta(weeks=1)
        elif self.interval == "Monthly":
            return self.date + timedelta(days=30)
        elif self.interval == "Yearly":
            return self.date + timedelta(days=365)
        else:
            return None


@receiver(pre_save, sender=Transaction)
def set_due_date(sender, instance, **kwargs):
    # If no date is specified, default to today
    if not instance.date:
        instance.date = date.today()

    if instance.recurring:
        instance.due_date = instance.calculate_due_date()


class SpendingBudget(models.Model):
    """
    Model representing a spending budget (e.g. €100.00 per month) for a specific user.
    Can specify a start and end date, or can be recurring (e.g. €100.00 per month).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=50,
        default="Spending Budget",
        help_text="Enter a budget name (e.g. Groceries, Rent, etc.)",
    )
    description = models.CharField(
        max_length=180, blank=True, help_text="Optionally, add a short description."
    )
    goal_amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Amount of budget."
    )
    interval = models.CharField(
        max_length=50,
        choices=BUDGET_TYPE,
        blank=True,
        null=True,
        help_text="Optionally, choose an interval for this budget (e.g. Weekly, Monthly, etc.)",
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text="Optionally, choose a start date for this budget.",
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Optionally, choose an end date for this budget.",
    )
    account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Optionally, choose an account for this budget.",
    )
    notes = models.TextField(
        blank=True, help_text="Optionally, add notes for this budget."
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_budget_progress(self):
        # Return the percentage of the budget that has been spent
        total_expense = 0

        if self.account:
            transactions = Transaction.objects.filter(
                user=self.user, income_or_expense="Expense", account=self.account
            )
        else:
            transactions = Transaction.objects.filter(
                user=self.user, income_or_expense="Expense"
            )

        for transaction in transactions:
            total_expense += transaction.amount
        return round(total_expense / self.goal_amount * 100, 2)

    def get_budget_remaining(self):
        # Return the amount of the budget that has not been spent
        total_expense = 0

        if self.account:
            transactions = Transaction.objects.filter(
                user=self.user, income_or_expense="Expense", account=self.account
            )
        else:
            transactions = Transaction.objects.filter(
                user=self.user, income_or_expense="Expense"
            )

        for transaction in transactions:
            total_expense += transaction.amount
        return self.goal_amount - total_expense


class SavingsGoal(models.Model):
    """
    Model representing a savings goal (e.g. €1000.00 for a new car) for a specific user.
    Can specify a start and end date, or can be recurring (e.g. €100.00 per month).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=50,
        default="Savings",
        help_text="Goal name, leave blank for to default to 'Savings'",
    )
    description = models.CharField(
        max_length=180, blank=True, help_text="Optionally, add a short description."
    )
    goal_amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Amount of goal."
    )
    interval = models.CharField(
        max_length=50,
        choices=BUDGET_TYPE,
        default="Custom",
        help_text="Optionally, choose an interval for this goal (e.g. Weekly, Monthly, etc.)",
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text="Optionally, choose a start date for this goal.",
    )
    target_date = models.DateField(
        blank=True,
        null=True,
        help_text="Optionally, choose a target date for this goal.",
    )
    account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Optionally, choose an account for this goal.",
    )
    notes = models.TextField(
        blank=True, help_text="Optionally, add notes for this goal."
    )

    def __str__(self):
        return self.name

    def calculate_progress(self):
        start_day = None
        end_day = None

        today = datetime.now()

        if self.interval == "Daily":
            start_day = datetime.date.today()
            end_day = start_day + timedelta(days=1)
        elif self.interval == "Weekly":
            start_day = today - timedelta(days=today.weekday())
            end_day = start_day + timedelta(days=7)
        elif self.interval == "Monthly":
            start_day = today.replace(day=1)
            _, last_day_of_month = monthrange(start_day.year, start_day.month)
            end_day = start_day.replace(day=last_day_of_month) + timedelta(days=1)
        elif self.interval == "Yearly":
            start_day = today.replace(month=1, day=1)
            end_day = start_day.replace(month=12, day=31) + timedelta(days=1)
        elif self.interval == "Custom":
            start_day = self.start_date
            end_day = self.target_date

        if self.account:
            transactions = Transaction.objects.filter(
                user=self.user, date__range=(start_day, end_day), account=self.account
            )
        else:
            transactions = Transaction.objects.filter(
                user=self.user, date__range=(start_day, end_day)
            )

        total_income = sum(
            transaction.amount
            for transaction in transactions.filter(income_or_expense="Income")
        )
        total_expenses = sum(
            transaction.amount
            for transaction in transactions.filter(income_or_expense="Expense")
        )

        progress = total_income - total_expenses

        return max(progress, 0)

    def get_progress_display(self, as_percentage=True):
        progress = self.calculate_progress()

        if as_percentage:
            if self.goal_amount == 0:
                return "100%"
            return f"{min((progress / self.goal_amount) * 100, 100):.2f}%"
        else:
            return f"${progress:.2f}"


class TaskStatus(models.Model):
    """
    Model to store last time a task was run.
    """

    name = models.CharField(max_length=50)
    last_run = models.DateTimeField(default=timezone.now)

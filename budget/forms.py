from django.utils import timezone
from django import forms

from .models import BankAccount, Category, Transaction, SpendingBudget, SavingsGoal


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ["name", "balance"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "amount",
            "income_or_expense",
            "date",
            "description",
            "category",
            "new_category",
            "recurring",
            "interval",
            "account",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "amount": forms.NumberInput(attrs={"step": "0.01"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        new_category = cleaned_data.get("new_category")

        if category and new_category:
            raise forms.ValidationError(
                "Please select a category or enter a new one, not both"
            )

        if new_category:
            category = Category.objects.create(
                name=new_category,
                user=self.instance.user,
            )
            cleaned_data["category"] = category

        return cleaned_data


class SpendingBudgetForm(forms.ModelForm):
    class Meta:
        model = SpendingBudget
        fields = [
            "name",
            "description",
            "goal_amount",
            "interval",
            "start_date",
            "end_date",
            "account",
            "notes",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "goal_amount": forms.NumberInput(attrs={"step": "0.01"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        interval = cleaned_data.get("interval")

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError(
                    "End date should be greater than start date"
                )

        if interval and start_date and end_date:
            if interval == "weekly":
                if (end_date - start_date).days < 7:
                    raise forms.ValidationError(
                        "Weekly budgets should be at least a week"
                    )
                if (end_date - start_date).days % 7 != 0:
                    raise forms.ValidationError(
                        "Weekly budgets should be a multiple of 7 days"
                    )
            elif interval == "monthly":
                if (end_date - start_date).days < 30:
                    raise forms.ValidationError(
                        "Monthly budgets should be at least a month"
                    )
                if (end_date - start_date).days % 30 != 0:
                    raise forms.ValidationError(
                        "Monthly budgets should be a multiple of 30 days"
                    )
            elif interval == "yearly":
                if (end_date - start_date).days < 365:
                    raise forms.ValidationError(
                        "Yearly budgets should be at least a year"
                    )
                if (end_date - start_date).days % 365 != 0:
                    raise forms.ValidationError(
                        "Yearly budgets should be a multiple of 365 days"
                    )

        if not start_date:
            start_date = timezone.now().date()

        if not interval and not start_date and not end_date:
            raise forms.ValidationError(
                "Please provide either an interval or a start and end date"
            )

        cleaned_data["start_date"] = start_date
        cleaned_data["end_date"] = end_date
        cleaned_data["interval"] = interval
        return cleaned_data


class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = [
            "name",
            "description",
            "goal_amount",
            "interval",
            "start_date",
            "target_date",
            "account",
            "notes",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "target_date": forms.DateInput(attrs={"type": "date"}),
            "goal_amount": forms.NumberInput(attrs={"step": "0.01"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        target_date = cleaned_data.get("target_date")
        interval = cleaned_data.get("interval")

        if start_date and target_date:
            if target_date < start_date:
                raise forms.ValidationError(
                    "Target date should be greater than start date"
                )

        if interval and start_date and target_date:
            if interval == "weekly":
                if (target_date - start_date).days < 7:
                    raise forms.ValidationError(
                        "Weekly goals should be at least a week"
                    )
                if (target_date - start_date).days % 7 != 0:
                    raise forms.ValidationError(
                        "Weekly goals should be a multiple of 7 days"
                    )
            elif interval == "monthly":
                if (target_date - start_date).days < 30:
                    raise forms.ValidationError(
                        "Monthly goals should be at least a month"
                    )
                if (target_date - start_date).days % 30 != 0:
                    raise forms.ValidationError(
                        "Monthly goals should be a multiple of 30 days"
                    )
            elif interval == "yearly":
                if (target_date - start_date).days < 365:
                    raise forms.ValidationError(
                        "Yearly goals should be at least a year"
                    )
                if (target_date - start_date).days % 365 != 0:
                    raise forms.ValidationError(
                        "Yearly goals should be a multiple of 365 days"
                    )

        if not start_date:
            start_date = timezone.now().date()

        if not interval and not start_date and not target_date:
            raise forms.ValidationError(
                "Please provide either an interval or a start and target date"
            )

        cleaned_data["start_date"] = start_date
        cleaned_data["target_date"] = target_date
        cleaned_data["interval"] = interval
        return cleaned_data

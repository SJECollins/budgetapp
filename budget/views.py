from django.utils import timezone
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import BankAccount, Category, Transaction, SpendingBudget, SavingsGoal
from .forms import (
    BankAccountForm,
    CategoryForm,
    TransactionForm,
    SpendingBudgetForm,
    SavingsGoalForm,
)


def home(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    transactions = Transaction.objects.filter(user=request.user).order_by("-date")

    upcoming_transactions = transactions.filter(
        recurring=True, new_transaction_created=False, date__gte=timezone.now().date()
    ).order_by("-due_date")

    recent_transactions = transactions.filter(recurring=False)[:5]
    serialized_transactions = list(transactions.values())

    context = {
        "spending_data": serialized_transactions,
        "upcoming_transactions": upcoming_transactions,
        "recent_transactions": recent_transactions,
    }

    return render(request, "budget/budget.html", context)


def manage(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    accounts = BankAccount.objects.filter(user=request.user).order_by("name")
    categories = Category.objects.filter(user=request.user).order_by("name")
    budgets = SpendingBudget.objects.filter(user=request.user).order_by("name")
    goals = SavingsGoal.objects.filter(user=request.user).order_by("name")

    context = {
        "accounts": accounts,
        "categories": categories,
        "budgets": budgets,
        "goals": goals,
    }

    return render(request, "budget/manage.html", context)


def list_transactions(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    transactions = Transaction.objects.filter(user=request.user).order_by("-date")

    context = {"transactions": transactions}

    return render(request, "budget/transaction_list.html", context)


def transaction_detail(request, transaction_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    transaction = Transaction.objects.get(id=transaction_id)

    context = {"transaction": transaction}

    return render(request, "budget/transaction.html", context)


def add_transaction(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add a transaction")
        return render(request, "index.html")

    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, "Transaction added successfully")
            return redirect("budget")
        else:
            messages.error(request, "Error adding transaction")
    else:
        form = TransactionForm()

    context = {
        "form": form,
        "form_for": "Transaction",
        "form_title": "Add A New Transaction",
        "form_button": "Add",
    }

    return render(request, "budget/generic_form.html", context)


def edit_transaction(request, transaction_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    transaction = Transaction.objects.get(id=transaction_id)

    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated successfully")
            return redirect("budget")
        else:
            messages.error(request, "Error updating transaction")
    else:
        form = TransactionForm(instance=transaction)

    context = {
        "form": form,
        "form_for": "Transaction",
        "form_title": "Edit Transaction",
        "form_button": "Update",
    }

    return render(request, "budget/generic_form.html", context)


def delete_transaction(request, transaction_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    transaction = Transaction.objects.get(id=transaction_id)

    if request.method == "POST":
        transaction.delete()
        messages.success(request, "Transaction deleted successfully")
        return redirect("budget")

    context = {
        "transaction": transaction,
        "form_for": "Transaction",
        "form_title": "Delete Transaction",
        "message": "Are you sure you want to delete this transaction?",
        "form_button": "Delete",
    }

    return render(request, "budget/generic_form.html", context)


def list_accounts(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    accounts = BankAccount.objects.filter(user=request.user).order_by("name")

    context = {"accounts": accounts}

    return render(request, "budget/account_list.html", context)


def account_detail(request, account_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    account = BankAccount.objects.get(id=account_id)
    transactions = Transaction.objects.filter(account=account).order_by("-date")

    context = {
        "account": account,
        "balance": account.get_balance(),
        "account_name": account.name,
        "transactions": transactions,
    }

    return render(request, "budget/account.html", context)


def add_account(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    if request.method == "POST":
        form = BankAccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            messages.success(request, "Account added successfully")
            return redirect("accont_detail", account.id)
        else:
            messages.error(request, "Error adding account")
    else:
        form = BankAccountForm()

    context = {
        "form": form,
        "form_for": "Account",
        "form_title": "Add A New Account",
        "form_button": "Add",
    }

    return render(request, "budget/generic_form.html", context)


def edit_account(request, account_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    account = BankAccount.objects.get(id=account_id)

    if request.method == "POST":
        form = BankAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, "Account updated successfully")
            return redirect("account_detail", account.id)
        else:
            messages.error(request, "Error updating account")
    else:
        form = BankAccountForm(instance=account)

    context = {
        "form": form,
        "form_for": account.name,
        "form_title": f"Edit ${account.name} Account",
        "form_button": "Update",
    }

    return render(request, "budget/generic_form.html", context)


def delete_account(request, account_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    account = BankAccount.objects.get(id=account_id)

    if request.method == "POST":
        account.delete()
        messages.success(request, "Account deleted successfully")
        return redirect("manage")

    context = {
        "account": account,
        "form_for": account.name,
        "form_title": f"Delete ${account.name} Account",
        "message": "Are you sure you want to delete this account?",
        "form_button": "Delete",
    }

    return render(request, "budget/generic_form.html", context)


def list_categories(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    categories = Category.objects.filter(user=request.user).order_by("name")

    context = {"categories": categories}

    return render(request, "budget/category_list.html", context)


def category_detail(request, category_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    category = Category.objects.get(id=category_id)

    context = {"category": category}

    return render(request, "budget/category.html", context)


def add_category(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, "Category added successfully")
            return redirect("category_detail", category.id)
        else:
            messages.error(request, "Error adding category")
    else:
        form = CategoryForm()

    context = {
        "form": form,
        "form_for": "Category",
        "form_title": "Add A New Category",
        "form_button": "Add",
    }

    return render(request, "budget/generic_form.html", context)


def edit_category(request, category_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    category = Category.objects.get(id=category_id)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully")
            return redirect("category_detail", category.id)
        else:
            messages.error(request, "Error updating category")
    else:
        form = CategoryForm(instance=category)

    context = {
        "form": form,
        "form_for": category.name,
        "form_title": f"Edit ${category.name} Category",
        "form_button": "Update",
    }

    return render(request, "budget/generic_form.html", context)


def delete_category(request, category_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    category = Category.objects.get(id=category_id)

    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully")
        return redirect("manage")

    context = {
        "category": category,
        "form_for": category.name,
        "form_title": f"Delete ${category.name} Category",
        "message": "Are you sure you want to delete this category?",
        "form_button": "Delete",
    }

    return render(request, "budget/generic_form.html", context)


def list_spending_budgets(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    budgets = SpendingBudget.objects.filter(user=request.user).order_by("name")

    context = {"budgets": budgets}

    return render(request, "budget/spending_budget_list.html", context)


def spending_budget_detail(request, budget_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    budget = SpendingBudget.objects.get(id=budget_id)
    progress = budget.get_budget_progress()

    context = {"budget": budget, "progress": progress}

    return render(request, "budget/spending_budget.html", context)


def add_spending_budget(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    if request.method == "POST":
        form = SpendingBudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, "Spending budget added successfully")
            return redirect("spending_budget_detail", budget.id)
        else:
            messages.error(request, "Error adding spending budget")
    else:
        form = SpendingBudgetForm()

    context = {
        "form": form,
        "form_for": "Spending Budget",
        "form_title": "Add A New Spending Budget",
        "form_button": "Add",
    }

    return render(request, "budget/generic_form.html", context)


def edit_spending_budget(request, budget_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    budget = SpendingBudget.objects.get(id=budget_id)

    if request.method == "POST":
        form = SpendingBudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, "Spending budget updated successfully")
            return redirect("spending_budget_detail", budget.id)
        else:
            messages.error(request, "Error updating spending budget")
    else:
        form = SpendingBudgetForm(instance=budget)

    context = {
        "form": form,
        "form_for": budget.name,
        "form_title": f"Edit ${budget.name} Budget",
        "form_button": "Update",
    }

    return render(request, "budget/generic_form.html", context)


def delete_spending_budget(request, budget_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    budget = SpendingBudget.objects.get(id=budget_id)

    if request.method == "POST":
        budget.delete()
        messages.success(request, "Spending budget deleted successfully")
        return redirect("manage")

    context = {
        "budget": budget,
        "form_for": budget.name,
        "form_title": f"Delete ${budget.name} Budget",
        "message": "Are you sure you want to delete this spending budget?",
        "form_button": "Delete",
    }

    return render(request, "budget/generic_form.html", context)


def list_savings_goals(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    goals = SavingsGoal.objects.filter(user=request.user).order_by("name")

    context = {"goals": goals}

    return render(request, "budget/saving_goals.html", context)


def savings_goal_detail(request, goal_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    goal = SavingsGoal.objects.get(id=goal_id)
    progress = goal.get_progress_display()

    context = {"goal": goal, "progress": progress}

    return render(request, "budget/savings_goal.html", context)


def add_savings_goal(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    if request.method == "POST":
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "Savings goal added successfully")
            return redirect("saving_goal_detail", goal.id)
        else:
            messages.error(request, "Error adding savings goal")
    else:
        form = SavingsGoalForm()

    context = {
        "form": form,
        "form_for": "Savings Goal",
        "form_title": "Add A New Savings Goal",
        "form_button": "Add",
    }

    return render(request, "budget/generic_form.html", context)


def edit_savings_goal(request, goal_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    goal = SavingsGoal.objects.get(id=goal_id)

    if request.method == "POST":
        form = SavingsGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, "Savings goal updated successfully")
            return redirect("saving_goal_detail", goal.id)
        else:
            messages.error(request, "Error updating savings goal")
    else:
        form = SavingsGoalForm(instance=goal)

    context = {
        "form": form,
        "form_for": goal.name,
        "form_title": f"Edit ${goal.name} Goal",
        "form_button": "Update",
    }

    return render(request, "budget/generic_form.html", context)


def delete_savings_goal(request, goal_id):
    if not request.user.is_authenticated:
        return render(request, "index.html")

    goal = SavingsGoal.objects.get(id=goal_id)

    if request.method == "POST":
        goal.delete()
        messages.success(request, "Savings goal deleted successfully")
        return redirect("manage")

    context = {
        "goal": goal,
        "form_for": goal.name,
        "form_title": f"Delete ${goal.name} Goal",
        "message": "Are you sure you want to delete this savings goal?",
        "form_button": "Delete",
    }

    return render(request, "budget/generic_form.html", context)

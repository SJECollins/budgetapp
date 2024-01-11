from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="budget"),
    path("manage/", views.manage, name="manage"),
    path("transactions/", views.list_transactions, name="transactions"),
    path(
        "transactions/<int:transaction_id>/",
        views.transaction_detail,
        name="transaction_detail",
    ),
    path(
        "transactions/<int:transaction_id>/edit/",
        views.edit_transaction,
        name="edit_transaction",
    ),
    path(
        "transactions/<int:transaction_id>/delete/",
        views.delete_transaction,
        name="delete_transaction",
    ),
    path("transactions/new/", views.add_transaction, name="add_transaction"),
    path("categories/", views.list_categories, name="categories"),
    path(
        "categories/<int:category_id>/", views.category_detail, name="category_detail"
    ),
    path(
        "categories/<int:category_id>/edit/", views.edit_category, name="edit_category"
    ),
    path(
        "categories/<int:category_id>/delete/",
        views.delete_category,
        name="delete_category",
    ),
    path("categories/new/", views.add_category, name="add_category"),
    path("accounts/", views.list_accounts, name="accounts"),
    path("accounts/<int:account_id>/", views.account_detail, name="account_detail"),
    path("accounts/<int:account_id>/edit/", views.edit_account, name="edit_account"),
    path(
        "accounts/<int:account_id>/delete/", views.delete_account, name="delete_account"
    ),
    path("accounts/new/", views.add_account, name="add_account"),
    path("spending-budgets/", views.list_spending_budgets, name="spending_budgets"),
    path(
        "spending-budgets/<int:budget_id>/",
        views.spending_budget_detail,
        name="spending_budget_detail",
    ),
    path(
        "spending-budgets/<int:budget_id>/edit/",
        views.edit_spending_budget,
        name="edit_spending_budget",
    ),
    path(
        "spending-budgets/<int:budget_id>/delete/",
        views.delete_spending_budget,
        name="delete_spending_budget",
    ),
    path(
        "spending-budgets/new/", views.add_spending_budget, name="add_spending_budget"
    ),
    path("saving-goals/", views.list_savings_goals, name="saving_goals"),
    path(
        "saving-goals/<int:goal_id>/",
        views.savings_goal_detail,
        name="saving_goal_detail",
    ),
    path(
        "saving-goals/<int:goal_id>/edit/",
        views.edit_savings_goal,
        name="edit_saving_goal",
    ),
    path(
        "saving-goals/<int:goal_id>/delete/",
        views.delete_savings_goal,
        name="delete_saving_goal",
    ),
    path("saving-goals/new/", views.add_savings_goal, name="add_saving_goal"),
]

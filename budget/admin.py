from django.contrib import admin
from .models import BankAccount, Category, Transaction, SpendingBudget, SavingsGoal


admin.site.register(BankAccount)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(SpendingBudget)
admin.site.register(SavingsGoal)

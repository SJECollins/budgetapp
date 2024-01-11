from django.utils import timezone
from .models import Transaction, TaskStatus


def update_recurring():
    today = timezone.now().date()
    transactions = Transaction.objects.filter(
        recurring=True, next_date__lte=today, new_transaction_created=False
    )

    for transaction in transactions:
        try:
            new_transaction = Transaction.objects.create(
                user=transaction.user,
                amount=transaction.amount,
                income_or_expense=transaction.income_or_expense,
                description=transaction.description,
                category=transaction.category,
                recurring=transaction.recurring,
                interval=transaction.interval,
                account=transaction.account,
                notes=transaction.notes,
                previous_transaction=transaction,
            )

            transaction.new_transaction_created = True
            transaction.save()
        except Exception as e:
            print(f"Error processing transaction {transaction.id}: {e}")

    TaskStatus.objects.filter(name="update-recurring").update(last_run=timezone.now())

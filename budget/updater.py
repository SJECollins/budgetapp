from datetime import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from .job import update_recurring
from .models import TaskStatus


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_recurring, "cron", hour=1)
    scheduler.start()


def check_task_status():
    last_run = TaskStatus.objects.filter(name="update-recurring").last_run

    threshold = timezone.now() - timezone.timedelta(hours=24)

    if last_run < threshold:
        update_recurring()

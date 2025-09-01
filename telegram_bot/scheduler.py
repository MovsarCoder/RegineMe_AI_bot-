# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from database.crud import CrudUser, CrudSubscription


def setup_scheduler():
    scheduler = AsyncIOScheduler(timezone=timezone("Europe/Moscow"))

    crud_user = CrudUser()
    crud_subscription = CrudSubscription()

    scheduler.add_job(
        crud_user.set_default_daily_limit,  # метод экземпляра
        CronTrigger(hour=10, minute=0)
    )

    scheduler.add_job(
        crud_subscription.remove_user_if_subscription_expired,  # метод экземпляра
        CronTrigger(hour=10, minute=0)
    )

    scheduler.start()

import datetime
from typing import Callable, Any, Coroutine

from telegram.ext import CallbackContext, ContextTypes

from core.utils.misc import get_server_datetime_by_user, get_server_timezone
from db.crud import users_cruds
from db.models import User


class Notificator:

    def create_notification_task(self, user_db: User, user_date: datetime.date) -> Callable[
        [Any], Coroutine[Any, Any, None]]:

        async def _task(context: ContextTypes.DEFAULT_TYPE):
            categories_lst = user_db.user_categories
            categories_dct = {category.name: sum(expense.amount for expense in category.expenses) for category in
                              categories_lst}
            total = sum(categories_dct.values())

            text_rows = [user_date.strftime("%Y-%m-%d")]
            text_rows.extend([f'{idx}) {key}: {val}' for idx, (key, val) in enumerate(categories_dct.items(), start=1)])
            text_rows.append(f'Total: {total}')
            await context.bot.send_message(chat_id=context.job.user_id, text='\n'.join(text_rows))

        return _task

    async def _add_user_to_notifications(self, user_db: User, context: CallbackContext):
        user_date: datetime.date = user_db.user_datetime.date()
        callback = self.create_notification_task(user_db=user_db, user_date=user_date)
        when_datetime = get_server_datetime_by_user(
            user_datetime=datetime.datetime.now().replace(hour=23, minute=59), user_utc_offset=user_db.user_utc_offset)
        # when_datetime = get_server_datetime_by_user(
        #     user_datetime=datetime.datetime.now()+datetime.timedelta(seconds=10), user_utc_offset=user_db.user_utc_offset)
        context.job_queue.run_once(callback=callback, when=when_datetime, name=str(user_db.id),
                                   chat_id=user_db.telegram_id, user_id=user_db.telegram_id)

    async def fetch_users_to_notifications(self, context: CallbackContext):
        users_to_notifications = users_cruds.get_users_for_notifications()
        for user_db in users_to_notifications:
            await self._add_user_to_notifications(user_db=user_db, context=context)

    async def add_user_to_notifications(self, user_db: User, context: CallbackContext):
        if user_db.utc_offset is not None and user_db.options.get('notifications_enabled'):
            await self._add_user_to_notifications(user_db=user_db, context=context)

    def delete_user_from_notifications(self, user_db: User, context: CallbackContext):
        jobs = context.job_queue.get_jobs_by_name(name=str(user_db.id))
        for job in jobs:
            job.schedule_removal()

    def start_periodic_fetch_users(self, context: CallbackContext):
        time = datetime.time(hour=0, minute=0).replace(tzinfo=get_server_timezone())
        context.job_queue.run_daily(callback=self.fetch_users_to_notifications, time=time,
                                    days=(0, 1, 2, 3, 4, 5, 6),
                                    name='Notificator')

notificator = Notificator()

import datetime
import functools
import telegram
from sqlalchemy import and_, Boolean
from telegram import Update
from telegram.ext import CallbackContext

from core.handlers.commands import COMMANDS
from core.utils.misc import get_utc_datetime_now
from db.database import get_db
from db.models import User


def create_user(tg_user: telegram.User) -> User:
    user_db = User(telegram_id=tg_user.id, creation_date=get_utc_datetime_now().date())
    with get_db() as db:
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
    return user_db


def get_user_by_telegram_id(telegram_user_id: int) -> User | None:
    with get_db() as db:
        return db.query(User).filter_by(telegram_id=telegram_user_id).first()


def set_user_utc_offset(utc_offset: int, user_db: User) -> User:
    with get_db() as db:
        user_db.utc_offset = utc_offset
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
        return user_db

def update_user_options(options_in: dict, user_db: User) -> User:
    with get_db() as db:
        user_db.options = user_db.options | options_in
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
        return user_db

def get_users_for_notifications() -> list:
    with get_db() as db:
        return db.query(User).filter(and_(User.utc_offset != None,
                                          User.options['notifications_enabled'].astext.cast(Boolean)==True)).all()

def needs_user(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        update: Update = args[0]

        if update.message is not None:
            tg_user = update.message.from_user
        else:
            tg_user = update.callback_query.from_user

        user_db = get_user_by_telegram_id(tg_user.id)
        msg = update.effective_message

        if user_db is None:
            user_db = create_user(tg_user)
            await msg.reply_text('Вы успешно зарегестрированы!')
        return await func(*args, **kwargs, user_db=user_db)

    return wrapper


def utc_warning(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        update: Update = args[0]

        user_db: User = kwargs['user_db']

        msg = update.effective_message

        if user_db.utc_offset is None:
            await msg.reply_text(
                f'Внимание! Не установлен часовой пояс!\nУведомления в конце дня присылаться не будут!\n{COMMANDS["set_utc_offset"]}')
        return await func(*args, **kwargs)

    return wrapper

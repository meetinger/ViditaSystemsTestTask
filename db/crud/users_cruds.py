import datetime
import functools
import telegram
from telegram import Update

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
        return user_db


def needs_user(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        update: Update = args[0]

        if update.message is not None:
            msg = update.message
        else:
            msg = update.callback_query.message

        tg_user = msg.from_user

        user_db = get_user_by_telegram_id(tg_user.id)

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

        if update.message is not None:
            msg = update.message
        else:
            msg = update.callback_query.message

        if user_db.utc_offset is None:
            await msg.reply_text(
                f'Внимание! Не установлен часовой пояс!\nУведомления в конце дня присылаться не будут!\n{COMMANDS["set_utc_offset"]}')
        return await func(*args, **kwargs)

    return wrapper

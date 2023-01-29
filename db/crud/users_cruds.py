import datetime
import functools
import telegram


from db.database import get_db
from db.models import User


def create_user(tg_user: telegram.User) -> User:
    user_db = User(telegram_id=tg_user.id, registration_date=datetime.datetime.now().date())
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
        db.add(utc_offset)
        db.commit()
        return user_db

def needs_user(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        update = args[0]
        tg_user = update.message.from_user
        user_db = get_user_by_telegram_id(tg_user.id)
        if user_db is None:
            user_db = create_user(tg_user)
            await update.message.reply_text('Вы успешно зарегестрированы!')
        return await func(*args, **kwargs, user_db=user_db)
    return wrapper

def needs_timezone(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        update = args[0]
        tg_user = update.message.from_user
        user_db = get_user_by_telegram_id(tg_user.id)
        if user_db.utc_offset is None:
            await update.message.reply_text('Для использования данной команды, установите часовой пояс с помощью команды:\n/set_utc_offset <кол-во минут от UTC>')
            return
        return await func(*args, **kwargs, user_db=user_db)
    return wrapper

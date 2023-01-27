import db.crud.users_cruds as users_cruds

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

from core.handlers.keyboards import build_categories_buttons
from db.models import User


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> User:
    tg_user = update.message.from_user
    user_db = users_cruds.get_user_by_telegram_id(tg_user.id)
    if user_db is None:
        user_db = users_cruds.create_user(tg_user)
        await update.message.reply_text('Вы успешно зарегестрированы!')
    else:
        await update.message.reply_text('Вы уже зарегестрированы!')
    return user_db


@users_cruds.needs_user
async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db: User):
    user_categories = user_db.user_categories

    reply_data = await build_categories_buttons(user_categories)

    if isinstance(reply_data, str):
        await update.message.reply_text(reply_data)
        return []
    await update.message.reply_text(text='Ваши статьи расходов:', reply_markup=InlineKeyboardMarkup([reply_data]))


HANDLERS = [CommandHandler('start', start), CommandHandler('categories', categories)]

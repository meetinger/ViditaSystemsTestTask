import datetime
import enum

import db.crud.users_cruds as users_cruds
import db.crud.categories_cruds as categories_cruds

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler

from core.utils.calendar_keyboard import CalendarStates, gen_calendar_with_offsets, date_selection_handler
from db.models import User, Category


class States(enum.IntEnum):
    CATEGORIES_SELECTION_AWAIT = 1


def build_categories_buttons(categories: list[Category]) -> str | list[InlineKeyboardButton]:
    if not categories:
        return 'У Вас ещё нет категорий расходов'
    return [InlineKeyboardButton(text=category.name, callback_data=str(category.user_id)) for category in categories]


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

    reply_data = build_categories_buttons(user_categories)

    if isinstance(reply_data, str):
        await update.message.reply_text(reply_data)
        return []
    await update.message.reply_text(text='Ваши статьи расходов:', reply_markup=InlineKeyboardMarkup([reply_data]))
    return States.CATEGORIES_SELECTION_AWAIT


@users_cruds.needs_user
async def set_category(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db: User):
    category_name = " ".join(context.args)
    category_db = categories_cruds.get_category_by_name(category_name=category_name, user_db=user_db)
    if category_db is None:
        category_db = categories_cruds.create_category(category_name=category_name, user_db=user_db)
        await update.message.reply_text('Категория создана')
    else:
        await update.message.reply_text('Категория с таким именем уже существует')


async def category_callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    category_id = int(query.data)


async def calendar_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Календарь')
    context.user_data['calendar_start_date'] = datetime.date(year=2022, month=2, day=24)
    context.user_data['calendar_end_date'] = datetime.date(year=2023, month=1, day=29)
    return CalendarStates.DATE_SELECTION_AWAIT


async def show_calendar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_date = context.user_data['calendar_start_date']
    end_date = context.user_data['calendar_end_date']
    await update.message.reply_text('Выберете дату:',
                                    reply_markup=gen_calendar_with_offsets(start_date=start_date, end_date=end_date))
    return CalendarStates.DATE_SELECTION_AWAIT


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Дата: {context.user_data.get("selected_date")}')
    await update.message.edit_reply_markup()


async def show_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Дата: {context.user_data.get("selected_date")}')


HANDLERS = [CommandHandler('start', start), CommandHandler('categories', categories),
            CommandHandler('calendar_test', calendar_test),
            ConversationHandler(entry_points=[CommandHandler('show_calendar', show_calendar_handler)],
                                states={
                                    CalendarStates.DATE_SELECTION_AWAIT: [CallbackQueryHandler(date_selection_handler)]
                                },
                                fallbacks=[CommandHandler('cancel', cancel)], per_message=False
                                ),
            CommandHandler('show_date', show_date),
            ]

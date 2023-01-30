import datetime
import decimal
from decimal import Decimal

import db.crud.users_cruds as users_cruds
import db.crud.categories_cruds as categories_cruds

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from telegram.ext import ContextTypes, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler, \
    MessageHandler, filters

from core.handlers.commands import COMMANDS
from core.utils.calendar_keyboard import gen_calendar_with_offsets, \
    create_date_selection_handler
from core.utils.misc import get_utc_datetime_now
from db.crud import expenses_cruds
from db.models import User, Category, Expense


class States:
    CATEGORIES_SELECTION_AWAIT = 1
    DATE_SELECTION_AWAIT = 2
    SHOW_EXPENSES = 3
    EXPENSES_ACTION_AWAIT = 4
    ENTER_EXPENSE_NAME = 5
    ENTER_EXPENSE_AMOUNT = 6
    ENTER_EXPENSE_CURRENCY = 7


def build_cancel_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton('Отмена', callback_data='cancel')]])

def build_help_str() -> str:
    rows = ['Доступные команды:']
    rows.extend([f'{idx}) {val}' if key in val else f'{idx}) /{key} — {val}' for idx, (key, val) in enumerate(COMMANDS.items(), start=1)])
    return '\n'.join(rows)

def build_expenses_reply_data(expenses_lst: list[Expense]) -> dict:
    expenses_text_lst = ['Статьи расходов:']
    keyboard = []
    for idx, expense in enumerate(expenses_lst, start=1):
        expenses_text_lst.append(f'{idx}) {expense.name}: {expense.amount}')
        keyboard.append(
            [InlineKeyboardButton(text=f'Удалить статью расходов {idx}', callback_data=f'del_exp:{expense.id}')])
    keyboard.append([InlineKeyboardButton(text='Добавить расход', callback_data='create_exp')])
    return {'text': '\n'.join(expenses_text_lst), 'reply_markup': InlineKeyboardMarkup(keyboard)}


def build_categories_buttons(categories_lst: list[Category]) -> str | InlineKeyboardMarkup:
    if not categories_lst:
        return 'У Вас ещё нет категорий расходов'
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=category.name, callback_data=str(category.user_id))] for category in
         categories_lst])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.message.from_user
    user_db = users_cruds.get_user_by_telegram_id(tg_user.id)
    if user_db is None:
        user_db = users_cruds.create_user(tg_user)
        await update.message.reply_text('Вы успешно зарегестрированы!')
    else:
        await update.message.reply_text('Вы уже зарегестрированы!')
    return ConversationHandler.END


@users_cruds.needs_user
async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db: User) -> int:
    user_categories = user_db.user_categories

    reply_data = build_categories_buttons(user_categories)

    if isinstance(reply_data, str):
        await update.message.reply_text(reply_data)
        return ConversationHandler.END

    await update.message.reply_text(text='Ваши категории расходов:', reply_markup=reply_data)
    return States.CATEGORIES_SELECTION_AWAIT


@users_cruds.needs_user
async def set_category(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db: User):
    if not context.args:
        await update.message.reply_text(f'Неверный синтаксис команды\n{COMMANDS["set_category"]}')
    category_name = " ".join(context.args)
    category_db = categories_cruds.get_category_by_name(category_name=category_name, user_db=user_db)
    if category_db is None:
        category_db = categories_cruds.create_category(category_name=category_name, user_db=user_db)
        await update.message.reply_text('Категория создана')
    else:
        await update.message.reply_text('Категория с таким именем уже существует')


@users_cruds.needs_user
async def category_callback_handler(update: Update, context: CallbackContext, user_db: User) -> int:
    query = update.callback_query
    await query.answer()
    category_id = int(query.data)
    category = categories_cruds.get_category_by_id(category_id=category_id, user_db=user_db)

    context.user_data['category'] = category

    start_date = category.creation_date - datetime.timedelta(days=1)
    end_date = get_utc_datetime_now().date() + datetime.timedelta(days=1)

    context.user_data['calendar_start_date'] = start_date
    context.user_data['calendar_end_date'] = end_date

    await update.callback_query.message.reply_text('Выберете дату:',
                                                   reply_markup=gen_calendar_with_offsets(start_date=start_date,
                                                                                          end_date=end_date))

    return States.DATE_SELECTION_AWAIT


@users_cruds.needs_user
async def show_expenses(update: Update, context: CallbackContext, user_db: User) -> int:
    category = context.user_data['category']
    creation_date = context.user_data['selected_date']
    expenses = expenses_cruds.get_category_expenses_by_date(category_db=category, creation_date=creation_date,
                                                            user_db=user_db)
    await update.callback_query.message.reply_text(**build_expenses_reply_data(expenses))
    return States.EXPENSES_ACTION_AWAIT


@users_cruds.needs_user
async def expenses_action_handler(update: Update, context: CallbackContext, user_db: User) -> int:
    query = update.callback_query
    await query.answer()

    query_data = query.data
    if 'del_exp' in query_data:
        expense_id = int(query_data.split(':')[-1])
        expenses_cruds.delete_expense(expense_id=expense_id, user_db=user_db)
        await query.message.reply_text('Статья расходов удалена')
        expenses = expenses_cruds.get_category_expenses_by_date(category_db=context.user_data['category'],
                                                                creation_date=context.user_data['selected_date'],
                                                                user_db=user_db)
        await query.message.reply_text(**build_expenses_reply_data(expenses))
        return States.EXPENSES_ACTION_AWAIT

    await query.message.reply_text('Введите название статьи расходов:', reply_markup=build_cancel_markup())
    context.user_data['expense_data'] = {}
    return States.ENTER_EXPENSE_NAME


@users_cruds.needs_user
async def expense_name(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db: User) -> int:
    context.user_data['expense_data']['name'] = update.message.text
    await update.message.reply_text('Введите расход(только цифры):', reply_markup=build_cancel_markup())
    return States.ENTER_EXPENSE_AMOUNT


@users_cruds.needs_user
async def expense_amount_and_create_expense(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db: User) -> int:
    try:
        context.user_data['expense_data']['amount'] = Decimal(update.message.text)
    except decimal.InvalidOperation:
        await update.message.reply_text('Введите расход(только цифры):')
        return States.ENTER_EXPENSE_AMOUNT
    expense_in = context.user_data['expense_data']
    expenses_cruds.create_expense(expense_in=expense_in, category_db=context.user_data['category'], user_db=user_db,
                                  creation_date=context.user_data['selected_date'])
    await update.message.reply_text('Статья расходов добавлена')

    expenses = expenses_cruds.get_category_expenses_by_date(category_db=context.user_data['category'],
                                                            creation_date=context.user_data['selected_date'],
                                                            user_db=user_db)
    await update.message.reply_text(**build_expenses_reply_data(expenses))
    return States.EXPENSES_ACTION_AWAIT


@users_cruds.needs_user
async def total(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db: User):
    expenses = expenses_cruds.get_all_user_expenses(user_db=user_db)
    total_sum = sum(expense.amount for expense in expenses)
    await update.message.reply_text(f'За всё время расходы составили:\n{total_sum}')


@users_cruds.needs_user
async def set_utc_offset(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db: User):
    if not context.args:
        await update.message.reply_text(f'Неверный синтаксис команды\n{COMMANDS["set_utc_offset"]}')
        return
    try:
        timezone = int(context.args[0])
    except (ValueError, IndexError):
        await update.message.reply_text(f'Неверный синтаксис команды\n{COMMANDS["set_utc_offset"]}')
        return
    users_cruds.set_user_utc_offset(utc_offset=timezone, user_db=user_db)
    await update.message.reply_text(f'Часовой пояс установлен: {timezone}min от UTC')


@users_cruds.needs_user
@users_cruds.utc_warning
async def enable_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db: User):
    users_cruds.update_user_options(options_in={'notifications_enabled': True}, user_db=user_db)
    await update.message.reply_text(text='Уведомления включены!')


@users_cruds.needs_user
@users_cruds.utc_warning
async def disable_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db: User):
    users_cruds.update_user_options(options_in={'notifications_enabled': False}, user_db=user_db)
    await update.message.reply_text(text='Уведомления отключены!')



async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Неизвестная команда!\n'+build_help_str())

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=build_help_str())


async def cancel(update: Update, context: CallbackContext):
    await update.callback_query.message.reply_text('Команда прервана')
    await update.callback_query.message.edit_reply_markup()
    return ConversationHandler.END


HANDLERS = [CommandHandler('start', start),
            CommandHandler('set_category', set_category),
            CommandHandler('set_utc_offset', set_utc_offset),
            CommandHandler('total', total),
            CommandHandler('enable_notifications', enable_notifications),
            CommandHandler('disable_notifications', disable_notifications),
            CommandHandler('help', help),
            ConversationHandler(entry_points=[CommandHandler('categories', categories)],
                                states={
                                    States.CATEGORIES_SELECTION_AWAIT: [
                                        CallbackQueryHandler(category_callback_handler)],
                                    States.DATE_SELECTION_AWAIT: [CallbackQueryHandler(
                                        create_date_selection_handler(await_selection_state=States.DATE_SELECTION_AWAIT,
                                                                      selected_callback=show_expenses))],
                                    States.SHOW_EXPENSES: [CallbackQueryHandler(show_expenses)],
                                    States.EXPENSES_ACTION_AWAIT: [CallbackQueryHandler(expenses_action_handler)],
                                    States.ENTER_EXPENSE_NAME: [
                                        MessageHandler(filters=filters.ALL, callback=expense_name)],
                                    States.ENTER_EXPENSE_AMOUNT: [MessageHandler(filters=filters.ALL,
                                                                                 callback=expense_amount_and_create_expense)],
                                },
                                fallbacks=[CallbackQueryHandler(cancel)], per_message=False, allow_reentry=True
                                ),
            MessageHandler(filters=filters.COMMAND, callback=unknown_command),
            ]

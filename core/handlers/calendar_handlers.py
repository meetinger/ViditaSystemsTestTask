import datetime
import enum
import locale
import calendar
from typing import Coroutine, Callable

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, ConversationHandler

from core.utils.misc import stringify, offset_date


class CalendarStates(enum.IntEnum):
    CONTINUE = enum.auto()
    # END = enum.auto


class CalendarCallbackTypes(enum.IntEnum):
    IGNORE = enum.auto()
    SELECT_DATE = enum.auto()
    PREV_MONTH = enum.auto()
    NEXT_MONTH = enum.auto()
    NEXT_YEAR = enum.auto()
    PREV_YEAR = enum.auto()

# CALENDAR_CALLBACK

def get_last_day_of_month(year: int, month: int) -> int:
    return calendar.monthrange(year=year, month=month)[1]


def encode_callback_data(callback_type: CalendarCallbackTypes, year: int = None, month: int = None, day: int = None, idx: int = None) -> str:
    encoded = ';'.join([str(callback_type.value)] + [stringify(year), stringify(month), stringify(day), stringify(idx)])
    return encoded


def decode_callback_data(callback_data: str) -> dict | None:
    data = callback_data.split(';')
    try:
        return {key: None if not data[idx] else data[idx] for idx, key in
                enumerate(('callback_type', 'year', 'month', 'day', 'idx'))}
    except Exception:
        return None


def build_calendar_markup(year: int = None, month: int = None, start_day: int = None, end_day: int = None,
                          prev_month: bool = True, next_month: bool = True, prev_year: bool = True,
                          next_year: bool = True):
    keyboard = []

    date_now = datetime.datetime.now().date()

    if year is None:
        year = date_now.year
    if month is None:
        month = date_now.month
    if start_day is None:
        start_day = 1
    if end_day is None:
        end_day = get_last_day_of_month(year=year, month=month)

    current_date = datetime.date(year=year, month=month, day=start_day)

    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

    ignore_callback_idx = 0

    def ignore_callback_data() -> str:
        nonlocal ignore_callback_idx
        encoded = encode_callback_data(CalendarCallbackTypes.IGNORE, idx=ignore_callback_idx)
        ignore_callback_idx += 1
        return encoded

    # ignore_callback = ignore_callback_data()

    def empty_btn():
        return InlineKeyboardButton(text=' ', callback_data=ignore_callback_data())

    # первая строка - год
    keyboard.append([InlineKeyboardButton(text='<',
                                          callback_data=encode_callback_data(
                                              callback_type=CalendarCallbackTypes.PREV_YEAR,
                                              year=year)) if prev_year else empty_btn(),
                     InlineKeyboardButton(text=current_date.strftime('%Y'), callback_data=ignore_callback_data()),
                     InlineKeyboardButton(text='>',
                                          callback_data=encode_callback_data(
                                              callback_type=CalendarCallbackTypes.NEXT_YEAR,
                                              year=year)) if next_year else empty_btn()
                     ])

    # вторая строчка - месяц
    keyboard.append([InlineKeyboardButton(text='<',
                                          callback_data=encode_callback_data(
                                              callback_type=CalendarCallbackTypes.PREV_MONTH,
                                              year=year,
                                              month=month)) if prev_month else empty_btn(),
                     InlineKeyboardButton(text=current_date.strftime('%b'), callback_data=ignore_callback_data()),
                     InlineKeyboardButton(text='>',
                                          callback_data=encode_callback_data(
                                              callback_type=CalendarCallbackTypes.NEXT_MONTH,
                                              year=year,
                                              month=month)) if next_month else empty_btn()
                     ])

    # третья строка - дни недели
    keyboard.append([InlineKeyboardButton(text=day, callback_data=ignore_callback_data()) for day in
                     ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')])

    # последующие строки - дни недели
    month_calendar = calendar.monthcalendar(year=year, month=month)

    for week in month_calendar:
        row = []
        for day in week:
            if day == 0 or day < start_day or day > end_day:
                row.append(empty_btn())
            else:
                row.append(InlineKeyboardButton(text=str(day), callback_data=encode_callback_data(
                    callback_type=CalendarCallbackTypes.SELECT_DATE, year=year, month=month, day=day)))
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


async def date_selection_handler(update: Update, context: CallbackContext, start_date: datetime.date,
                                 end_date: datetime.date) -> CalendarStates | int:
    def gen_calendar_with_offsets(current_date: datetime.date, month_offset: int = 0,
                                  year_offset: int = 0) -> InlineKeyboardMarkup:
        nonlocal start_date, end_date
        date_with_offset = offset_date(in_date=current_date, month_offset=month_offset,
                                       year_offset=year_offset)

        cur_min_day, cur_max_day = calendar.monthrange(year=date_with_offset.year, month=date_with_offset.month)

        prev_month = offset_date(in_date=date_with_offset, month_offset=-1, year_offset=0) > start_date
        next_month = offset_date(in_date=date_with_offset, month_offset=1, year_offset=0) < end_date

        prev_year = offset_date(in_date=date_with_offset, month_offset=0, year_offset=-1) > start_date
        next_year = offset_date(in_date=date_with_offset, month_offset=0, year_offset=1) > end_date

        if not prev_month:
            cur_min_day = start_date.day
        if not next_month:
            cur_max_day = end_date.day

        return build_calendar_markup(year=date_with_offset.year, month=date_with_offset.month, start_day=cur_min_day,
                                     end_day=cur_max_day, prev_month=prev_month, next_month=next_month,
                                     prev_year=prev_year, next_year=next_year)

    query = update.callback_query

    if query is None:
        await update.message.reply_text(text='Выберете дату', reply_markup=gen_calendar_with_offsets(end_date))
        return CalendarStates.CONTINUE

    # print(query)

    callback_data = decode_callback_data(query.data)

    if callback_data is None:
        await query.answer()
        return CalendarStates.CONTINUE

    def date_from_callback(_callback_data: dict) -> datetime.date:
        return datetime.date(
            **{key: int(_callback_data[key]) if _callback_data.get(key, None) is not None else 1 for key in
               ('year', 'month', 'day')})

    cur_date_from_callback = date_from_callback(callback_data)

    await query.answer()

    match CalendarCallbackTypes[callback_data['callback_type']]:
        case CalendarCallbackTypes.SELECT_DATE:
            context.user_data['selected_date'] = cur_date_from_callback
            await update.message.edit_reply_markup()
            return ConversationHandler.END

        case CalendarCallbackTypes.PREV_MONTH:
            await update.message.edit_reply_markup(
                gen_calendar_with_offsets(current_date=cur_date_from_callback, month_offset=-1))

        case CalendarCallbackTypes.NEXT_MONTH:
            await update.message.edit_reply_markup(
                gen_calendar_with_offsets(current_date=cur_date_from_callback, month_offset=1))

        case CalendarCallbackTypes.PREV_YEAR:
            await update.message.edit_reply_markup(
                gen_calendar_with_offsets(current_date=cur_date_from_callback, year_offset=-1))

        case CalendarCallbackTypes.NEXT_YEAR:
            await update.message.edit_reply_markup(
                gen_calendar_with_offsets(current_date=cur_date_from_callback, year_offset=1))

        case _:
            await query.answer()

    return CalendarStates.CONTINUE


def create_handler(start_date: datetime.date, end_date: datetime.date) -> Callable[
    [Update, CallbackContext], Coroutine]:
    async def _date_selection_handler(update: Update, context: CallbackContext):
        return await date_selection_handler(update=update, context=context, start_date=start_date, end_date=end_date)

    return _date_selection_handler

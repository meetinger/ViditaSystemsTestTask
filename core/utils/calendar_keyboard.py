import asyncio
import calendar
import datetime
import locale
from typing import Callable, Coroutine, Any

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, ConversationHandler

from core.utils.misc import stringify, offset_date, get_utc_datetime_now


class CalendarCallbackTypes:
    IGNORE = 1
    SELECT_DATE = 2
    PREV_MONTH = 3
    NEXT_MONTH = 4
    NEXT_YEAR = 5
    PREV_YEAR = 6


# CALENDAR_CALLBACK

def get_last_day_of_month(year: int, month: int) -> int:
    return calendar.monthrange(year=year, month=month)[1]


def encode_callback_data(callback_type: int, year: int = None, month: int = None, day: int = None,
                         idx: int = None) -> str:
    encoded = ';'.join([str(callback_type)] + [stringify(year), stringify(month), stringify(day), stringify(idx)])
    return encoded


def decode_callback_data(callback_data: str) -> dict | None:
    data = callback_data.split(';')
    try:
        return {key: None if not data[idx] else int(data[idx]) for idx, key in
                enumerate(('callback_type', 'year', 'month', 'day', 'idx'))}
    except Exception:
        return None


def build_calendar_markup(year: int = None, month: int = None, start_day: int = None, end_day: int = None,
                          prev_month: bool = True, next_month: bool = True, prev_year: bool = True,
                          next_year: bool = True):
    keyboard = []

    date_now = get_utc_datetime_now().date()

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
            if day == 0 or not (start_day <= day <= end_day):
                row.append(empty_btn())
            else:
                row.append(InlineKeyboardButton(text=str(day), callback_data=encode_callback_data(
                    callback_type=CalendarCallbackTypes.SELECT_DATE, year=year, month=month, day=day)))
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def gen_calendar_with_offsets(start_date: datetime.date = None,
                              end_date: datetime.date = None, current_date: datetime.date = None, month_offset: int = 0,
                              year_offset: int = 0) -> InlineKeyboardMarkup:
    if current_date is None:
        current_date = end_date or start_date or datetime.datetime.now().astimezone().date()

    date_with_offset = offset_date(in_date=current_date, month_offset=month_offset,
                                   year_offset=year_offset)

    if start_date is not None and end_date is not None and not start_date <= date_with_offset <= end_date:
        date_with_offset = current_date

    cur_min_day, cur_max_day = 1, calendar.monthrange(year=date_with_offset.year, month=date_with_offset.month)[1]

    prev_month = start_date is None or offset_date(in_date=date_with_offset, month_offset=-1, year_offset=0) >= start_date
    next_month = end_date is None or offset_date(in_date=date_with_offset, month_offset=1, year_offset=0) <= end_date

    prev_year = start_date is None or offset_date(in_date=date_with_offset, month_offset=0, year_offset=-1) >= start_date
    next_year = end_date is None or offset_date(in_date=date_with_offset, month_offset=0, year_offset=1) <= end_date

    if start_date is not None and date_with_offset.replace(day=1) == start_date.replace(day=1):
        cur_min_day = start_date.day
    if end_date is not None and date_with_offset.replace(day=1) == end_date.replace(day=1):
        cur_max_day = end_date.day

    return build_calendar_markup(year=date_with_offset.year, month=date_with_offset.month, start_day=cur_min_day,
                                 end_day=cur_max_day, prev_month=prev_month, next_month=next_month,
                                 prev_year=prev_year, next_year=next_year)


async def date_selection_handler(update: Update, context: CallbackContext, await_selection_state: int,
                                 selected_state: int = None,
                                 selected_callback: Callable[[Update, CallbackContext], Any] = None) -> int:
    start_date = context.user_data['calendar_start_date']
    end_date = context.user_data['calendar_end_date']

    query = update.callback_query

    if query is None:
        return await_selection_state

    callback_data = decode_callback_data(query.data)

    if callback_data is None:
        await query.answer()
        return await_selection_state

    def date_from_callback(_callback_data: dict) -> datetime.date:
        return datetime.date(
            **{key: int(_callback_data[key]) if _callback_data.get(key, None) is not None else 1 for key in
               ('year', 'month', 'day')})

    cur_date_from_callback = date_from_callback(callback_data)

    await query.answer()
    match callback_data['callback_type']:
        case CalendarCallbackTypes.SELECT_DATE:
            context.user_data['selected_date'] = cur_date_from_callback
            await query.edit_message_reply_markup()

            if selected_callback is not None:
                if asyncio.iscoroutinefunction(selected_callback):
                    return await selected_callback(update, context)
                else:
                    return selected_callback(update, context)
            if selected_state is not None:
                return selected_state

        case CalendarCallbackTypes.PREV_MONTH:
            await query.edit_message_reply_markup(
                gen_calendar_with_offsets(start_date=start_date, end_date=end_date, current_date=cur_date_from_callback,
                                          month_offset=-1))

        case CalendarCallbackTypes.NEXT_MONTH:
            await query.edit_message_reply_markup(
                gen_calendar_with_offsets(start_date=start_date, end_date=end_date, current_date=cur_date_from_callback,
                                          month_offset=1))

        case CalendarCallbackTypes.PREV_YEAR:
            await query.edit_message_reply_markup(
                gen_calendar_with_offsets(start_date=start_date, end_date=end_date, current_date=cur_date_from_callback,
                                          year_offset=-1))

        case CalendarCallbackTypes.NEXT_YEAR:
            await query.edit_message_reply_markup(
                gen_calendar_with_offsets(start_date=start_date, end_date=end_date, current_date=cur_date_from_callback,
                                          year_offset=1))

        case _:
            await query.answer()

    return await_selection_state


def create_date_selection_handler(await_selection_state: int, selected_state: int = ConversationHandler.END,
                                  selected_callback: Callable[[Update, CallbackContext], Any] = None) -> Callable[[Update, CallbackContext], Coroutine]:
    async def _date_selection_handler(update: Update, context: CallbackContext):
        return await date_selection_handler(update=update, context=context, await_selection_state=await_selection_state,
                                            selected_state=selected_state, selected_callback=selected_callback)

    return _date_selection_handler

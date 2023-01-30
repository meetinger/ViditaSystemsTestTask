import calendar
import datetime

from typing import Any


def mod_negative(a: int, b: int) -> int:
    res = a % b
    return res if not res else res - b if a < 0 else res


def stringify(val: Any) -> str:
    if val is None:
        return ''
    return str(val)


def get_utc_datetime_now():
    return datetime.datetime.now(datetime.timezone.utc)


def offset_date(in_date: datetime.date, year_offset: int = 0, month_offset: int = 0):
    cur_year = in_date.year
    cur_month = in_date.month
    cur_day = in_date.day

    year_delta = int(month_offset / 12) + year_offset
    month_delta = mod_negative(month_offset, 12)

    if cur_month + month_delta < 1:
        month_delta = 12 - abs(month_delta)
        year_delta -= 1
    if cur_month + month_delta > 12:
        month_delta = -(12 - abs(month_delta))
        year_delta += 1

    replace_year = cur_year + year_delta
    replace_month = cur_month + month_delta

    max_day = calendar.monthrange(year=replace_year, month=replace_month)[1]

    replace_day = cur_day if cur_day < max_day else max_day

    return in_date.replace(year=replace_year, month=replace_month, day=replace_day)

def get_server_datetime_by_user(user_datetime: datetime.datetime, user_utc_offset: datetime.timedelta):
    return (user_datetime.astimezone(datetime.timezone.utc).replace(tzinfo=None) + user_utc_offset).astimezone()

def get_server_timezone() -> datetime.tzinfo:
    tz = datetime.datetime.now().astimezone()
    return datetime.timezone(tz.utcoffset())

def get_time_from_datetime(dt: datetime.datetime):
    return dt.time().replace(tzinfo=dt.tzinfo)
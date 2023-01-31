import datetime

from sqlalchemy import Column, Integer, Date, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from core.utils.misc import get_utc_datetime_now
from db.database import Base


class User(Base):
    """Класс пользователя"""
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id = Column(BigInteger, index=True)
    creation_date = Column(Date)
    utc_offset = Column(Integer, nullable=True)

    options = Column(JSONB, index=True, default={})

    user_categories = relationship('Category', lazy='subquery', back_populates='user')
    user_expenses = relationship('Expense', lazy='subquery', back_populates='user')

    @property
    def user_utc_offset(self) -> datetime.timedelta:
        return datetime.timedelta(minutes=self.utc_offset)

    @property
    def user_datetime(self) -> datetime.datetime:
        return get_utc_datetime_now().astimezone(datetime.timezone(self.user_utc_offset))


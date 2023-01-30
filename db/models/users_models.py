import datetime

from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship

from core.utils.misc import get_utc_datetime_now
from db.database import Base


class User(Base):
    """Класс пользователя"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, index=True)
    creation_date = Column(Date)
    utc_offset = Column(Integer, nullable=True)

    user_categories = relationship('Category', lazy='subquery', back_populates='user')
    user_expenses = relationship('Expense', lazy='subquery', back_populates='user')

    @property
    def user_datetime(self):
        return get_utc_datetime_now() + datetime.timedelta(minutes=self.utc_offset)

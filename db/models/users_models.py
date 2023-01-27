from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship

from db.database import Base


class User(Base):
    """Класс пользователя"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, index=True)
    registration_date = Column(Date)

    user_categories = relationship('Category', lazy='subquery', back_populates='user')
    user_expenses = relationship('Expense', lazy='subquery', back_populates='user')

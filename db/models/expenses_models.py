from sqlalchemy import Column, Integer, ForeignKey, String, Date, Numeric
from sqlalchemy.orm import relationship

from db.database import Base


class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    amount = Column(Numeric)
    currency = Column(String)

    creation_date = Column(Date, index=True)

    category_id = Column(Integer, ForeignKey('categories.id'), index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)

    category = relationship('Category', lazy='subquery', back_populates='expenses')
    user = relationship('User', lazy='subquery', back_populates='user_expenses')

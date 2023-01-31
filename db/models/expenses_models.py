from sqlalchemy import Column, ForeignKey, String, Date, Numeric, BigInteger
from sqlalchemy.orm import relationship

from db.database import Base


class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(BigInteger, primary_key=True, index=True)

    name = Column(String)
    amount = Column(Numeric)

    creation_date = Column(Date, index=True)

    category_id = Column(BigInteger, ForeignKey('categories.id'), index=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), index=True)

    category = relationship('Category', lazy='subquery', back_populates='expenses')
    user = relationship('User', lazy='subquery', back_populates='user_expenses')

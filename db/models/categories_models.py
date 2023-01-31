from sqlalchemy import Column, ForeignKey, String, Date, BigInteger
from sqlalchemy.orm import relationship

from db.database import Base


class Category(Base):
    __tablename__ = 'categories'
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, index=True)
    creation_date = Column(Date)

    user_id = Column(BigInteger, ForeignKey('users.id'), index=True)
    user = relationship('User', lazy='subquery', back_populates='user_categories')
    expenses = relationship('Expense', lazy='subquery', back_populates='category')

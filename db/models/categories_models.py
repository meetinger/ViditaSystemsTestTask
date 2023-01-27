from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey('users.id'), index=True)

    user = relationship('User',lazy='subquery', back_populates='user_categories')
    expenses = relationship('Expense',lazy='subquery', back_populates='category')
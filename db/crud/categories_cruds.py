import datetime

from db.database import get_db
from db.models import User, Category


def get_category_by_name(category_name: str, user_db: User) -> Category | None:
    with get_db() as db:
        category_db = db.query(Category).filter_by(name=category_name, user_id=user_db.id).first()
        return category_db


def create_category(category_name: str, user_db: User) -> Category:
    category_db = Category(name=category_name, creation_date=datetime.datetime.now().date(), user_id=user_db.id)
    with get_db() as db:
        db.add(category_db)
        db.commit()
        db.refresh(category_db)
    return category_db


def get_users_categories(user_db: User) -> list[Category] | list:
    return user_db.user_categories

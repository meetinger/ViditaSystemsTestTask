from core.utils.misc import get_utc_datetime_now
from db.database import get_db
from db.models import User, Category


def get_category_by_name(category_name: str, user_db: User) -> Category | None:
    with get_db() as db:
        category_db = db.query(Category).filter_by(name=category_name, user_id=user_db.id).first()
        return category_db


def get_category_by_id(category_id: int, user_db: User) -> Category | None:
    with get_db() as db:
        category_db = db.query(Category).filter_by(id=category_id, user_id=user_db.id).first()
        return category_db


def delete_category_by_id(category_id: int, user_db: User):
    with get_db() as db:
        category_db = db.query(Category).filter_by(id=category_id, user_id=user_db.id).first()
        if category_db is not None:
            db.delete(category_db)
            db.commit()
            db.refresh(user_db)
            return True
        return False


def create_category(category_name: str, user_db: User) -> Category:
    category_db = Category(name=category_name, creation_date=get_utc_datetime_now().date(), user_id=user_db.id)
    with get_db() as db:
        db.add(category_db)
        db.commit()
        db.refresh(category_db)
    return category_db

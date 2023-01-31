import datetime


from core.utils.misc import get_utc_datetime_now
from db.database import get_db
from db.models import User, Category, Expense


def create_expense(expense_in: dict, category_db: Category, user_db: User,
                   creation_date: datetime.date = None) -> Expense:
    if creation_date is None:
        creation_date = get_utc_datetime_now().date()
    with get_db() as db:
        expense_db = Expense(name=expense_in['name'], amount=expense_in['amount'],
                             creation_date=creation_date, category_id=category_db.id, user_id=user_db.id)
        db.add(expense_db)
        db.commit()
        db.refresh(expense_db)
        return expense_db


def delete_expense_by_id(expense_id: int, user_db: User) -> bool:
    with get_db() as db:
        expense_db = db.query(Expense).filter_by(id=expense_id, user_id=user_db.id).first()
        if expense_db is not None:
            db.delete(expense_db)
            db.commit()
            return True
        return False


def get_all_user_expenses(user_db: User) -> list[Expense]:
    return user_db.user_expenses

def get_user_expenses_by_date(expense_date: datetime.date, user_db: User) -> list:
    return user_db.user_expenses.filter_by(creation_date=expense_date).all()


def get_all_category_expenses(category_db: Category, user_db: User) -> list:
    with get_db() as db:
        return db.query(Expense).filter_by(user_id=user_db.id, category_id=category_db.id).all()


def get_category_expenses_by_date(category_db: Category, creation_date: datetime.date, user_db: User) -> list:
    with get_db() as db:
        return db.query(Expense).filter_by(user_id=user_db.id, category_id=category_db.id,
                                           creation_date=creation_date).all()

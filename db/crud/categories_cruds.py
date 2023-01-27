from db.database import get_db
from db.models import User


def get_users_categories(user_db: User):
    with get_db() as db:
        db.query()
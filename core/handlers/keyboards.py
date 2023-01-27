from telegram import InlineKeyboardButton

from db.models import Category


async def build_categories_buttons(categories: list[Category]) -> str | list[InlineKeyboardButton]:
    if not categories:
        return 'У Вас ещё нет категорий расходов'
    return [InlineKeyboardButton(text=category.name, callback_data=str(category.user_id)) for category in categories]

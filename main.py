from core.handlers.handlers import HANDLERS

from core.settings import settings
from telegram.ext import Application


def main():
    application = Application.builder().token(settings.BOT_TOKEN).build()
    application.add_handlers(HANDLERS)
    application.run_polling()


if __name__ == '__main__':
    main()


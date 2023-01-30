from core.handlers.handlers import HANDLERS as COMMAND_HANDLERS

from core.handlers.handlers import start
from core.settings import settings
from telegram.ext import Application, CommandHandler


def main():
    application = Application.builder().token(settings.BOT_TOKEN).build()
    application.add_handlers(COMMAND_HANDLERS)
    application.run_polling()


if __name__ == '__main__':
    main()


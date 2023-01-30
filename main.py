import asyncio

from core.handlers.handlers import HANDLERS, COMMANDS

from core.settings import settings
from telegram.ext import Application


application = Application.builder().token(settings.BOT_TOKEN).build()

async def main():
    application.add_handlers(HANDLERS)
    await application.bot.set_my_commands(COMMANDS.items())
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    while True:
        await asyncio.sleep(1000)
    await application.updater.stop()
    await application.stop()
    await application.shutdown()


if __name__ == '__main__':
    asyncio.run(main())


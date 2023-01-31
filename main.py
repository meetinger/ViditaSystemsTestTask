import asyncio


from core.handlers.handlers import HANDLERS, COMMANDS
from core.handlers.notifications import notificator

from core.settings import settings
from telegram.ext import Application


application = Application.builder().token(settings.BOT_TOKEN).build()

async def run_bot(update_method='webhook'):
    application.add_handlers(HANDLERS)
    await application.bot.set_my_commands([(cmd, desc) for cmd, (desc, _) in COMMANDS.items()])
    await application.initialize()
    await application.start()
    if update_method == 'webhook':
        await application.updater.start_webhook(
            listen='0.0.0.0',
            port=settings.WEBHOOK_PORT,
            secret_token=settings.SECRET_TOKEN,
            key='private.key',
            cert='cert.pem',
            webhook_url=settings.WEBHOOK_URL
        )
    else:
        await application.updater.start_polling()
    await notificator.fetch_users_to_notifications(application)
    notificator.start_periodic_fetch_users(application)
    while True:
        await asyncio.sleep(1000)
    await application.updater.stop()
    await application.stop()
    await application.shutdown()


if __name__ == '__main__':
    asyncio.run(run_bot(update_method=settings.UPDATE_METHOD))


import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config import BOT_TOKEN, WEBHOOK_URL, PORT
from database import Database
from handlers import start, ai_services, premium, payment, referral, admin
from middleware.subscription_check import SubscriptionMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"


async def main():
    db = Database()
    await db.load()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Pass db through dispatcher workflow_data
    dp["db"] = db

    # Middleware
    dp.message.middleware(SubscriptionMiddleware(db))
    dp.callback_query.middleware(SubscriptionMiddleware(db))

    # Routers
    dp.include_router(start.router)
    dp.include_router(ai_services.router)
    dp.include_router(premium.router)
    dp.include_router(payment.router)
    dp.include_router(referral.router)
    dp.include_router(admin.router)

    if WEBHOOK_URL:
        # Webhook mode for Koyeb
        await bot.set_webhook(
            url=f"{WEBHOOK_URL}{WEBHOOK_PATH}",
            allowed_updates=["message", "callback_query", "pre_checkout_query", "successful_payment"]
        )
        logger.info(f"Webhook set: {WEBHOOK_URL}{WEBHOOK_PATH}")

        app = web.Application()
        handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
        await site.start()
        logger.info(f"Server running on port {PORT}")
        try:
            await asyncio.Event().wait()
        finally:
            await bot.delete_webhook()
            await runner.cleanup()
    else:
        # Polling mode for local dev
        logger.info("Starting polling mode...")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

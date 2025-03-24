from asyncio import run

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import config

import logging

from handlers import all_router, groups_router, direct_router, events_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode="markdown", link_preview_is_disabled=True))

dp = Dispatcher()


async def aiogram_on_startup_polling(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Starting polling...")


async def aiogram_on_shutdown_polling():
    logger.info("Stopping polling...")
    logger.info("Stopped polling")


async def main():

    dp.include_routers(all_router, groups_router, direct_router, events_router)

    dp.startup.register(aiogram_on_startup_polling)
    dp.shutdown.register(aiogram_on_shutdown_polling)

    await dp.start_polling(bot)


if __name__ == "__main__":
    run(main())

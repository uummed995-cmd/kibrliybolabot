import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import (
    admin_panel, group_manager, games, translator,
    bonus, fun, contact_admin, quiz_monitor, start
)
from utils.scheduler import start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Routers
    dp.include_router(start.router)
    dp.include_router(admin_panel.router)
    dp.include_router(group_manager.router)
    dp.include_router(games.router)
    dp.include_router(translator.router)
    dp.include_router(bonus.router)
    dp.include_router(fun.router)
    dp.include_router(contact_admin.router)
    dp.include_router(quiz_monitor.router)

    # Scheduler (quiz monitor, daily tasks)
    await start_scheduler(bot)

    logger.info("🤖 KibrliyBolaBot ishga tushdi!")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())

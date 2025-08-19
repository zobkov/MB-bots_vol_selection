import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from redis.asyncio import Redis

from config.config import load_config
from database.db import Database
from database.repositories import UserRepository
from bot.handlers import router
from bot.dialogs import start_dialog, menu_dialog, application_dialog, department_selection_dialog

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    # Загружаем конфигурацию
    config = load_config()
    
    # Создаем Redis хранилище для FSM
    redis = Redis(
        host=config.redis.host,
        port=config.redis.port,
        password=config.redis.password if config.redis.password else None,
        decode_responses=True
    )
    storage = RedisStorage(redis=redis)
    
    # Создаем бота и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)
    
    # Создаем подключение к базе данных
    db = Database(config)
    
    # Создаем таблицы
    await db.create_tables()
    
    # Регистрируем middleware для передачи конфигурации и БД
    @dp.middleware()
    async def config_middleware(handler, event, data):
        data["config"] = config
        data["db"] = db
        return await handler(event, data)
    
    # Регистрируем роутеры и диалоги
    dp.include_router(router)
    dp.include_router(start_dialog)
    dp.include_router(menu_dialog)
    dp.include_router(application_dialog)
    dp.include_router(department_selection_dialog)
    
    # Настраиваем диалоги
    setup_dialogs(dp)
    
    try:
        logger.info("Бот запускается...")
        await dp.start_polling(bot)
    finally:
        # Закрываем соединения
        await db.close()
        await redis.close()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())

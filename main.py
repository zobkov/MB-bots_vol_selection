import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
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
    if config.redis.password:
        redis_client = Redis.from_url(f"redis://:{config.redis.password}@{config.redis.host}:{config.redis.port}/0")
    else:
        redis_client = Redis.from_url(f"redis://{config.redis.host}:{config.redis.port}/0")
    storage = RedisStorage(
        redis=redis_client,
        key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        state_ttl=86400,  # время жизни состояния в секунду (например, 1 день)
        data_ttl=86400   # время жизни данных
    )

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
    
    # Создаем middleware для передачи конфигурации и БД
    async def config_middleware(handler, event, data):
        data["config"] = config
        data["db"] = db
        return await handler(event, data)
    
    # Регистрируем middleware
    dp.message.middleware(config_middleware)
    dp.callback_query.middleware(config_middleware)
    
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
        await redis_client.aclose()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())

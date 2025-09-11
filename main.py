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
from bot.middlewares import LoggingMiddleware
from bot.keyboards.command_menu import set_main_menu
from utils.logging_config import setup_logging, log_error, log_user_action
from utils.google_services import setup_google_sheets_service


async def main():
    try:
        # Загружаем конфигурацию
        config = load_config()
        
        # Настройка логирования с уровнем из конфигурации
        logger = setup_logging(config.log_level)
        logger.info("🚀 Запуск бота...")
        logger.info("⚙️ Конфигурация загружена")
        
        # Создаем Redis хранилище для FSM
        if config.redis.password:
            redis_client = Redis.from_url(f"redis://:{config.redis.password}@{config.redis.host}:{config.redis.port}/0")
        else:
            redis_client = Redis.from_url(f"redis://{config.redis.host}:{config.redis.port}/0")
            
        # Проверка подключения к Redis
        await redis_client.ping()
        logger.info(f"🔗 Подключение к Redis установлено: {config.redis.host}:{config.redis.port}")
        
        storage = RedisStorage(
            redis=redis_client,
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
            state_ttl=86400*2,  # время жизни состояния в секунду (например, 1 день)
            data_ttl=86400*2   # время жизни данных
        )

        # Создаем бота и диспетчер
        bot = Bot(
            token=config.tg_bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher(storage=storage)
        
        # Проверка подключения к боту
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот подключен: @{bot_info.username} ({bot_info.first_name})")
        
        # Создаем подключение к базе данных
        db = Database(config)
        
        # Настраиваем меню команд
        await set_main_menu(bot)

        # Создаем таблицы
        await db.create_tables()
        logger.info("🗄️ База данных инициализирована")
        
        # Настраиваем Google Sheets сервис
        google_sheets_service = setup_google_sheets_service(config)
        if google_sheets_service:
            logger.info("📊 Google Sheets сервис настроен")
        else:
            logger.warning("⚠️ Google Sheets сервис не настроен")
        
        # Создаем middleware для передачи конфигурации, БД и Google Sheets
        async def config_middleware(handler, event, data):
            data["config"] = config
            data["db"] = db
            data["google_sheets_service"] = google_sheets_service
            return await handler(event, data)
        
        # Регистрируем middleware
        dp.message.middleware(LoggingMiddleware())
        dp.callback_query.middleware(LoggingMiddleware())
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
        
        # Регистрация обработчика ошибок
        from bot.dialogs.dialog_error_handler import dialog_error_handler
        dp.errors.register(dialog_error_handler)
        
        logger.info("🔧 Роутеры и диалоги настроены")

        logger.info("✅ Бот готов к работе")
        await dp.start_polling(bot)
        
    except Exception as e:
        log_error(e, "Критическая ошибка при запуске бота")
        raise 
    finally:
        try:
            # Закрываем соединения
            await db.close()
            await redis_client.aclose()
            await bot.session.close()
            logger.info("🛑 Бот остановлен")
        except Exception as e:
            log_error(e, "Ошибка при остановке бота")


if __name__ == '__main__':
    asyncio.run(main())

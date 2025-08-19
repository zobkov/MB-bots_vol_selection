"""
Простой HTTP сервер для healthcheck бота
"""
import asyncio
import logging
from aiohttp import web, ClientSession
from aiogram import Bot
import os


async def health_check(request):
    """Проверка здоровья бота"""
    try:
        # Проверяем токен бота
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            return web.json_response(
                {'status': 'error', 'message': 'BOT_TOKEN not found'}, 
                status=500
            )
        
        # Проверяем подключение к Telegram API
        bot = Bot(token=bot_token)
        try:
            bot_info = await bot.get_me()
            await bot.session.close()
            
            return web.json_response({
                'status': 'healthy',
                'bot_username': bot_info.username,
                'bot_name': bot_info.first_name
            })
        except Exception as e:
            await bot.session.close()
            return web.json_response(
                {'status': 'error', 'message': f'Telegram API error: {str(e)}'}, 
                status=500
            )
            
    except Exception as e:
        return web.json_response(
            {'status': 'error', 'message': str(e)}, 
            status=500
        )


async def create_app():
    """Создание приложения"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)  # Для простоты
    return app


def run_healthcheck_server():
    """Запуск сервера healthcheck"""
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    run_healthcheck_server()

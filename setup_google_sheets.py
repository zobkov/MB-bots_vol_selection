#!/usr/bin/env python3
"""
Скрипт для настройки Google Sheets с правильными заголовками и тестовыми данными
"""

import asyncio
import logging
from datetime import datetime
from utils.google_services import setup_google_sheets_service
from config.config import load_config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def setup_sheets():
    """Настройка Google Sheets с правильными заголовками и тестовыми данными"""
    try:
        # Загружаем конфигурацию
        config = load_config()
        
        if not config.google:
            logger.error("❌ Google конфигурация не найдена")
            return
        
        # Создаем Google Sheets сервис
        google_sheets_service = setup_google_sheets_service(config)
        
        if not google_sheets_service:
            logger.error("❌ Не удалось инициализировать Google Sheets сервис")
            return
        
        logger.info("✅ Google Sheets сервис инициализирован")
        
        # Открываем таблицу
        spreadsheet = google_sheets_service.gc.open_by_key(google_sheets_service.spreadsheet_id)
        logger.info(f"📋 Открыта таблица: {google_sheets_service.spreadsheet_id}")
        
        # Получаем или создаем лист Applications
        worksheet_name = "Applications"
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            logger.info(f"✅ Лист {worksheet_name} найден")
            
            # Очищаем существующий лист
            logger.info("🧹 Очищаем существующий лист...")
            worksheet.clear()
            
        except Exception:
            logger.info(f"📄 Лист {worksheet_name} не найден, создаем новый...")
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
        
        # Заголовки согласно нашей системе
        headers = [
            'Timestamp',           # A
            'User ID',             # B
            'Username',            # C
            'Full Name',           # D
            'First Name',          # E
            'Last Name',           # F
            'Middle Name',         # G
            'Course',              # H
            'Dormitory',           # I
            'Email',               # J
            'Phone',               # K
            'Personal Qualities',  # L
            'Motivation',          # M
            'Logistics Rating',    # N
            'Marketing Rating',    # O
            'PR Rating',           # P
            'Program Rating',      # Q
            'Partners Rating',     # R
            'Created At',          # S
            'Updated At'           # T
        ]
        
        logger.info("📋 Добавляем заголовки...")
        worksheet.append_row(headers)
        
        # Добавляем тестовые данные
        test_data = [
            [
                datetime.now().isoformat(),                    # Timestamp
                '123456789',                                   # User ID
                'test_user',                                   # Username
                'Иванов Иван Иванович',                       # Full Name
                'Иван',                                        # First Name
                'Иванов',                                      # Last Name
                'Иванович',                                    # Middle Name
                '3_bachelor',                                  # Course
                'Да',                                          # Dormitory
                'test@student.spbu.ru',                       # Email
                '+7-999-123-45-67',                           # Phone
                'Ответственный, коммуникабельный, креативный', # Personal Qualities
                'Хочу попробовать себя в волонтерской деятельности', # Motivation
                '5',                                           # Logistics Rating
                '4',                                           # Marketing Rating
                '3',                                           # PR Rating
                '5',                                           # Program Rating
                '2',                                           # Partners Rating
                datetime.now().isoformat(),                    # Created At
                datetime.now().isoformat(),                    # Updated At
            ]
        ]
        
        logger.info("📝 Добавляем тестовые данные...")
        for i, row in enumerate(test_data, 1):
            worksheet.append_row(row)
            logger.info(f"✅ Добавлена тестовая запись {i}")
        
        # Форматируем заголовки (делаем их жирными)
        logger.info("🎨 Форматируем заголовки...")
        try:
            worksheet.format('A1:T1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            logger.info("✅ Заголовки отформатированы")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось отформатировать заголовки: {e}")
        
        # Автоматически подгоняем ширину колонок
        logger.info("📏 Настраиваем ширину колонок...")
        try:
            # Устанавливаем ширину колонок
            requests = [
                {
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': worksheet.id,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,  # A
                            'endIndex': 20    # T
                        },
                        'properties': {
                            'pixelSize': 150
                        },
                        'fields': 'pixelSize'
                    }
                }
            ]
            
            spreadsheet.batch_update({'requests': requests})
            logger.info("✅ Ширина колонок настроена")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось настроить ширину колонок: {e}")
        
        logger.info("🎉 Google Sheets успешно настроен!")
        logger.info(f"🔗 Ссылка на таблицу: https://docs.google.com/spreadsheets/d/{config.google.spreadsheet_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка настройки Google Sheets: {e}")
        return False


async def test_application_export():
    """Тест экспорта заявки в Google Sheets"""
    try:
        config = load_config()
        
        google_sheets_service = setup_google_sheets_service(config)
        
        if not google_sheets_service:
            logger.error("❌ Не удалось инициализировать Google Sheets сервис")
            return False
        
        # Тестовые данные заявки
        test_application = {
            'telegram_id': '555666777',
            'telegram_username': 'test_user_priority',
            'full_name': 'Тестов Приоритет Системович',
            'first_name': 'Приоритет',
            'last_name': 'Тестов',
            'middle_name': 'Системович',
            'course': '4_bachelor',
            'dormitory': True,
            'email': 'priority.test@student.spbu.ru',
            'phone': '+7-555-666-77-88',
            'personal_qualities': 'Ответственный, организованный, умею работать в команде',
            'motivation': 'Хочу попробовать себя в роли волонтера и получить новый опыт',
            'logistics_rating': 5,
            'marketing_rating': 4,
            'pr_rating': 3,
            'program_rating': 5,
            'partners_rating': 2,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        logger.info("🧪 Тестируем экспорт заявки...")
        success = await google_sheets_service.add_application_to_sheet(test_application)
        
        if success:
            logger.info("✅ Тест экспорта прошел успешно!")
        else:
            logger.error("❌ Тест экспорта не удался!")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Ошибка теста экспорта: {e}")
        return False


async def main():
    """Главная функция"""
    logger.info("🚀 Запуск настройки Google Sheets...")
    
    # Настраиваем Google Sheets
    setup_success = await setup_sheets()
    
    if setup_success:
        logger.info("✅ Настройка Google Sheets завершена")
        
        # Тестируем экспорт
        logger.info("🧪 Запуск теста экспорта...")
        test_success = await test_application_export()
        
        if test_success:
            logger.info("🎉 Все тесты прошли успешно!")
        else:
            logger.error("❌ Тесты не прошли")
    else:
        logger.error("❌ Настройка Google Sheets не удалась")


if __name__ == "__main__":
    asyncio.run(main())

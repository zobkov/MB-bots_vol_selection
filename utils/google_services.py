import os
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Класс для работы с Google Sheets"""
    
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        """
        Инициализация сервиса Google Sheets
        
        Args:
            credentials_path: Путь к файлу с учетными данными сервисного аккаунта
            spreadsheet_id: ID Google Таблицы
        """
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        
        # Области доступа
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
        ]
        
        self._setup_service()
    
    def _setup_service(self):
        """Настройка сервиса Google Sheets"""
        try:
            # Создаем учетные данные
            credentials = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=self.scopes
            )
            
            # Настраиваем gspread для работы с Google Sheets
            self.gc = gspread.authorize(credentials)
            logger.info("✅ Google Sheets API настроен")
            
        except Exception as e:
            logger.error(f"Ошибка настройки Google Sheets: {e}")
            raise
    
    async def add_application_to_sheet(self, application_data: Dict[str, Any]) -> bool:
        """
        Добавляет данные заявки в Google Таблицу
        
        Args:
            application_data: Словарь с данными заявки
            
        Returns:
            bool: True если успешно, False в случае ошибки
        """
        try:
            logger.info(f"📊 Начинаем добавление заявки в Google Sheets...")
            logger.info(f"👤 Пользователь: {application_data.get('telegram_id')} (@{application_data.get('telegram_username')})")
            
            # Открываем таблицу по ID
            logger.info(f"📋 Открываем таблицу: {self.spreadsheet_id}")
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            
            # Получаем лист "Applications" или создаем его
            worksheet_name = "Applications"
            try:
                logger.info(f"🔍 Ищем лист: {worksheet_name}")
                worksheet = spreadsheet.worksheet(worksheet_name)
                logger.info(f"✅ Лист {worksheet_name} найден")
            except gspread.WorksheetNotFound:
                logger.info(f"📄 Лист {worksheet_name} не найден, создаем новый...")
                # Создаем лист если его нет
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
                
                # Добавляем заголовки
                headers = [
                    'Timestamp', 'User ID', 'Username', 'Full Name', 'First Name', 'Last Name', 'Middle Name',
                    'Course', 'Dormitory', 'Email', 'Phone', 'Personal Qualities', 'Motivation',
                    'Logistics Rating', 'Marketing Rating', 'PR Rating', 'Program Rating', 'Partners Rating',
                    'Created At', 'Updated At'
                ]
                worksheet.append_row(headers)
                logger.info(f"✅ Лист {worksheet_name} создан с заголовками")
            
            # Проверяем, есть ли уже запись для этого пользователя
            try:
                # Получаем все записи
                all_records = worksheet.get_all_records()
                user_id = str(application_data.get('telegram_id'))
                
                # Ищем существующую запись
                existing_row = None
                for i, record in enumerate(all_records, start=2):  # start=2 because row 1 is headers
                    if str(record.get('User ID')) == user_id:
                        existing_row = i
                        break
                
                if existing_row:
                    logger.info(f"🔄 Обновляем существующую запись в строке {existing_row}")
                    update_method = "update"
                else:
                    logger.info(f"➕ Добавляем новую запись")
                    update_method = "insert"
                    
            except Exception as e:
                logger.warning(f"⚠️ Не удалось проверить существующие записи: {e}")
                update_method = "insert"
            
            # Подготавливаем данные для записи
            logger.info(f"📝 Подготавливаем данные для записи...")
            row_data = [
                datetime.now().isoformat(),  # Timestamp
                application_data.get('telegram_id', ''),  # User ID
                application_data.get('telegram_username', ''),  # Username
                application_data.get('full_name', ''),  # Full Name
                application_data.get('first_name', ''),  # First Name
                application_data.get('last_name', ''),  # Last Name
                application_data.get('middle_name', ''),  # Middle Name
                application_data.get('course', ''),  # Course
                "Да" if application_data.get('dormitory') else "Нет",  # Dormitory
                application_data.get('email', ''),  # Email
                application_data.get('phone', ''),  # Phone
                application_data.get('personal_qualities', ''),  # Personal Qualities
                application_data.get('motivation', ''),  # Motivation
                application_data.get('logistics_rating', ''),  # Logistics Rating
                application_data.get('marketing_rating', ''),  # Marketing Rating
                application_data.get('pr_rating', ''),  # PR Rating
                application_data.get('program_rating', ''),  # Program Rating
                application_data.get('partners_rating', ''),  # Partners Rating
                application_data.get('created_at', ''),  # Created At
                application_data.get('updated_at', ''),  # Updated At
            ]
            
            logger.info(f"📤 Отправляем данные в Google Sheets...")
            
            if update_method == "update" and existing_row:
                # Обновляем существующую строку
                worksheet.update(f'A{existing_row}:T{existing_row}', [row_data])
                logger.info(f"🔄 Заявка пользователя {application_data.get('telegram_id')} обновлена в Google Sheets")
            else:
                # Добавляем новую строку
                worksheet.append_row(row_data)
                logger.info(f"➕ Заявка пользователя {application_data.get('telegram_id')} добавлена в Google Sheets")
            
            logger.info(f"🎉 Заявка пользователя {application_data.get('telegram_id')} успешно сохранена в Google Sheets")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Ошибка добавления заявки в Google Sheets: {e}")
            
            # Детальная диагностика ошибок Google Sheets
            if "quotaExceeded" in error_msg:
                logger.error("📊 ОШИБКА: Превышены лимиты Google Sheets API")
                logger.error("💡 РЕШЕНИЕ: Подождите и повторите попытку позже")
            elif "403" in error_msg:
                if "Forbidden" in error_msg:
                    logger.error("🚫 ОШИБКА: Нет доступа к Google Sheets (403 Forbidden)")
                    logger.error("💡 РЕШЕНИЕ: Проверьте права доступа Service Account к таблице")
                else:
                    logger.error("🚫 ОШИБКА 403: Доступ запрещен")
            elif "401" in error_msg:
                logger.error("🔐 ОШИБКА: Ошибка авторизации Google Sheets (401)")
                logger.error("💡 РЕШЕНИЕ: Проверьте учетные данные Service Account")
            elif "404" in error_msg:
                logger.error("📋 ОШИБКА: Таблица Google Sheets не найдена (404)")
                logger.error(f"💡 РЕШЕНИЕ: Проверьте ID таблицы: {self.spreadsheet_id}")
            elif "500" in error_msg:
                logger.error("🔧 ОШИБКА: Внутренняя ошибка сервера Google (500)")
                logger.error("💡 РЕШЕНИЕ: Повторите попытку позже")
            elif "PERMISSION_DENIED" in error_msg:
                logger.error("🔒 ОШИБКА: Нет прав доступа к таблице")
                logger.error("💡 РЕШЕНИЕ: Предоставьте Service Account доступ к таблице")
            else:
                logger.error(f"❓ НЕИЗВЕСТНАЯ ОШИБКА Google Sheets: {error_msg}")
                
            return False


def setup_google_sheets_service(config) -> Optional[GoogleSheetsService]:
    """
    Настройка Google Sheets сервиса
    
    Args:
        config: Конфигурация приложения
        
    Returns:
        GoogleSheetsService или None в случае ошибки
    """
    try:
        if not config.google:
            logger.warning("Google Sheets не настроен в конфигурации")
            return None
        
        # Проверяем существование файла учетных данных
        if not os.path.exists(config.google.credentials_path):
            logger.warning(f"Файл учетных данных Google не найден: {config.google.credentials_path}")
            return None
        
        return GoogleSheetsService(
            credentials_path=config.google.credentials_path,
            spreadsheet_id=config.google.spreadsheet_id
        )
        
    except Exception as e:
        logger.error(f"Ошибка настройки Google Sheets сервиса: {e}")
        return None

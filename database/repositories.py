from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Application
from typing import Optional
from utils.logging_config import log_db_operation, log_error
import re


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user(self, telegram_id: int, telegram_username: Optional[str] = None) -> User:
        """Получить или создать пользователя"""
        try:
            # Попытаемся найти существующего пользователя
            result = await self.session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user is None:
                # Создаем нового пользователя
                user = User(
                    telegram_id=telegram_id,
                    telegram_username=telegram_username
                )
                self.session.add(user)
                await self.session.commit()
                await self.session.refresh(user)
                log_db_operation("CREATE", "users", f"new user created", telegram_id)
            else:
                # Обновляем username если изменился
                if user.telegram_username != telegram_username:
                    user.telegram_username = telegram_username
                    await self.session.commit()
                    log_db_operation("UPDATE", "users", f"username updated to {telegram_username}", telegram_id)
                log_db_operation("SELECT", "users", f"existing user found", telegram_id)
            
            return user
        except Exception as e:
            log_error(e, "Ошибка при получении/создании пользователя", telegram_id)
            raise

    async def update_stage1_status(self, telegram_id: int, status: str):
        """Обновить статус первого этапа"""
        try:
            await self.session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(stage1_submitted=status)
            )
            await self.session.commit()
            log_db_operation("UPDATE", "users", f"stage1_status updated to {status}", telegram_id)
        except Exception as e:
            log_error(e, "Ошибка при обновлении статуса этапа 1", telegram_id)
            raise

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по telegram_id"""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


class ApplicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def parse_full_name(full_name: str) -> tuple[str, str, Optional[str]]:
        """Разделение ФИО на составные части"""
        parts = full_name.strip().split()
        
        if len(parts) >= 2:
            last_name = parts[0]
            first_name = parts[1]
            middle_name = parts[2] if len(parts) >= 3 else None
            return first_name, last_name, middle_name
        elif len(parts) == 1:
            # Если только одно слово, считаем его именем
            return parts[0], "", None
        else:
            return "", "", None

    async def create_application(self, user_id: int, application_data: dict) -> Application:
        """Создать заявку"""
        try:
            # Разбираем ФИО
            first_name, last_name, middle_name = self.parse_full_name(application_data['full_name'])
            
            application = Application(
                user_id=user_id,
                full_name=application_data['full_name'],
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                course=application_data['course'],
                dormitory=application_data['dormitory'],
                email=application_data['email'],
                phone=application_data['phone'],
                personal_qualities=application_data['personal_qualities'],
                motivation=application_data['motivation'],
                logistics_rating=application_data['logistics_rating'],
                marketing_rating=application_data['marketing_rating'],
                pr_rating=application_data['pr_rating'],
                program_rating=application_data['program_rating'],
                partners_rating=application_data['partners_rating'],
            )
            
            self.session.add(application)
            await self.session.commit()
            await self.session.refresh(application)
            
            # Получаем telegram_id пользователя для логирования
            user_result = await self.session.execute(
                select(User.telegram_id).where(User.id == user_id)
            )
            telegram_id = user_result.scalar_one_or_none()
            
            log_db_operation("CREATE", "applications", 
                           f"application created: {application_data['full_name']}, {application_data['email']}", 
                           telegram_id)
            return application
        except Exception as e:
            log_error(e, "Ошибка при создании заявки")
            raise

    async def get_user_applications(self, user_id: int) -> list[Application]:
        """Получить все заявки пользователя"""
        result = await self.session.execute(
            select(Application).where(Application.user_id == user_id)
        )
        return list(result.scalars().all())

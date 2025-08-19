from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Application
from typing import Optional
import re


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user(self, telegram_id: int, telegram_username: Optional[str] = None) -> User:
        """Получить или создать пользователя"""
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
        else:
            # Обновляем username если изменился
            if user.telegram_username != telegram_username:
                user.telegram_username = telegram_username
                await self.session.commit()
        
        return user

    async def update_stage1_status(self, telegram_id: int, status: str):
        """Обновить статус первого этапа"""
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(stage1_submitted=status)
        )
        await self.session.commit()

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
        return application

    async def get_user_applications(self, user_id: int) -> list[Application]:
        """Получить все заявки пользователя"""
        result = await self.session.execute(
            select(Application).where(Application.user_id == user_id)
        )
        return list(result.scalars().all())

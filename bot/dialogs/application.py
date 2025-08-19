from aiogram import types
from aiogram.types import CallbackQuery, ContentType
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Start, Group, Select, Back, Next, SwitchTo, Cancel
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, MessageInput

from bot.states import DepartmentSelectionSG, ApplicationSG, MenuSG
from database.repositories import UserRepository, ApplicationRepository
from database.db import Database
import re


# Валидация email
async def email_check(message: types.Message, widget, dialog_manager: DialogManager, text: str):
    if not text.endswith("@spbu.ru"):
        await message.answer("❌ Email должен заканчиваться на @spbu.ru")
        return False
    return True


# Обработка ввода ФИО
async def on_full_name_input(message: types.Message, widget, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["full_name"] = text
    await dialog_manager.next()


# Обработка ввода email
async def on_email_input(message: types.Message, widget, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["email"] = text
    await dialog_manager.next()


# Обработка ввода личных качеств
async def on_qualities_input(message: types.Message, widget, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["personal_qualities"] = text
    await dialog_manager.next()


# Обработка ввода мотивации
async def on_motivation_input(message: types.Message, widget, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["motivation"] = text
    await dialog_manager.next()


# Обработка контакта
async def on_contact_received(message: types.Message, widget, dialog_manager: DialogManager):
    if message.contact:
        dialog_manager.dialog_data["phone"] = message.contact.phone_number
        await dialog_manager.next()
    else:
        await message.answer("❌ Пожалуйста, поделитесь контактом через кнопку")


# Обработка выбора курса
async def on_course_selected(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    course_data = {
        "1_bachelor": "1 курс бакалавриат",
        "2_bachelor": "2 курс бакалавриат", 
        "3_bachelor": "3 курс бакалавриат",
        "4_bachelor": "4 курс бакалавриат",
        "1_master": "1 курс магистратура",
        "2_master": "2 курс магистратура"
    }
    
    course_key = callback.data.split(":")[1]
    dialog_manager.dialog_data["course"] = course_key
    dialog_manager.dialog_data["course_display"] = course_data[course_key]
    await dialog_manager.next()


# Обработка выбора общежития
async def on_dormitory_selected(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dormitory = callback.data.split(":")[1] == "yes"
    dialog_manager.dialog_data["dormitory"] = dormitory
    await dialog_manager.next()


# Обработка завершения заполнения анкеты
async def on_submit_application(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # Получаем данные
    data = dialog_manager.dialog_data
    user = dialog_manager.event.from_user
    db: Database = dialog_manager.middleware_data.get("db")
    
    # Сохраняем в БД
    async with db.get_session() as session:
        user_repo = UserRepository(session)
        app_repo = ApplicationRepository(session)
        
        # Получаем или создаем пользователя
        db_user = await user_repo.get_or_create_user(
            telegram_id=user.id,
            telegram_username=user.username
        )
        
        # Создаем заявку
        application_data = {
            "full_name": data["full_name"],
            "course": data["course"],
            "dormitory": data["dormitory"],
            "email": data["email"],
            "phone": data["phone"],
            "personal_qualities": data["personal_qualities"],
            "motivation": data["motivation"],
            "logistics_rating": data["logistics_rating"],
            "marketing_rating": data["marketing_rating"],
            "pr_rating": data["pr_rating"],
            "program_rating": data["program_rating"],
            "partners_rating": data["partners_rating"],
        }
        
        await app_repo.create_application(db_user.id, application_data)
        
        # Обновляем статус пользователя
        await user_repo.update_stage1_status(user.id, "submitted")
    
    await callback.message.answer(
        "✅ Спасибо, что рассказал(а) о себе! "
        "Будем счастливы познакомиться вживую! "
        "Организаторы МБ'25 🤍"
    )
    await dialog_manager.start(MenuSG.main)


# Обработка возврата из диалога выбора отделов
async def on_departments_result(start_data, result, dialog_manager: DialogManager):
    """Обработка результата диалога выбора отделов"""
    if result:
        # Копируем данные об оценках отделов
        for key, value in result.items():
            dialog_manager.dialog_data[key] = value
    
    # Переходим к следующему шагу - мотивации
    await dialog_manager.switch_to(ApplicationSG.motivation)


# Геттеры данных
async def get_overview_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    
    dormitory_text = "Да" if data.get("dormitory") else "Нет"
    
    overview_text = f"""📋 Проверьте введенные данные:

👤 ФИО: {data.get('full_name', 'Не указано')}
🎓 Курс: {data.get('course_display', 'Не указан')}
🏠 Общежитие: {dormitory_text}
📧 Email: {data.get('email', 'Не указан')}
📱 Телефон: {data.get('phone', 'Не указан')}

🌸 Личные качества:
{data.get('personal_qualities', 'Не указано')}

🌟 Мотивация:
{data.get('motivation', 'Не указано')}

📊 Оценки отделов:
• Логистика: {data.get('logistics_rating', 'Не указано')}
• Маркетинг: {data.get('marketing_rating', 'Не указано')}
• PR: {data.get('pr_rating', 'Не указано')}
• Программа: {data.get('program_rating', 'Не указано')}
• Партнеры: {data.get('partners_rating', 'Не указано')}"""

    return {"overview_text": overview_text}


application_dialog = Dialog(
    # Окно 1: ФИО
    Window(
        Const("👤 Введите ваше полное ФИО:"),
        TextInput(
            id="full_name_input",
            on_success=on_full_name_input,
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.full_name,
    ),
    
    # Окно 2: Курс обучения
    Window(
        Const("🎓 Укажите курс обучения:"),
        Group(
            Button(Const("1 курс бакалавриат"), id="1_bachelor", on_click=on_course_selected),
            Button(Const("2 курс бакалавриат"), id="2_bachelor", on_click=on_course_selected),
            Button(Const("3 курс бакалавриат"), id="3_bachelor", on_click=on_course_selected),
            Button(Const("4 курс бакалавриат"), id="4_bachelor", on_click=on_course_selected),
            Button(Const("1 курс магистратура"), id="1_master", on_click=on_course_selected),
            Button(Const("2 курс магистратура"), id="2_master", on_click=on_course_selected),
            width=2,
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.course,
    ),
    
    # Окно 3: Общежитие
    Window(
        Const("🏠 Живешь ли ты в общежитии в Михайловской даче?"),
        Group(
            Button(Const("Да"), id="yes", on_click=on_dormitory_selected),
            Button(Const("Нет"), id="no", on_click=on_dormitory_selected),
            width=2,
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.dormitory,
    ),
    
    # Окно 4: Email
    Window(
        Const("📧 Укажи свою корпоративную почту (должна заканчиваться на @spbu.ru):"),
        TextInput(
            id="email_input",
            on_success=on_email_input,
            type_factory=email_check,
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.email,
    ),
    
    # Окно 5: Телефон
    Window(
        Const("📱 Поделись своим контактным номером телефона:"),
        MessageInput(
            func=on_contact_received,
            content_types=[ContentType.CONTACT],
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.phone,
    ),
    
    # Окно 6: Личные качества
    Window(
        Const("🌸 Расскажи развёрнуто о своих личностных качествах и умениях, "
              "которые пригодились бы в волонтёрской работе:"),
        TextInput(
            id="qualities_input",
            on_success=on_qualities_input,
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.personal_qualities,
    ),
    
    # Окно 7: Переход к выбору отделов
    Window(
        Const("📊 Теперь оцени свой интерес к каждому отделу от 1 до 5, "
              "где 1 - наименее интересный, 5 - очень хотелось бы попасть в этот отдел."),
        Start(
            Const("📋 Оценить отделы"),
            id="departments",
            state=DepartmentSelectionSG.logistics
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.departments,
    ),
    
    # Окно 8: Мотивация
    Window(
        Const("🌟 Объясни подробно, почему тебе бы хотелось попробовать себя в роли волонтёра МБ:"),
        TextInput(
            id="motivation_input",
            on_success=on_motivation_input,
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.motivation,
    ),
    
    # Окно 9: Обзор ответов
    Window(
        Format("{overview_text}"),
        Group(
            Button(Const("✅ Подтвердить и отправить"), id="submit", on_click=on_submit_application),
            Button(Const("✏️ Изменить"), id="edit", on_click=lambda c, b, m: m.switch_to(ApplicationSG.full_name)),
            width=1,
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.overview,
        getter=get_overview_data,
    ),
    
    on_process_result=on_departments_result,
)

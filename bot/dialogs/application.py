from aiogram import types
from aiogram.types import CallbackQuery, ContentType
from aiogram_dialog import Dialog, DialogManager, Window, StartMode 
from aiogram_dialog.widgets.kbd import Button, Start, Group, Select, Back, Next, SwitchTo, Cancel, Radio, Column
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, MessageInput

from bot.states import DepartmentSelectionSG, ApplicationSG, MenuSG
from database.repositories import UserRepository, ApplicationRepository
from database.db import Database
import re


# Валидация email
def email_check(text: str) -> str:
    if not (text.endswith("@spbu.ru") or text.endswith("@student.spbu.ru") or text.endswith("@gsom.spbu.ru")):
        raise ValueError("❌ Email должен заканчиваться на @spbu.ru, @student.spbu.ru или @gsom.spbu.ru")
    return text


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
    
    # Отправляем сообщение и сразу переходим к выбору отделов
    await message.answer(
        "📊 Теперь оцени свой интерес к каждому отделу от 1 до 5, "
        "где 1 - наименее интересный, 5 - очень хотелось бы попасть в этот отдел."
    )
    await dialog_manager.start(DepartmentSelectionSG.logistics)


# Обработка ввода мотивации
async def on_motivation_input(message: types.Message, widget, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["motivation"] = text
    await dialog_manager.next()


# Валидация телефона
def phone_check(text: str) -> str:
    # Простая проверка что это похоже на номер телефона
    phone_digits = re.sub(r'[^\d]', '', text)
    if len(phone_digits) < 10:
        raise ValueError("❌ Введите корректный номер телефона")
    return text


# Обработка ввода телефона
async def on_phone_input(message: types.Message, widget, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["phone"] = text
    await dialog_manager.next()


# Обработка контакта
async def on_contact_received(message: types.Message, widget, dialog_manager: DialogManager):
    if message.contact:
        dialog_manager.dialog_data["phone"] = message.contact.phone_number
        await dialog_manager.next()
    else:
        await message.answer("❌ Пожалуйста, поделитесь контактом через кнопку или введите номер текстом")


# Обработка выбора курса
async def on_course_selected(callback: CallbackQuery, radio, dialog_manager: DialogManager, item_id: str):
    course_data = {
        "1_bachelor": "1 курс бакалавриат",
        "2_bachelor": "2 курс бакалавриат", 
        "3_bachelor": "3 курс бакалавриат",
        "4_bachelor": "4 курс бакалавриат",
        "1_master": "1 курс магистратура",
        "2_master": "2 курс магистратура"
    }
    
    dialog_manager.dialog_data["course"] = item_id
    dialog_manager.dialog_data["course_display"] = course_data[item_id]
    await dialog_manager.next()


# Обработка выбора общежития
async def on_dormitory_selected(callback: CallbackQuery, radio, dialog_manager: DialogManager, item_id: str):
    dormitory = item_id == "yes"
    dialog_manager.dialog_data["dormitory"] = dormitory
    await dialog_manager.next()


# Обработка завершения заполнения анкеты
async def on_submit_application(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # Получаем данные
    data = dialog_manager.dialog_data
    user = dialog_manager.event.from_user
    db: Database = dialog_manager.middleware_data.get("db")
    
    # Сохраняем в БД
    session = await db.get_session()
    try:
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
    finally:
        await session.close()
    
    await callback.message.answer(
        "✅ Спасибо, что рассказал(а) о себе! "
        "Будем счастливы познакомиться вживую! "
        "Организаторы МБ'25 🤍"
    )
    await dialog_manager.start(MenuSG.main, StartMode = StartMode.RESET_STACK)


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
async def get_dormitory_options(dialog_manager: DialogManager, **kwargs):
    """Геттер данных для выбора общежития"""
    options = [
        {"id": "yes", "text": "Да"},
        {"id": "no", "text": "Нет"},
    ]
    
    return {"dormitory_options": options}


async def get_course_options(dialog_manager: DialogManager, **kwargs):
    """Геттер данных для выбора курса"""
    courses = [
        {"id": "1_bachelor", "text": "1 курс бакалавриат"},
        {"id": "2_bachelor", "text": "2 курс бакалавриат"},
        {"id": "3_bachelor", "text": "3 курс бакалавриат"},
        {"id": "4_bachelor", "text": "4 курс бакалавриат"},
        {"id": "1_master", "text": "1 курс магистратура"},
        {"id": "2_master", "text": "2 курс магистратура"},
    ]
    
    return {"courses": courses}


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
        Column(
            Radio(
                Format("🔘 {item[text]}"),
                Format("⚪ {item[text]}"),
                id="course_radio",
                item_id_getter=lambda item: item["id"],
                items="courses",
                on_click=on_course_selected
            ),
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.course,
        getter=get_course_options,
    ),
    
    # Окно 3: Общежитие
    Window(
        Const("🏠 Живешь ли ты в общежитии в Михайловской даче?"),
        Column(
            Radio(
                Format("🔘 {item[text]}"),
                Format("⚪ {item[text]}"),
                id="dormitory_radio",
                item_id_getter=lambda item: item["id"],
                items="dormitory_options",
                on_click=on_dormitory_selected
            ),
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.dormitory,
        getter=get_dormitory_options,
    ),
    
    # Окно 4: Email
    Window(
        Const("📧 Укажи свою корпоративную почту (должна заканчиваться на @spbu.ru, @student.spbu.ru или @gsom.spbu.ru):"),
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
        Const("📱 Введите ваш номер телефона или поделитесь контактом:"),
        TextInput(
            id="phone_input",
            on_success=on_phone_input,
            type_factory=phone_check,
        ),
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
    
    # Окно 7: Мотивация (бывшее окно 8)
    Window(
        Const("🌟 Объясни подробно, почему тебе бы хотелось попробовать себя в роли волонтёра МБ:"),
        TextInput(
            id="motivation_input",
            on_success=on_motivation_input,
        ),
        Cancel(Const("❌ Отмена")),
        state=ApplicationSG.motivation,
    ),
    
    # Окно 8: Обзор ответов (бывшее окно 9)
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

from aiogram import types
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Start
from aiogram_dialog.widgets.text import Const, Format

from bot.states import DepartmentSelectionSG, ApplicationSG


# Обработчики выбора рейтинга для каждого отдела
async def on_logistics_rating(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    rating = int(callback.data.split(":")[1])
    dialog_manager.dialog_data["logistics_rating"] = rating
    await dialog_manager.next()


async def on_marketing_rating(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    rating = int(callback.data.split(":")[1])
    dialog_manager.dialog_data["marketing_rating"] = rating
    await dialog_manager.next()


async def on_pr_rating(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    rating = int(callback.data.split(":")[1])
    dialog_manager.dialog_data["pr_rating"] = rating
    await dialog_manager.next()


async def on_program_rating(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    rating = int(callback.data.split(":")[1])
    dialog_manager.dialog_data["program_rating"] = rating
    await dialog_manager.next()


async def on_partners_rating(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    rating = int(callback.data.split(":")[1])
    dialog_manager.dialog_data["partners_rating"] = rating
    await dialog_manager.next()


# Обработчик завершения выбора отделов
async def on_departments_done(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # Получаем данные об оценках отделов
    result_data = {
        "logistics_rating": dialog_manager.dialog_data.get("logistics_rating"),
        "marketing_rating": dialog_manager.dialog_data.get("marketing_rating"),
        "pr_rating": dialog_manager.dialog_data.get("pr_rating"),
        "program_rating": dialog_manager.dialog_data.get("program_rating"),
        "partners_rating": dialog_manager.dialog_data.get("partners_rating"),
    }
    
    # Закрываем диалог с возвратом данных
    await dialog_manager.done(result=result_data)


# Геттеры данных
async def get_logistics_data(dialog_manager: DialogManager, **kwargs):
    return {"department": "Логистика"}


async def get_marketing_data(dialog_manager: DialogManager, **kwargs):
    return {"department": "Маркетинг"}


async def get_pr_data(dialog_manager: DialogManager, **kwargs):
    return {"department": "PR"}


async def get_program_data(dialog_manager: DialogManager, **kwargs):
    return {"department": "Программа"}


async def get_partners_data(dialog_manager: DialogManager, **kwargs):
    return {"department": "Партнеры"}


async def get_dept_overview_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    
    overview_text = f"""📊 Ваши оценки отделов:

• Логистика: {data.get('logistics_rating', 'Не указано')}
• Маркетинг: {data.get('marketing_rating', 'Не указано')}
• PR: {data.get('pr_rating', 'Не указано')}
• Программа: {data.get('program_rating', 'Не указано')}
• Партнеры: {data.get('partners_rating', 'Не указано')}

Проверьте свои оценки и нажмите "Продолжить" для завершения или "Изменить" для корректировки."""

    return {"overview_text": overview_text}


department_selection_dialog = Dialog(
    # Логистика
    Window(
        Format("📊 Оцените отдел '{department}' от 1 до 5:"),
        Group(
            Button(Const("1"), id="1", on_click=on_logistics_rating),
            Button(Const("2"), id="2", on_click=on_logistics_rating),
            Button(Const("3"), id="3", on_click=on_logistics_rating),
            Button(Const("4"), id="4", on_click=on_logistics_rating),
            Button(Const("5"), id="5", on_click=on_logistics_rating),
            width=5,
        ),
        state=DepartmentSelectionSG.logistics,
        getter=get_logistics_data,
    ),
    
    # Маркетинг
    Window(
        Format("📊 Оцените отдел '{department}' от 1 до 5:"),
        Group(
            Button(Const("1"), id="1", on_click=on_marketing_rating),
            Button(Const("2"), id="2", on_click=on_marketing_rating),
            Button(Const("3"), id="3", on_click=on_marketing_rating),
            Button(Const("4"), id="4", on_click=on_marketing_rating),
            Button(Const("5"), id="5", on_click=on_marketing_rating),
            width=5,
        ),
        state=DepartmentSelectionSG.marketing,
        getter=get_marketing_data,
    ),
    
    # PR
    Window(
        Format("📊 Оцените отдел '{department}' от 1 до 5:"),
        Group(
            Button(Const("1"), id="1", on_click=on_pr_rating),
            Button(Const("2"), id="2", on_click=on_pr_rating),
            Button(Const("3"), id="3", on_click=on_pr_rating),
            Button(Const("4"), id="4", on_click=on_pr_rating),
            Button(Const("5"), id="5", on_click=on_pr_rating),
            width=5,
        ),
        state=DepartmentSelectionSG.pr,
        getter=get_pr_data,
    ),
    
    # Программа
    Window(
        Format("📊 Оцените отдел '{department}' от 1 до 5:"),
        Group(
            Button(Const("1"), id="1", on_click=on_program_rating),
            Button(Const("2"), id="2", on_click=on_program_rating),
            Button(Const("3"), id="3", on_click=on_program_rating),
            Button(Const("4"), id="4", on_click=on_program_rating),
            Button(Const("5"), id="5", on_click=on_program_rating),
            width=5,
        ),
        state=DepartmentSelectionSG.program,
        getter=get_program_data,
    ),
    
    # Партнеры
    Window(
        Format("📊 Оцените отдел '{department}' от 1 до 5:"),
        Group(
            Button(Const("1"), id="1", on_click=on_partners_rating),
            Button(Const("2"), id="2", on_click=on_partners_rating),
            Button(Const("3"), id="3", on_click=on_partners_rating),
            Button(Const("4"), id="4", on_click=on_partners_rating),
            Button(Const("5"), id="5", on_click=on_partners_rating),
            width=5,
        ),
        state=DepartmentSelectionSG.partners,
        getter=get_partners_data,
    ),
    
    # Обзор выбранных оценок
    Window(
        Format("{overview_text}"),
        Group(
            Button(Const("✅ Продолжить"), id="continue", on_click=on_departments_done),
            Button(Const("✏️ Изменить"), id="edit", on_click=lambda c, b, m: m.switch_to(DepartmentSelectionSG.logistics)),
            width=1,
        ),
        state=DepartmentSelectionSG.overview,
        getter=get_dept_overview_data,
    ),
)

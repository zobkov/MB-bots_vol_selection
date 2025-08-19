from aiogram import types
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const

from bot.states import StartSG, MenuSG


async def get_start_data(dialog_manager: DialogManager, **kwargs):
    """Геттер данных для стартового диалога"""
    return {}


start_dialog = Dialog(
    Window(
        StaticMedia(
            url="https://aiogram-dialog.readthedocs.io/en/stable/_images/stack_transitions.png",
            type="photo"
        ),
        Const("🌟 Добро пожаловать в бот отбора волонтеров МБ 2025!\n\n"
              "Здесь вы сможете подать заявку на участие в команде волонтеров "
              "и пройти все этапы отбора.\n\n"
              "Нажмите кнопку ниже, чтобы перейти в главное меню."),
        Start(
            Const("🏠 Перейти в главное меню"),
            id="to_menu",
            state=MenuSG.main
        ),
        state=StartSG.start,
        getter=get_start_data,
    ),
)

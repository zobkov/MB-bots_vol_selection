from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from bot.states import StartSG, MenuSG

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, dialog_manager: DialogManager):
    """Обработчик команды /start"""
    await dialog_manager.start(StartSG.start, mode=StartMode.RESET_STACK)


@router.message(Command("menu"))
async def cmd_menu(message: Message, dialog_manager: DialogManager):
    """Обработчик команды /menu"""
    await dialog_manager.start(MenuSG.main, mode=StartMode.RESET_STACK)

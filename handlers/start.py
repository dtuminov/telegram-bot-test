from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from init import commands


def create_menu_keyboard():
    keyboard = [[command[0] for command in commands]]  # Создаем одну строку с командами
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я бот для знакомств.", reply_markup=create_menu_keyboard())
    command_list = "\n".join([f"{cmd} - {desc}" for cmd, desc in commands])
    await update.message.reply_text(f"Вам доступны следующие команды:\n{command_list}")

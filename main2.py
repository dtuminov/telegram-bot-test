import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

from handlers.start import start
from handlers.help import help_command
from handlers.registration import register, receive_info, receive_photo
from handlers.profile import profile
from handlers.find_matches import find_match, show_next_match
from handlers.edit_profile import edit_profile, receive_new_info
from init import conn, cursor

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем таблицу для хранения пользователей, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
   id INTEGER PRIMARY KEY,
    username TEXT,
    name TEXT,
    course TEXT,
    age TEXT,
    tags TEXT,
    info TEXT,
    preferences TEXT,
    photo TEXT,
    matches TEXT
)
''')

conn.commit()


# Указываем функцию для обработки текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('potential_matches'):
        await show_next_match(update, context)
    elif context.user_data.get('registering'):
        await receive_info(update, context)
    elif context.user_data.get('edit_mode'):
        await receive_new_info(update, context)
    else:
        await update.message.reply_text("Команда не распознана. Используйте /help.")


def main() -> None:
    application = ApplicationBuilder().token("7926794811:AAF-mqYJ67RtCeELt2z9LpyCBFq5Ajj1oZs").build()

    # Установка команд
    application.bot.set_my_commands([
        ("start", "Запустить бота"),
        ("help", "Показать доступные команды"),
        ("register", "Зарегистрироваться"),
        ("profile", "Посмотреть свой профиль"),
        ("edit_profile", "Редактировать профиль"),
        ("find_match", "Найти совпадения")
    ])

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("edit_profile", edit_profile))
    application.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    try:
        main()
    finally:
        conn.close()  # Закрываем соединение с базой данных при завершении

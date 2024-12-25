import logging
import sqlite3
from telegram.ext import ApplicationBuilder, CommandHandler

from handlers.start import start
from handlers.help import help_command

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем и подключаемся к базе данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Создаем таблицу для хранения пользователей, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    name TEXT,
    info TEXT,
    photo TEXT,
    matches TEXT
)
''')

conn.commit()


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
    application.add_handler(CommandHandler("help", help_command))
    # application.add_handler(CommandHandler("register", register))
    # application.add_handler(CommandHandler("profile", profile))
    # application.add_handler(CommandHandler("find_match", find_match))
    # application.add_handler(CommandHandler("edit_profile", edit_profile))
    # application.add_handler(MessageHandler(filters.PHOTO, receive_photo))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    try:
        main()
    finally:
        conn.close()  # Закрываем соединение с базой данных при завершении
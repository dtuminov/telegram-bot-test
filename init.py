import sqlite3
from telegram import Update, ReplyKeyboardMarkup

commands = [
    ("/start", "Запустить бота"),
    ("/help", "Показать доступные команды"),
    ("/register", "Зарегистрироваться"),
    ("/profile", "Посмотреть свой профиль"),
    ("/edit_profile", "Редактировать профиль"),
    ("/find_match", "Найти совпадения")
]


def create_menu_keyboard():
    # Создаем клавиатуру на основе команд, организовав их по двум строкам
    options = []
    for i in range(0, len(commands), 2):  # Разбиваем команды на строки, по 2 в каждой
        options.append([command[0] for command in commands[i:i + 2]])
    return ReplyKeyboardMarkup(options, one_time_keyboard=True, resize_keyboard=True)


# Создаем и подключаемся к базе данных
conn = sqlite3.connect('users.db')  # бля вот это вообще пиздец
cursor = conn.cursor()

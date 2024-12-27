import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from init import conn, cursor

# Команда для отображения профиля
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    if user:
        name = user[2]  # Имя пользователя
        course = user[3]
        course_name = user[4]
        age = user[5]
        tags = user[6]
        info = user[7]
        preferences = user[8]
        photo = user[9]

        response_message = f"Ваш профиль:\nИмя: {name}, {age}\nКурс: {course}, {course_name}\nТэги: {tags}\nИнформация: {info}\nЯ ищу: {preferences}\n"

        if photo:
            await context.bot.send_photo(chat_id=user_id, photo=photo)
        else:
            response_message += "Фотография: не установлена."

        await update.message.reply_text(response_message)
    else:
        await update.message.reply_text(
            "Вы еще не создали профиль. Используйте команду /register."
        )

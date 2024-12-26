import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from init import conn, cursor


async def find_match(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    if user is None:
        await update.message.reply_text("Сначала зарегистрируйся с помощью команды /register.")
        return

    # Получаем всех пользователей, кроме текущего
    cursor.execute('SELECT * FROM users WHERE id != ?', (user_id,))
    potential_matches = cursor.fetchall()

    if not potential_matches:
        await update.message.reply_text("Пока нет совпадений.")
        return

    # Сохраняем потенциальные совпадения в контексте
    context.user_data['potential_matches'] = potential_matches
    context.user_data['match_index'] = 0  # Начинаем с первого совпадения

    # Показываем первое совпадение
    await show_next_match(update, context)


async def show_next_match(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Получаем список потенциальных совпадений и индекс текущего совпадения
    potential_matches = context.user_data.get('potential_matches')
    match_index = context.user_data.get('match_index', 0)

    # Проверяем, есть ли совпадения и индекс меньше длины списка
    if potential_matches and match_index < len(potential_matches):
        # Получаем текущего пользователя
        matched_user = potential_matches[match_index]
        user_photo = matched_user[8]  # Предполагаем, что фото пользователя в 5-й колонке

        # Отправляем фото пользователя
        await context.bot.send_photo(chat_id=update.message.from_user.id, photo=user_photo)

        # Увеличиваем индекс следующего совпадения
        context.user_data['match_index'] += 1

        # Уведомляем пользователя
        await update.message.reply_text("Введите 'следующий', чтобы увидеть следующего пользователя.")
    else:
        await update.message.reply_text("Это все совпадения. Используйте команду /find_match, чтобы начать заново.")


async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.lower()  # Получаем текст от пользователя

    if user_input == 'следующий':
        await show_next_match(update, context)
    else:
        await update.message.reply_text("Пожалуйста, введите 'следующий', чтобы увидеть следующего пользователя.")

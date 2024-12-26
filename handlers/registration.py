import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from init import conn, cursor


# Регистрация пользователя
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    if user is None:
        # Начинаем процесс регистрации
        await update.message.reply_text("Вы зарегистрируетесь. Пожалуйста, введите ваше имя.")
        context.user_data['registering'] = True  # Устанавливаем флаг регистрации
        context.user_data['step'] = 'name'  # Устанавливаем текущий шаг регистрации
    else:
        await update.message.reply_text("Вы уже зарегистрированы!")


# Хэндлер для текстовой информации
async def receive_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    step = context.user_data.get('step')

    if context.user_data.get('registering'):
        if step == 'name':
            name = update.message.text
            context.user_data['name'] = name  # Сохраняем имя
            await update.message.reply_text("Имя сохранено. Теперь расскажите на каком курсе вы обучаетесь.")
            context.user_data['step'] = 'course'  # Переходим к следующему шагу
        elif step == 'course':
            course = update.message.text
            context.user_data['course'] = course  # Сохраняем информацию об пользователе
            await update.message.reply_text("Информация о курсе сохранена. Теперь расскажите сколько вам лет.")
            context.user_data['step'] = 'age'  # Переходим к следующему шагу
        elif step == 'age':
            age = update.message.text
            context.user_data['age'] = age  # Сохраняем информацию об пользователе
            await update.message.reply_text(
                "Информация о возрасте сохранена. Теперь расскажите для чего вы используете этого бота.")
            context.user_data['step'] = 'tags'  # Переходим к следующему шагу
        elif step == 'tags':
            tags = update.message.text
            context.user_data['tags'] = tags  # Сохраняем информацию об пользователе
            await update.message.reply_text("Информация сохранена. Теперь расскажите немного о себе.")
            context.user_data['step'] = 'info'  # Переходим к следующему шагу
        elif step == 'info':
            info = update.message.text
            context.user_data['info'] = info  # Сохраняем информацию об пользователе
            await update.message.reply_text("Информация сохранена. Теперь расскажите кого вы ищете.")
            context.user_data['step'] = 'preferences'  # Переходим к следующему шагу
        elif step == 'preferences':
            preferences = update.message.text
            context.user_data['preferences'] = preferences  # Сохраняем информацию об пользователе
            await update.message.reply_text("Информация сохранена. Теперь пришлите фото для вашего профиля.")
            context.user_data['step'] = 'photo'  # Переходим к следующему шагу
    elif not (context.user_data.get('registering')):
        await update.message.reply_text("Сначала зарегистрируйтесь с помощью команды /register.")


# Хэндлер для получения фотографии
async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if context.user_data.get('registering') and context.user_data.get('step') == 'photo':
        # Получение файла фотографии
        photo_file = update.message.photo[-1].file_id
        name = context.user_data.get('name')
        info = context.user_data.get('info')
        course = context.user_data.get('course')
        age = context.user_data.get('age')
        tags = context.user_data.get('tags')
        preferences = context.user_data.get('preferences')

        # Сохраняем данные в БД
        cursor.execute(
            'INSERT INTO users (id, username, name, course, age, tags, info, preferences, photo, matches) VALUES (?, '
            '?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, update.message.from_user.username, name, course, age, tags, info, preferences, photo_file, '')
        )
        conn.commit()

        # Убираем флаг регистрации
        context.user_data['registering'] = False
        context.user_data['step'] = None  # Сбрасываем шаг

        await update.message.reply_text(
            "Регистрация завершена! Ваш профиль создан. Теперь вы можете использовать команду /profile."
        )
    else:
        await update.message.reply_text("Команда не распознана. Используйте /help.")

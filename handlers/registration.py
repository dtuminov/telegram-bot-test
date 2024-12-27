import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from init import conn, cursor, create_menu_keyboard


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
            await update.message.reply_text("Имя сохранено. Теперь расскажите, на каком курсе вы обучаетесь.")
            context.user_data['step'] = 'course'
        elif step == 'course':
            course = update.message.text
            context.user_data['course'] = course
            await update.message.reply_text(
                "Информация о курсе сохранена. Теперь расскажите, на каком факультете вы обучаетесь.")
            context.user_data['step'] = 'course_name'
        elif step == 'course_name':
            course_name = update.message.text
            context.user_data['course_name'] = course_name
            await update.message.reply_text("Информация о курсе сохранена. Теперь расскажите, сколько вам лет.")
            context.user_data['step'] = 'age'
        elif step == 'age':
            age = update.message.text
            context.user_data['age'] = age
            await update.message.reply_text("Информация о возрасте сохранена. Теперь выберите теги (от 1 до 4).",
                                            reply_markup=await get_tag_keyboard())
            context.user_data['step'] = 'tags'
        elif step == 'tags':
            selected_tag = update.message.text
            if selected_tag == "Готово":
                if 'tags' in context.user_data and context.user_data['tags']:
                    await update.message.reply_text(
                        f"Выбранные теги: {', '.join(context.user_data['tags'])}. Теперь расскажите о себе.",
                        reply_markup=create_menu_keyboard())
                    context.user_data['step'] = 'info'
                else:
                    await update.message.reply_text("Вы не выбрали теги! Пожалуйста, выберите хотя бы один тег.")
            else:
                tags = await get_tag_keyboard_options()
                if selected_tag in tags:
                    if 'tags' not in context.user_data:
                        context.user_data['tags'] = []
                    current_tags = context.user_data['tags']

                    if selected_tag in current_tags:
                        current_tags.remove(selected_tag)  # Убрать тег, если он уже выбран
                    elif len(current_tags) < 4:
                        current_tags.append(selected_tag)  # Добавить тег, если меньше 4

                    context.user_data['tags'] = current_tags
                    await update.message.reply_text(
                        f"Выбранные теги: {', '.join(current_tags)}. Выберите ещё или нажмите 'Готово' для завершения.")
                else:
                    await update.message.reply_text("Нет такого тега, повторите попытку.")

        elif step == 'info':
            info = update.message.text
            context.user_data['info'] = info
            await update.message.reply_text("Информация сохранена. Теперь расскажите, кого вы ищете.",
                                            reply_markup=await get_gender_keyboard())
            context.user_data['step'] = 'preferences'
        elif step == 'preferences':
            preferences = update.message.text
            if preferences in ["Парня", "Девушку"]:
                context.user_data['preferences'] = preferences
                await update.message.reply_text("Информация сохранена. Теперь пришлите фото для вашего профиля.",
                                                reply_markup=create_menu_keyboard())
                context.user_data['step'] = 'photo'
            else:
                await update.message.reply_text("Выберете из предложенного: 'Парня' или 'Девушку'.")

    elif not context.user_data.get('registering'):
        await update.message.reply_text("Сначала зарегистрируйтесь с помощью команды /register.")


async def get_tag_keyboard():
    tags = ["Спорт", "Музыка", "Путешествия", "Наука", "Искусство", "Технологии", "Кулинария", "Готово"]
    keyboard = ReplyKeyboardMarkup([[tag] for tag in tags], one_time_keyboard=True, resize_keyboard=True)
    return keyboard


async def get_gender_keyboard():
    keyboard = ReplyKeyboardMarkup([["Парня"], ["Девушку"]], one_time_keyboard=True, resize_keyboard=True)
    return keyboard


async def get_tag_keyboard_options():
    return ["Спорт", "Музыка", "Путешествия", "Наука", "Искусство", "Технологии", "Кулинария"]


# Хэндлер для получения фотографии
async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if context.user_data.get('registering') and context.user_data.get('step') == 'photo':
        # Получение файла фотографии
        photo_file = update.message.photo[-1].file_id
        name = context.user_data.get('name')
        info = context.user_data.get('info')
        course = context.user_data.get('course')
        course_name = context.user_data.get('course_name')
        age = context.user_data.get('age')
        tags = ', '.join(['#' + tag for tag in context.user_data.get('tags', [])])  # Записываем теги в формате #тэг
        preferences = context.user_data.get('preferences')

        # Сохраняем данные в БД
        cursor.execute(
            'INSERT INTO users (id, username, name, course, course_name, age, tags, info, preferences, photo, '
            'matches) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, update.message.from_user.username, name, course, course_name, age, tags, info, preferences,
             photo_file, '')
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

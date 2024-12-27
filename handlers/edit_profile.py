import logging

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from init import create_menu_keyboard

from init import cursor, conn

logger = logging.getLogger(__name__)

def check_user_exists(user_id):
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    return cursor.fetchone() is not None

# Функция для обновления данных пользователя в базе данных
def update_data_in_db(user_id, column_name, new_value):
    logger.info(f'Попытка обновления {column_name} пользователя. User ID: {user_id}, Новое значение: {new_value}')

    # Проверка на существование пользователя
    if not check_user_exists(user_id):
        logger.warning(f'Пользователь с ID {user_id} не найден.')
        return

    try:
        # Обновляем на новое значение
        cursor.execute(f'''
            UPDATE users SET {column_name} = ? WHERE id = ?
        ''', (new_value, user_id))
        conn.commit()

        if cursor.rowcount == 0:
            logger.warning(f'Данные пользователя с ID {user_id} не были обновлены.')
        else:
            logger.info(f'{column_name} пользователя с ID {user_id} обновлено на {new_value}.')

    except Exception as e:
        logger.error(f'Ошибка обновления данных пользователя: {e}')

async def edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    options = [['Описание', 'Предпочтения'], ['Теги', 'Фото'], ['Выход']]
    reply_markup = ReplyKeyboardMarkup(options, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        'Что вы хотите изменить?',
        reply_markup=reply_markup
    )

    # Сохраняем состояние для ожидания ответа от пользователя
    context.user_data['edit_mode'] = True
    context.user_data['user_id'] = user.id  # Сохраняем ID пользователя для дальнейшего использования

async def receive_new_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('edit_mode'):
        user_id = context.user_data.get('user_id')

        # Проверяем выбранный пункт
        selected_option = update.message.text

        if selected_option == 'Выход':
            context.user_data['edit_mode'] = False
            await update.message.reply_text('Вы вышли из режима редактирования.', reply_markup=create_menu_keyboard())
            return

        # Условие для каждого поля
        if selected_option in ['Описание', 'Предпочтения', 'Теги', 'Фото']:
            context.user_data['selected_field'] = selected_option
            await update.message.reply_text(f'Введите новое значение для: {selected_option}')
        else:
            # Получаем новое значение
            new_value = update.message.text
            selected_field = context.user_data.get('selected_field')

            # Изменяем на соответствующее название поля в базе данных
            column_name_mapping = {
                'Описание': 'info',
                'Кого я ищу': 'preferences',
                'Теги': 'tags',
                'Фото': 'photo'
            }
            column_name = column_name_mapping.get(selected_field)

            # Проверка наличия пользователя в базе данных
            if check_user_exists(user_id):
                update_data_in_db(user_id, column_name, new_value)
                await update.message.reply_text(f'Ваше поле "{selected_field}" было обновлено на: {new_value}', reply_markup=create_menu_keyboard())
            else:
                await update.message.reply_text('Пользователь не найден в базе данных. Пожалуйста, зарегистрируйтесь.', reply_markup=create_menu_keyboard())

            # Убираем режим редактирования
            context.user_data['edit_mode'] = False
            context.user_data.pop('selected_field', None)
        return

    await update.message.reply_text('Вы не находитесь в режиме редактирования. Начните с команды /edit_profile.', reply_markup=create_menu_keyboard())
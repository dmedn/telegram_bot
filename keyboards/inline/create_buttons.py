from loguru import logger
from loader import bot
from telebot import types
from telebot.types import Dict, Message


def show_buttons_photo_need_yes_no(message: Message) -> None:
    """Отображает в чате инлайн-кнопки с вопросом - нужны ли пользователи фотографии"""

    logger.info(f'Вызов функции {show_buttons_photo_need_yes_no.__name__}. User_id: {message.chat.id}')
    keyboard_yes_no = types.InlineKeyboardMarkup()
    keyboard_yes_no.add(types.InlineKeyboardButton(text='ДА', callback_data='yes'))
    keyboard_yes_no.add(types.InlineKeyboardButton(text='НЕТ', callback_data='no'))
    bot.send_message(message.chat.id, "Вам нужны фотографии?", reply_markup=keyboard_yes_no)


def show_city_buttons(message: Message, possible_city: dict) -> None:
    logger.info(f'Вызов функции {show_city_buttons.__name__}. User_id: {message.chat.id}')
    keyboard_city = types.InlineKeyboardMarkup()
    for key, value in possible_city.items():
        keyboard_city.add(types.InlineKeyboardButton(text=value["regionNames"], callback_data=value["gaiaId"]))
    bot.send_message(message.from_user.id, 'Выберите город', reply_markup=keyboard_city)

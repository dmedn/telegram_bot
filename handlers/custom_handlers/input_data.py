import datetime

import keyboards.inline.create_buttons
import utils
from loguru import logger
from telebot.types import Message
from loader import bot
from states.user_states import UserInputState
from keyboards.inline.create_buttons import show_city_buttons
from keyboards.calendar.telebot_calendar import Calendar

bot_calendar = Calendar()


def check_command(command: str) -> str:
    """Обрабатывает команду сортировки, которую выбрал пользователь"""
    if command == '/lowprice' or command == '/highprice':
        return 'PRICE_LOW_TO_HIGH'
    elif command == '/bestdeal':
        return 'DISTANCE'


def my_calendar(message: Message, params: str) -> None:
    """Отдача клавиатуры для выобра дат заезда и выезда"""
    bot.send_message(message.chat.id, f'Выберите дату {params}.', reply_markup=bot_calendar.create_calendar())


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def low_high_best_handler(message: Message) -> None:
    """Перехватывает команды /lowprice, /highprice, /bestdeal.
    Запрашивает у пользователя город, в котором необходимо осуществить поиск"""

    logger.info(f'Запуск обработчика {low_high_best_handler.__name__}')

    bot.set_state(message.chat.id, UserInputState.command)
    with bot.retrieve_data(message.chat.id) as data:
        data.clear()
        data['command'] = message.text
        data['sort'] = check_command(message.text)
        data['date_time'] = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        data['chat_id'] = message.chat.id
    bot.set_state(message.chat.id, UserInputState.input_city)
    bot.send_message(message.from_user.id, 'Укажите город, в котором будем искать?')


@bot.message_handler(state=UserInputState.input_city)
def input_city_handler(message: Message) -> None:
    """Перехватывает введенный пользователем город, отправляет запрос на сервер на подбор вариантов городов.
    Найденные сервером города передает конструктору клавиатуры"""

    logger.info(f'Запуск обработчика {input_city_handler.__name__}')

    with bot.retrieve_data(message.chat.id) as data:
        data['input_city'] = message.text
        url = "https://hotels4.p.rapidapi.com/locations/v3/search"
        querystring = {'q': message.text, 'locale': 'en_US'}
        response_cities = utils.api_request.request('get', url, querystring)
        if response_cities.status_code == 200:
            logger.info(
                f'Получен ответ от сервера. Код ответа - {response_cities.status_code}, User_id - {message.chat.id}')
            cities = utils.processing_json.get_city(response_cities.text)
            show_city_buttons(message, cities)
        else:
            logger.error(f'Обработчик: {input_city_handler.__name__}.'
                         f' Сервер не отвечает, код ответа: {response_cities.status_code}')
            bot.send_message(message.chat.id, f'Что-то пошло не так. Код ответа сервера: {response_cities.status_code}')
            bot.send_message(message.chat.id, 'Попробуйте еще раз. Выберите другой город')
            data.clear()


@bot.message_handler(state=UserInputState.quantity_hotels)
def quantity_hotels_handler(message: Message) -> None:
    """Перехват и валидация введенного пользователем количества отелей. """

    logger.info(f'Запуск обработчика {quantity_hotels_handler.__name__}')

    if message.text.isdigit():
        if 0 < int(message.text) <= 25:
            with bot.retrieve_data(message.chat.id) as data:
                data['quantity_hotels'] = message.text
            bot.set_state(message.chat.id, UserInputState.priceMin)
            bot.send_message(message.chat.id, 'Введите минимальную стоимость бронирования (в долларах США)')
        else:
            bot.send_message(message.chat.id, 'Укажите количество отелей в диапазоне от 0 до 25')
    else:
        bot.send_message(message.chat.id, f'Вы ввели {message.text}. Это не число, попробуйте еще раз')


@bot.message_handler(state=UserInputState.priceMin)
def input_price_min_handler(message: Message) -> None:
    """Перехват и валидация введенной пользователем минимальной стоимости бронирования"""

    logger.info(f'Запуск обработчика {input_price_min_handler.__name__}')

    if message.text.isdigit():
        with bot.retrieve_data(message.chat.id) as data:
            data['price_min'] = message.text
        bot.set_state(message.chat.id, UserInputState.priceMax)
        bot.send_message(message.chat.id, 'Введите максимальную стоимость бронирования (в долларах США)')
    else:
        bot.send_message(message.chat.id, f'Вы ввели {message.text}. Это не число, попробуйте еще раз')


@bot.message_handler(state=UserInputState.priceMax)
def input_price_max_handler(message: Message) -> None:
    """Перехват и валидация максимальной стоимости бронирования"""

    logger.info(f'Запуск обработчика {input_price_max_handler.__name__}')

    if message.text.isdigit():
        with bot.retrieve_data(message.chat.id) as data:
            if int(data['price_min']) < int(message.text):
                data['price_max'] = message.text
                keyboards.inline.create_buttons.show_buttons_photo_need_yes_no(message)
            else:
                bot.send_message(message.chat.id, f'Максимальная стоимость должна быть больше минимальной.'
                                                  f'Минимальная стоимость {data['price_min']}')
    else:
        bot.send_message(message.chat.id, f'Вы ввели: {message.text}. Это не число, попробуйте еще раз')


@bot.message_handler(state=UserInputState.photo_count)
def input_count_photo_handler(message: Message) -> None:
    """Перехват и валидация количества запрашиваемых пользователем фотографий"""

    logger.info(f'Запуск обработчика {input_count_photo_handler.__name__}')

    if message.text.isdigit():
        if 0 < int(message.text) <= 10:
            with bot.retrieve_data(message.chat.id) as data:
                data['photo_count'] = message.text
            my_calendar(message, params='заезда')
        else:
            bot.send_message(message.chat.id, 'Число фотографий должно быть в диапазоне от 0 до 10')
    else:
        bot.send_message(message.chat.id, f'Вы ввели {message.text}. Это не число, повторите ввод')


@bot.message_handler(state=UserInputState.landmarkIn)
def input_landmark_in_handler(message: Message) -> None:
    """Перехват и валидация расстояния от центра города"""

    logger.info(f'Запуск обработчика {input_landmark_in_handler.__name__}')

    if message.text.isdigit():
        with bot.retrieve_data(message.chat.id) as data:
            data['landmark_in'] = message.text
        bot.set_state(message.chat.id, UserInputState.landmarkOut)
        bot.send_message(message.chat.id, 'Введите максимальное расстояние от центра')
    else:
        bot.send_message(message.chat.id, f'Вы ввели {message.text}. Это не число, попробуйте еще раз')


@bot.message_handler(state=UserInputState.landmarkOut)
def input_landmark_out_handler(message: Message) -> None:
    """Перехват и валидация максимального расстояния от центра"""

    logger.info(f'Запуск обработчика {input_landmark_out_handler.__name__}')

    if message.text.isdigit():
        with bot.retrieve_data(message.chat.id) as data:
            if int(message.text) > data['landmark_in']:
                data['landmark_out'] = message.text
                utils.show_data_and_find_hotels.get_data(message, data)
            else:
                bot.send_message(message.chat.id, f'Максимальное расстояние должно быть больше минимального.'
                                                  f'Вы ввели {data['landmark_in']} как минимальное. Попробуйте еще раз')
    else:
        bot.send_message(message.chat.id, f'Вы ввели {message.text}. Это не число, попробуйте еще раз')

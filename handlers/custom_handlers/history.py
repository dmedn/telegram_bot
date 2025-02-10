import database
from loguru import logger
from telebot.types import Message, InputMediaPhoto
from states.user_states import UserInputState
from loader import bot


@bot.message_handler(commands=['/history'])
def get_query_handler(message: Message) -> None:
    """Возвращает пользователю его предыдущие запросы по отелям"""

    logger.info(f'Запуск обработчика {get_query_handler.__name__}')

    queries = database.read_from_database.read_query(message.chat.id)

    if queries:
        for query in queries:
            bot.send_message(message.chat.id, f'{query[0]}. Вы запрашивали город {query[2]}. Дата запроса: {query[1]}')
        bot.set_state(message.chat.id, UserInputState.select_number)
        bot.send_message(message.chat.id, 'Какой запрос вас интересует?')
    else:
        bot.send_message(message.chat.id, 'В базе данных нет ваших запросов')


@bot.message_handler(state=UserInputState.select_number)
def number_query_handler(message: Message) -> None:
    """Перехват и валидация введенного пользователем номера запроса."""
    logger.info(f'Запуск обработчика {number_query_handler.__name__}')

    if message.text.isdigit():
        queries = database.read_from_database.read_query(message.chat.id)
        number_query = []
        photo_need = ''
        for query in queries:
            number_query.append(query[0])
            if int(message.text) == 3 and query[3] == 'yes':
                photo_need = 'yes'
        if photo_need == 'no':
            bot.send_message(message.chat.id, 'Пользователь выбрал вариант без фото')

        if int(message.text) in number_query:
            history_dict = database.read_from_database.get_history_response(message)
            with bot.retrieve_data(message.chat.id) as data:
                data.clear()
            if history_dict:
                for hotel in history_dict.items():
                    media = []
                    caption = f"Название отеля: {hotel[1]['name']}]\n Адрес отеля: {hotel[1]['address']}"
                    f"\nСтоимость проживания в " \
                    f"сутки $: {hotel[1]['price']}\nРасстояние до центра: {hotel[1]['distance']}"
                    urls = hotel[1]['images']
                    if photo_need == 'yes':
                        for number, url in enumerate(urls):
                            if number == 0:
                                media.append(InputMediaPhoto(media=url, caption=caption))
                            else:
                                media.append(InputMediaPhoto(media=url))
                        bot.send_media_group(message.chat.id, media)
                    else:
                        bot.send_message(message.chat.id, caption)
            else:
                bot.send_message(message.chat.id, 'Запрос пуст. Попробуйте еще раз')
        else:
            bot.send_message(message.chat.id, 'Запроса с таким номером нет. Попробуйте еще раз')
    else:
        bot.send_message(message.chat.id, 'Некорректный ввод. Запрос должен быть в числовой форме')
    bot.set_state(message.chat.id, None)

import database
import utils
import random
from config_data.settings import settings
from loader import bot
from loguru import logger
from telebot.types import Message, Dict, InputMediaPhoto


def find_and_show_hotel(message: Message, data: Dict) -> None:
    """Формирование запросов на поиск отелей и отдача пользователю в чат"""

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": data['destination_id']},
        "checkInDate": {
            'day': int(data['checkInDate']['day']),
            'month': int(data['checkInDate']['month']),
            'year': int(data['checkInDate']['year'])
        },
        "checkOutDate": {
            'day': int(data['checkOutDate']['day']),
            'month': int(data['checkOutDate']['month']),
            'year': int(data['checkOutDate']['year'])
        },
        "rooms": [
            {
                "adults": 2,
                "children": [{"age": 5}, {"age": 7}]
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 30,
        "sort": data['sort'],
        "filters": {"price": {
            "max": int(data['price_max']),
            "min": int(data['price_min'])
        }}
    }

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    response_hotels = utils.api_request.request('POST', url, payload)
    status_code = response_hotels.status_code
    logger.info(f'Код ответа сервера: {status_code}. User_id: {message.chat.id}')
    if status_code == 200:
        hotels = utils.processing_json.get_hotels(
            response_text=response_hotels.text,
            command=data['command'],
            landmark_in=data['landmark_in'],
            landmark_out=data['landmark_out'],
        )
        if 'error' in hotels:
            bot.send_message(message.chat.id, hotels['error'])
            bot.send_message(message.chat.id, 'Попробуйте повторить поиск ')
            bot.send_message(message.chat.id, '')
        count = 0
        for hotel in hotels.values():
            if count < int(data['quantity_hotels']):
                count += 1
                summary_payload = {
                    'currency': 'USD',
                    'eapid': 1,
                    'loacale': 'en_US',
                    'siteId': 300000001,
                    'propertyId': hotel['id'],
                }
                summary_url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"
                get_summary = utils.api_request.request('POST', summary_url, summary_payload)
                logger.info(f'Status code: {get_summary.status_code}. User_id: {message.chat.id}')
                if get_summary.status_code == 200:
                    summary_info = utils.processing_json.hotels_info(get_summary.text)
                    caption = f'Название: {hotel["name"]}\n ' \
                              f'Адрес: {summary_info["address"]}\n' \
                              f'Стоимость проживания в сутки: {hotel["price"]}\n ' \
                              f'Расстояние до центра: {round(hotel["distance"], 2)} mile.\n'
                    images = []
                    links_to_images = []
                    try:
                        for random_url in range(int(data['photo_count'])):
                            links_to_images.append(
                                summary_info['images'][random.randint(0, len(summary_info['images']) - 1)])
                    except IndexError:
                        continue
                    data_to_db = {
                        hotel['id']: {
                            'name': hotel['name'],
                            'address': summary_info['address'],
                            'user_id': message.chat.id,
                            'price': hotel['price'],
                            'distance': round(hotel['distance'], 2),
                            'date_time': data['date_time'],
                            'images': links_to_images,
                        }
                    }
                    database.add_to_database.add_response(data_to_db)
                    if int(data['photo_count']) > 0:
                        for number, url in enumerate(links_to_images):
                            if number == 0:
                                images.append(InputMediaPhoto(media=url, caption=caption))
                            else:
                                images.append(InputMediaPhoto(media=url))
                        bot.send_media_group(message.chat.id, images)
                    else:
                        bot.send_message(message.chat.id, caption)
                else:
                    bot.send_message(message.chat.id, f'Что-то пошло не так')
                    logger.error(f'Прозошла ошибка. Код: {get_summary.status_code}')
            else:
                break
    else:
        bot.send_message(message.chat.id, f'Что-то пошло не так. Попробуйте еще раз!')
        logger.error(f'Произошла ошибка. Код: {response_hotels.status_code}')
    logger.info(f'Поиск завершен. User_id: {message.chat.id}')
    bot.send_message(message.chat.id, 'Поиск завершен!')
    bot.send_message(message.chat.id, None)


def get_data(message: Message, data: dict) -> None:
    """Собираем инофрмацию от пользователя, добавляем ее в историю запросов и передаем в функцию поиска отелей"""

    database.add_to_database.add_query(data)
    text_message = (f'Данные запроса:\n'
                    f'Дата и время запроса: {data['date_time']}\n,'
                    f'Введена команда: {data['command']}\n'
                    f'Город: {data['input_city']}\n')
    bot.send_message(message.chat.id, text_message)
    logger.info(f'Данные от пользователя {message.chat.id} получены')
    find_and_show_hotel(message, data)

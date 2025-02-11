import sqlite3
from loguru import logger
from config_data.settings import settings


def read_query(user_id: int) -> list:
    """Возвращает результаты запросов пользователя по id """

    logger.info(f'Запрос к базе данных для пользователя {user_id}')
    connection = sqlite3.connect(settings.DB_NAME)
    with connection as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT 'id', 'date_time', 'input_city', 'photo_need' FROM query WHERE user_id = ?", (user_id,))
            queries = cursor.fetchall()
            conn.close()
            return queries
        except sqlite3.OperationalError:
            logger.error(f'В базе данных отсутствуют запросы от пользователя {user_id}')
            conn.close()
            return []


def get_history_response(message) -> dict:
    """Возвращает результаты запроса по его id"""
    connect = sqlite3.connect(settings.DB_NAME)
    with connect as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM response WHERE `query_id` = ?", (message.text,))
            records = cursor.fetchall()
            history = {}
            for item in records:
                hotel_id = item[2]
                history[item[2]] = {'name': item[3], 'address': item[4], 'price': item[5], 'distance': item[6]}
                cursor.execute("SELECT * FROM images WHERE `hotel_id` = ?", (hotel_id,))
                images = cursor.fetchall()
                links = []
                for link in images:
                    links.append(link[2])
                history[item[2]]['images'] = links
            connect.close()
            return history
        except sqlite3.OperationalError:
            logger.error(f'В базе данных отсутствует данные запроса. User_id: {message.chat.id}')
            conn.close()

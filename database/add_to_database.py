import sqlite3
from loguru import logger
from telebot.types import Message
from config_data.settings import settings


def add_user(message: Message) -> None:
    """Если база данных еще не создана - создает базу данных с даннными пользователя
    id,username, и если есть - 'имя и фамилия', и добавляет туда данные, если пользователь
    использует бота впервые"""
    connection = sqlite3.connect(settings.DB_NAME)
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        chat_id INTEGER UNIQUE, username STRING, full_name TEXT);""")
        conn.commit()
        try:
            cursor.execute(
                "INSERT INTO user(chat_id, username, full_name) VALUES (?,?,?)",
                (message.chat.id, message.from_user.username, message.from_user.full_name))
            logger.info(f'Добавлен пользователь - {message.from_user.username}')
            conn.commit()

        except sqlite3.IntegrityError:
            logger.info(f'Пользователь с именем {message.from_user.username} уже существует')
            conn.close()


def add_query(query: dict) -> None:
    """Создает таблицу, если она отсутствует в базе данных, и добавляет туда запрос пользователя. Для каждого пользователя
    будем хранить только 5 последних запросов"""
    user_id = query['chat_id']
    connection = sqlite3.connect(settings.DB_NAME)
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS query(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
       user_id INTEGER, date_time STRING, input_city STRING, destination_id STRING, photo_need STRING,
       response_id INTEGER, FOREIGN KEY (response_id) REFERENCES response(id) ON DELETE CASCADE ON UPDATE CASCADE);""")
        try:
            cursor.execute(
                'INSERT INTO query(user_id, input_city, photo_need, destination_id, date_time) VALUES (?,?,?,?,?)',
                (user_id, query['input_city'], query['photo_need'], query['destination_id'], query['date_time'])
            )
            logger.info(f'Добавлен новый запрос от пользователя {user_id}')
            cursor.execute(f"""
                    DELETE FROM query WHERE query.[date_time] = (SELECT MIN([date_time]) FROM query WHERE `user_id` = '{user_id}')
                    AND ((SELECT COUNT(*) FROM query WHERE `user_id` = '{user_id}' ) > 5 )
                """)
            conn.commit()
        except sqlite3.IntegrityError:
            logger.info(f'Запрос с такой датой и временем уже существует. Пользователь {user_id}')
            conn.close()


def add_response(response: dict) -> None:
    """Создает таблицу, если она отсутствует в базе данных и добавляет туда результаты запроса к внешнему API"""
    connection = sqlite3.connect(settings.DB_NAME)
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS response(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, query_id INTEGER,
        hotel_id STRING, name STRING, address STRING, price REAL, distance REAL, FOREIGN KEY(hotel_id) REFERENCES images(hotel_id)
        ON DELETE CASCADE ON UPDATE CASCADE);""")
        for item in response.items():
            cursor.execute(f"SELECT `id` FROM query WHERE `date_time` = ?", (item[1]['date_time'],))
            query_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO response(query_id, hotel_id, name, address, price, distance) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    query_id,
                    item[0],
                    item[1]['name'],
                    item[1]['address'],
                    item[1]['price'],
                    item[1]['distance']
                )
            )
            logger.info(f'В базу данных добавлены данные отеля. User_id: {item[1]["user_id"]}')
            for link in item[1]['images']:
                cursor.execute("""CREATE TABLE IF NOT EXISTS images(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                hotel_id INTEGER REFERENCES response (id),
                link TEXT     
                );""")
                cursor.execute("INSERT INTO images (hotel_id, link) VALUES (?, ?)", (item[0], link))
            logger.info(f'В базу данных добавлены ссылки на фотографии отеля. User_id: {item[1]["user_id"]}')
            connection.commit()
        connection.close()

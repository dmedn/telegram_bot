import os
from dotenv import find_dotenv, load_dotenv
from loguru import logger


class BaseSettings:
    def __init__(self):
        self.BOT_TOKEN = os.getenv('BOT_TOKEN')
        self.RAPID_API_KEY = os.getenv('RAPID_API_KEY')
        self.DB_NAME = os.getenv('DB_NAME')
        self.DEFAULT_COMMANDS = (
            ('start', "Запустить бота"),
            ('help', "Помощь по командам бота"),
            ('lowprice', "Вывод самых дешёвых отелей в городе"),
            ('highprice', "Вывод самых дорогих отелей в городе"),
            ('bestdeal', "вывод отелей, наиболее подходящих по цене и расположению от центра"),
            ('history', "Вывод истории поиска отелей")
        )


if not find_dotenv():
    logger.error('Отсутствует файл .env. Переменные окружения не загружены')
    exit('Переменные окружения не загружены - отсутствует файл .env')
else:
    load_dotenv()
    settings = BaseSettings()
    logger.info(f'Загружены переменные окружения. Создан объект: {settings.__name__}')

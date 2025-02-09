import sqlite3
from loguru import logger
from telebot.types import Message
from config_data.settings import settings

def add_user(message:Message) -> None:
    """Если база данных еще не создана - создает базу данных с даннными пользователя
    id,username, и если есть - 'имя и фамилия', и добавляет туда данные, если пользователь
    использует бота впервые"""
    connection = sqlite3.connect(settings.DB_NAME)
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT""")
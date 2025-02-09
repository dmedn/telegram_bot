import database
from telebot.types import Message
from loader import bot

@bot.message_handler(commands=['start'])
def bot_start_handler(message: Message) -> None:
    bot.reply_to(message, f'Приветствую, {message.from_user.full_name}')
    database.add_to_database.add_user(message)
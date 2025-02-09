from loader import bot
from telebot.types import Message


@bot.message_handler(func=lambda message: True)
def bot_echo_handler(message: Message) -> None:
    if message.text == 'привет':
        bot.reply_to(message, f'И тебе привет, {message.from_user.full_name}')
    else:
        bot.reply_to(message, f'Сообщение {message.text} без состояния или фильтра')

from telebot.types import Message
from config_data.settings import settings
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help_handler(message: Message) -> None:
    answer = [f'/{command} - {description}' for command, description in settings.DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(answer))

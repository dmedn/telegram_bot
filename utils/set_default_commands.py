from telebot.types import BotCommand
from config_data.settings import settings


def set_default_commands(bot):
    commands = settings.DEFAULT_COMMANDS
    bot.set_my_commands([BotCommand(*i) for i in commands])

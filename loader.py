from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data.settings import settings

storage = StateMemoryStorage()
bot = TeleBot(state_storage=storage, token=settings.BOT_TOKEN)


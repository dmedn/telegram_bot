from loguru import logger
from loader import bot
from telebot.types import CallbackQuery
from states.user_states import UserInputState


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def destination_id_callback_handler(call: CallbackQuery) -> None:
    """Перехват введенного пользователем города"""

    logger.info(f'Запуск обработчика {destination_id_callback_handler.__name__}')

    if call.data:
        bot.set_state(call.message.chat.id, UserInputState.destination_id)
        with bot.retrieve_data(call.message.chat.id) as data:
            data['destination_id'] = call.data
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.set_state(call.message.chat.id, UserInputState.quantity_hotels)
        bot.send_message(call.message.chat.id, 'Какое количество отелей вы можете найти?')

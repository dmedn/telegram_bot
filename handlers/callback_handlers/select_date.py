import datetime
import utils
from loguru import logger
from loader import bot
from states.user_states import UserInputState
from handlers.custom_handlers import input_data
from telebot.types import CallbackQuery
from keyboards.calendar.telebot_calendar import CallbackData, Calendar, check_month_day

calendar = Calendar()
calendar_callback = CallbackData('calendar', 'action', 'year', 'month', 'day')

@bot.callback_query_handler(func= lambda call: call.data.startswith(calendar_callback.prefix))
def input_date_handler(callback: CallbackQuery) -> None:
    """Перехват и валидация указанных пользователем дат заезда и выезда"""

    logger.info(f'Вызов обработчика {input_date_handler.__name__}')

    name, action, year, month, day = callback.data.split(sep=calendar_callback.sep)
    calendar.calendar_query_handler(bot=bot, call=callback,name=name, action=action, year=year,month=month, day=day)

    if action == 'DAY':
        month = check_month_day(month)
        day = check_month_day(day)
        select_date = year + month + day

        now_year, now_month, now_day = datetime.datetime.now().strftime('%Y.%m.%d').split('.')
        now = now_year + now_month + now_day

        bot.set_state(callback.message.chat.id, UserInputState.input_date)
        with bot.retrieve_data(callback.message.chat.id) as data:
            if 'checkInDate' in data:
                checkin = int(data['checkInDate']['year'] + data['checkInDate']['month'] + data['checkInDate']['day'])
                if int(select_date) > checkin:
                    data['checkOutDate'] = {'day': day, 'month': month, 'year': year}
                    data['landmark_in'] = 0
                    data['landmark_out'] = 0
                    if data['sort'] == 'DISTANCE':
                        bot.set_state(callback.message.chat.id, UserInputState.landmarkIn)
                        bot.send_message(callback.message.chat.id, 'Укажите минимальное расстояние от центра')
                    else:
                        utils.show_data_and_find_hotels.get_data(callback.message, data)
                else:
                    bot.send_message(callback.message.chat.id, 'Некорректный выбор даты. Дата выезда должна быть позже даты заезда')
                    input_data.my_calendar(callback.message, 'выезда')
            else:
                data['checkInDate'] = {'day': day, 'month': month, 'year': year}
                input_data.my_calendar(callback.message, 'выезда')
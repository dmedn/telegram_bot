from loguru import logger
from loader import bot
from states.contact_information import UserInfoState
from keyboards.reply.request_contact import request_contact
from telebot.types import Message


@bot.message_handler(commands=['/survey'])
def survey_handler(message: Message) -> None:
    """Начало диалога с пользователем"""

    logger.info(f'Запуск обработчика {survey_handler.__name__}')

    bot.set_state(message.from_user.id, UserInfoState.name, message.chat.id)
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.username}, введи свое имя!!!')


@bot.message_handler(state=UserInfoState.name)
def get_name_handler(message: Message) -> None:
    """Перехватывает имя пользователя"""

    logger.info(f'Запуск обработчика {get_name_handler.__name__}')

    if message.text.isalpha():
        bot.send_message(message.from_user.id, f'Привет, {message.chat.id}! Теперь укажи свой возраст!')
        bot.set_state(message.from_user.id, UserInfoState.age, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Имя должно содержать только буквы!')


@bot.message_handler(state=UserInfoState.age)
def get_age_handler(message: Message) -> None:
    """Перехватывает возраст пользователя"""

    logger.info(f'Запуск обработчика {get_age_handler.__name__}')

    if message.text.isdigit():
        bot.send_message(message.from_user.id, f'Отлично! Теперь укажи свою страну!')
        bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['age'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Возраст должен содержать только цифры!')


@bot.message_handler(state=UserInfoState.country)
def get_country_handler(message: Message) -> None:
    """Перехватывает страну пользователя"""

    logger.info(f'Запуск обработчика {get_country_handler.__name__}')

    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Теперь укажи свой город!')
        bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['country'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Название страны указано некорректно')


@bot.message_handler(state=UserInfoState.city)
def get_city_handler(message: Message) -> None:
    """Перехватывает город пользователя"""

    logger.info(f'Запуск обработчика {get_city_handler.__name__}')

    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Отлично! Теперь отправь свой номер телефона!',
                         reply_markup=request_contact())
        bot.set_state(message.from_user.id, UserInfoState.phone_number, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Название города указано некорректно')


@bot.message_handler(state=UserInfoState.phone_number, content_types=['text', 'contact'])
def get_contact(message: Message) -> None:
    """Перехватывает номер телефона пользователя"""

    logger.info(f'Запуск обработчика {get_contact.__name__}')

    if message.content_type == 'contact':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['phone_number'] = message.contact.phone_number
            answer = f'Спасибо за информацию! Ваши данные: \n'
            f'Имя - {data['name']}\n'
            f'Возраст - {data['age']}\n'
            f'Страна - {data['country']}\n'
            f'Город - {data['city']}\n'
            f'Номер телефона - {data['phone_number']}\n'
            bot.send_message(message.from_user.id, answer)
    else:
        bot.send_message(message.from_user.id, 'Чтобы отправить контактную информацию, нажми на кнопку!')

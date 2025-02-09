from telebot.handler_backends import State, StatesGroup


class UserInputState(StatesGroup):
    command = State()
    input_city = State()
    destination_id = State()
    quantity_hotels = State()
    photo_count = State()
    input_date = State()
    priceMin = State()
    priceMax = State()
    landmarkIn = State()
    landmarkOut = State()
    select_number = State()

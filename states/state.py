from aiogram.filters.state import State, StatesGroup


class RegisterState(StatesGroup):
    full_name = State()
    phone = State()
    front_p = State()
    back_p = State()
    front_tex = State()
    back_tex = State()
    car = State()
    payment = State()


class Check(StatesGroup):
    start = State()
    final = State()


class CheckPyment(StatesGroup):
    start = State()

from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    get_pdf = State()
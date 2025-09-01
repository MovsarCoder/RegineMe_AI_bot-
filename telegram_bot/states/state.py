from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    get_username = State()
    set_admin = State()
    remove_admin = State()


class RemoveLimitStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_day_count = State()


# Состояния для снятия средств
class WithdrawStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_card_number = State()
    waiting_for_card_type = State()


class AddGroupStates(StatesGroup):
    get_name = State()
    get_username = State()


class SetLimitStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_day_count = State()


class Video(StatesGroup):
    get_video = State()


class Photo(StatesGroup):
    get_photo = State()


class SupportStates(StatesGroup):
    text_requests = State()


class CooperationStates(StatesGroup):
    text_requests = State()


class NewsLetter(StatesGroup):
    text = State()

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database.crud import CrudUser
from telegram_bot.states.state import SetLimitStates

router = Router()


@router.callback_query(F.data == 'set_day_limit')
async def set_day_limits_function(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()

    await callback.message.answer("Введите user_id пользователя, для которого хотите установить дневной лимит:")

    await state.set_state(SetLimitStates.waiting_for_user_id)


@router.message(SetLimitStates.waiting_for_user_id)
async def get_user_id(message: Message, state: FSMContext):
    user_id = message.text.strip()

    await state.update_data(user_id=user_id)

    await message.answer("Введите новое значение дневного лимита (целое число):")
    await state.set_state(SetLimitStates.waiting_for_day_count)


@router.message(SetLimitStates.waiting_for_day_count)
async def get_day_count(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")

    try:
        day_count = int(message.text.strip())
        if day_count < 0:
            await message.answer('Введите пожалуйста неотрицательное число дней!')
            return

    except ValueError:
        await message.answer("Пожалуйста! Введите корректное число!")
        return

    crud_user = CrudUser()
    success = await crud_user.set_days_for_user(user_id, day_count)

    if success:
        await message.answer(f"Дневной лимит пользователя {user_id} установлен на {day_count} дней.")
    else:
        await message.answer(f"Не удалось установить лимит. Проверьте user_id.")

    await state.clear()

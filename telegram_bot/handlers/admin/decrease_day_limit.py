from aiogram import F, Router
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.states.state import RemoveLimitStates
from database.crud import CrudUser

router = Router()

@router.callback_query(F.data == "decrease_day_limit")
async def process_decrease_day_limit_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.answer("Введите user_id пользователя, у которого хотите уменьшить дневной лимит:")
    await state.set_state(RemoveLimitStates.waiting_for_user_id)


@router.message(RemoveLimitStates.waiting_for_user_id)
async def process_decrease_user_id(message: types.Message, state: FSMContext):
    user_id = message.text.strip()
    await state.update_data(user_id=user_id)
    await message.answer("Введите, на сколько дней уменьшить дневной лимит:")
    await state.set_state(RemoveLimitStates.waiting_for_day_count)


@router.message(RemoveLimitStates.waiting_for_day_count)
async def process_decrease_day_count(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    try:
        days_to_remove = int(message.text.strip())
        if days_to_remove <= 0:
            await message.answer("Введите положительное число дней.")
            return
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
        return

    crud_user = CrudUser()
    success = await crud_user.remove_days_for_user(user_id, days_to_remove)
    if success:
        await message.answer(f"Дневной лимит пользователя {user_id} успешно уменьшен на {days_to_remove} дней.")
    else:
        await message.answer(f"Не удалось уменьшить лимит. Проверьте user_id и текущее значение лимита.")

    await state.clear()

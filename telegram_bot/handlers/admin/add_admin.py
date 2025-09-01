from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram import Router, F

from database.crud import CrudUser
from telegram_bot.states.state import UserState

router = Router()


@router.callback_query(F.data == 'add_admin')
async def prompt_admin_user_id(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.answer("🔑 Введите ID пользователя, которому нужно выдать админку:")
    await state.set_state(UserState.set_admin)


@router.message(UserState.set_admin)
async def assign_admin_role(message: Message, state: FSMContext):
    user_id = message.text.strip()
    crud = CrudUser()

    is_set = await crud.set_admin_user(user_id)

    if is_set:
        await message.answer(f"✅ Админка успешно выдана пользователю с ID: {user_id}")
    else:
        await message.answer("❌ Человек является администратором или не удалось найти пользователя с таким ID.")

    await state.clear()

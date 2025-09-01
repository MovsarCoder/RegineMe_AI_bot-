from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram import Router, F

from database.crud import CrudUser
from telegram_bot.states.state import UserState

router = Router()


@router.callback_query(F.data == 'remove_admin')
async def prompt_remove_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.answer("🧹 Введите ID пользователя, у которого нужно забрать админку:")
    await state.set_state(UserState.remove_admin)


@router.message(UserState.remove_admin)
async def remove_admin_role(message: Message, state: FSMContext):
    user_id = message.text.strip()
    crud = CrudUser()

    is_removed = await crud.remove_admin_user(user_id)

    if is_removed:
        await message.answer(f"✅ Админка успешно снята с пользователя ID: {user_id}")
    else:
        await message.answer("❌ Человек является не администратором или не удалось найти пользователя с таким ID.")

    await state.clear()

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.crud import CrudUser
from telegram_bot.keyboard.keyboard_builder import make_row_inline_keyboards
from telegram_bot.keyboard.keyboards import admin_keyboard
from telegram_bot.states.state import UserState

router = Router()


@router.callback_query(F.data == 'get_user_id_by_username')
async def get_user_id_by_username(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # Закрываем "часики" в Telegram UI
    await callback.message.answer("Пожалуйста, отправьте USERNAME без символа '@'.")
    await state.set_state(UserState.get_username)


@router.message(UserState.get_username)
async def send_user_id_by_username(message: Message, state: FSMContext):
    username = message.text.strip()

    # Проверка на корректность username (только буквы, цифры и подчеркивания)
    if not username.isalnum() and "_" not in username:
        await message.answer("⚠️ Неверный формат username! Используйте только буквы, цифры и подчеркивания.")
        return

    crud = CrudUser()

    try:
        user_id = await crud.get_user_id_by_username(username)

    except Exception as e:
        await message.answer(f"❌ Ошибка при поиске пользователя. Попробуйте позже. \n {e}")
        await state.clear()
        return

    if user_id:
        await message.answer(f"🔎 Результат поиска:\n\nUsername: <b>@{username}</b>\nUser ID: <code>{user_id}</code>")
    else:
        await message.answer("❌ Пользователь с таким username не найден!",
                             reply_markup=make_row_inline_keyboards(admin_keyboard))

    await state.clear()

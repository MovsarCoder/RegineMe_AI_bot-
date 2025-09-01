from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from database.crud import CrudGroup
from telegram_bot.keyboard.keyboard_builder import make_row_inline_keyboards
from telegram_bot.keyboard.keyboards import admin_keyboard
from telegram_bot.states.state import AddGroupStates
import re

router = Router()

# Регулярное выражение для валидации username
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{5,32}$")


@router.callback_query(F.data == 'add_group_to_subscription')
async def ask_group_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "📝 Введите <b>название группы</b>, которое будет отображаться на кнопке:",
        parse_mode="HTML"
    )
    await state.set_state(AddGroupStates.get_name)


@router.message(AddGroupStates.get_name)
async def ask_group_username(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("⚠️ Название не может быть пустым. Попробуйте снова.")
        return

    await state.update_data(name_group=name)
    await message.answer("🔗 Отлично! Теперь введите <b>username группы</b> (без @):")
    await state.set_state(AddGroupStates.get_username)


@router.message(AddGroupStates.get_username)
async def save_group(message: Message, state: FSMContext):
    username = message.text.strip()

    if not USERNAME_REGEX.fullmatch(username):
        await message.answer("❌ Неверный формат username. Убедитесь, что он состоит из латиницы, цифр или подчёркиваний и содержит от 5 до 32 символов.")
        return

    data = await state.get_data()
    group_name = data.get("name_group")

    crud = CrudGroup()
    added = await crud.add_group(group_name=group_name, group_username=username)

    if added:
        await message.answer(f"✅ Группа <b>{group_name}</b> (@{username}) успешно добавлена!", )
    else:
        await message.answer("⚠️ Ошибка при добавлении группы. Возможно, она уже существует или возникла проблема с базой данных.")

    await state.clear()
    await message.answer(
        "📋 Возврат в главное меню. Выберите следующее действие:",
        reply_markup=make_row_inline_keyboards(admin_keyboard)
    )

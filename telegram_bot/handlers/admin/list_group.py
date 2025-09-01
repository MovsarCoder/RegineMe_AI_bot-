from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from database.crud import CrudGroup
from telegram_bot.keyboard.keyboard_builder import make_row_inline_keyboards
from telegram_bot.keyboard.keyboards import admin_keyboard

router = Router()


@router.callback_query(F.data == 'list_group')
async def list_group(callback: CallbackQuery):
    crud = CrudGroup()
    groups = await crud.get_all_groups()

    if not groups:
        await callback.message.edit_text("⚠️ <b>Нет добавленных групп.</b>")
        return

    keyboard = []

    for group in groups:
        if group.group_username:  # Защита от пустых username
            button = InlineKeyboardButton(
                text=f"🔹 {group.group_name}",
                url=f"https://t.me/{group.group_username}"  # URL-кнопка вместо callback
            )
            keyboard.append([button])

    keyboard.append([
        InlineKeyboardButton(text="⏪ Назад", callback_data="cancel_list_group")
    ])
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.message.edit_text(text="📋 <b>Список всех групп, на которые нужно подписаться:</b>", reply_markup=reply_markup)


@router.callback_query(F.data == 'cancel_list_group')
async def return_admin_kb(callback: CallbackQuery):
    await callback.message.edit_text("📋 <b>Возврат в меню. Выберите следующее действие:</b>",
                                     reply_markup=make_row_inline_keyboards(admin_keyboard), )

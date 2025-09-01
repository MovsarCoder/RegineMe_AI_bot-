from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.crud import CrudUser
from telegram_bot.states.state import NewsLetter
from telegram_bot.keyboard.keyboards import cancel_newsletter, admin_keyboard
from telegram_bot.keyboard.keyboard_builder import make_row_inline_keyboards

router = Router()


@router.callback_query(F.data == "broadcast_message")
async def handle_broadcast_button(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_text(
        "📨 <b>Рассылка пользователям</b>\n\n"
        "Пожалуйста, введите текст или отправьте медиафайл (фото, видео, документ), который будет отправлен всем пользователям.",
        reply_markup=make_row_inline_keyboards(cancel_newsletter),
    )
    await state.set_state(NewsLetter.text)


@router.message(NewsLetter.text, F.content_type.in_({"text", "photo", "video", "document"}))
async def send_broadcast(message: Message, state: FSMContext):
    users = await CrudUser().get_all_telegram_ids()

    if not users:
        await message.answer("⚠️ Нет зарегистрированных пользователей для рассылки.")
        await state.clear()
        return

    await message.answer(f"👥 Начинаю рассылку для <b>{len(users)}</b> пользователей...")

    success = 0
    failed = 0
    failed_users = []

    for user_id in users:
        try:
            if message.text:
                await message.bot.send_message(chat_id=user_id, text=message.text)
            elif message.photo:
                await message.bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption or "")
            elif message.video:
                await message.bot.send_video(chat_id=user_id, video=message.video.file_id, caption=message.caption or "")
            elif message.document:
                await message.bot.send_document(chat_id=user_id, document=message.document.file_id, caption=message.caption or "")
            success += 1
        except Exception as e:
            failed += 1
            failed_users.append(str(user_id))
            continue

    text_result = (
        f"✅ Рассылка завершена!\n\n"
        f"👤 Получателей всего: {len(users)}\n"
        f"📬 Успешно отправлено: {success}\n"
        f"⚠️ Ошибок: {failed}"
    )

    if failed_users:
        text_result += f"\n\n🚫 Не удалось доставить:\n" + "\n".join(failed_users[:10])
        if len(failed_users) > 10:
            text_result += f"\n...и ещё {len(failed_users) - 10}."

    await message.answer(text_result, reply_markup=make_row_inline_keyboards(admin_keyboard))
    await state.clear()


@router.callback_query(F.data == 'cancel_newsletter')
async def cancel_sending_photo(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Рассылка отменена. Возвращение к админ панели.", reply_markup=make_row_inline_keyboards(admin_keyboard))
    await callback.answer()

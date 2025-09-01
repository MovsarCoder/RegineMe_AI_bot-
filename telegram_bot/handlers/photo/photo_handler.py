from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, CallbackQuery

from telegram_bot.keyboard.keyboard_builder import make_row_inline_keyboards
from telegram_bot.keyboard.keyboards import back_photo
from telegram_bot.states.state import Photo
from telegram_bot.utils.file_saver import save_file_from_message
from telegram_bot.services.photo_tools import enhance_photo
from database.crud import CrudUser

router = Router()


@router.message(F.text.startswith("🖼️ Улучшить фото — повышение резкости и детализации"))
async def handle_photo_improvement_start(message: Message, state: FSMContext):
    await state.clear()

    crud_user = CrudUser()
    user = await crud_user.get_user_by_id(message.from_user.id)

    now = datetime.now()
    has_active_subscription = any(
        sub.expires_at > now for sub in user.subscriptions
    )

    if not has_active_subscription:
        day_count = user.day_count or 0
        if day_count <= 0:
            await message.answer(
                "⚠️ У вас закончились дневные лимиты на улучшение фотографий.\n\n"
                "📆 Ежедневно доступно 5 бесплатных улучшений. "
                "Вы можете попробовать снова завтра.\n\n"
                "🚀 Хотите безлимит? Оформите подписку по команде <b>/subscriptions</b>."
            )
            return

    await message.answer(
        "📷 <b>Пожалуйста, отправьте фотографию</b>, которую вы хотите улучшить.\n\n"
        "⚠️ <i>Рекомендуем отправлять как файл для максимального качества</i>.",
        reply_markup=make_row_inline_keyboards(back_photo)
    )
    await state.set_state(Photo.get_photo)


@router.message(Photo.get_photo, F.photo)
async def handle_photo_received(message: Message, state: FSMContext, bot: Bot):
    crud_user = CrudUser()
    await crud_user.decrease_day_count(message.from_user.id)

    get_photo_message = await message.answer("📥 Получаю фото...")

    input_path = await save_file_from_message(message, bot)

    improvement_photo_message = await message.answer("🔧 Улучшаю изображение, это займет несколько секунд...")

    output_path = await enhance_photo(input_path)

    # Отправим оригинал
    with open(input_path, "rb") as original_file:
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=BufferedInputFile(original_file.read(), filename="original.jpg"),
            caption="🖼️ <b>До улучшения</b>",
        )

    # Отправим улучшенную
    with open(output_path, "rb") as enhanced_file:
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=BufferedInputFile(enhanced_file.read(), filename="enhanced.jpg"),
            caption="✨ <b>После улучшения</b>",
        )

    try:
        from telegram_bot.utils.file_cleanup import remove_files_quietly
        remove_files_quietly(input_path, output_path)
        await get_photo_message.delete()
        await improvement_photo_message.delete()
    except Exception as e:
        print(f"❌ Ошибка при удалении файлов: {e}")

    await state.clear()


@router.message(Photo.get_photo)
async def handle_invalid_content_type(message: Message, state: FSMContext):
    await message.answer(
        "⚠️ Пожалуйста, отправьте именно фотографию!",
        reply_markup=make_row_inline_keyboards(back_photo)
    )
    await state.set_state(Photo.get_photo)


@router.callback_query(F.data == 'cancel_photo')
async def cancel_sending_photo(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Заявка на улучшение фотографии была отменена.")
    await callback.answer()

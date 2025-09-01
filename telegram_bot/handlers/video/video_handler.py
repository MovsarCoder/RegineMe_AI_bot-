from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, CallbackQuery

from telegram_bot.keyboard.keyboard_builder import make_row_inline_keyboards
from telegram_bot.keyboard.keyboards import back_video
from telegram_bot.states.state import Video
from telegram_bot.services.video_tools import enhance_video
from telegram_bot.utils.file_saver import save_file_from_message
from database.crud import CrudUser

router = Router()


@router.message(F.text.startswith("🎬 Улучшить видео — стабилизация и повышение качества"))
async def handle_video_improvement_start(message: Message, state: FSMContext):
    await state.clear()

    crud_user = CrudUser()
    user = await crud_user.get_user_by_id(message.from_user.id)

    now = datetime.now()
    has_active_subscription = any(
        sub.is_active and sub.expires_at > now
        for sub in user.subscriptions
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
        "📷 <b>Пожалуйста, отправьте видео</b>, которое вы хотите улучшить.\n\n"
        "⚠️ <i>Рекомендуем отправлять как файл для максимального качества</i>.",
        reply_markup=make_row_inline_keyboards(back_video)
    )

    await state.set_state(Video.get_video)


@router.message(Video.get_video, F.video)
async def handle_video_received(message: Message, state: FSMContext, bot: Bot):
    get_video_message = await message.answer("📥 Получаю видео...")

    input_path = await save_file_from_message(message, bot)

    improvement_video_message = await message.answer("🔧 Улучшаю видео, это займет несколько секунд...")

    output_path = await enhance_video(input_path)

    # Отправим оригинал
    with open(input_path, "rb") as original_file:
        await bot.send_video(
            chat_id=message.from_user.id,
            video=BufferedInputFile(original_file.read(), filename="original.mp4"),
            caption="🎬 <b>До улучшения</b>",
        )

    # Отправим улучшенную
    with open(output_path, "rb") as enhanced_file:
        await bot.send_video(
            chat_id=message.from_user.id,
            video=BufferedInputFile(enhanced_file.read(), filename="enhanced.mp4"),
            caption="✨ <b>После улучшения</b>",
        )

    try:
        from telegram_bot.utils.file_cleanup import remove_files_quietly
        remove_files_quietly(input_path, output_path)
        await get_video_message.delete()
        await improvement_video_message.delete()
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")

    await state.clear()


# Когда отправляем что-то кроме видео
@router.message(Video.get_video)
async def handle_invalid_content_type(message: Message, state: FSMContext):
    await message.answer(
        "⚠️ Пожалуйста, отправьте именно видео!",
        reply_markup=make_row_inline_keyboards(back_video)
    )

    await state.set_state(Video.get_video)


# Отмена отправки видео
@router.callback_query(F.data == 'cancel_video')
async def cancel_sending_video(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Заявка на улучшение видео была отменена.")
    await callback.answer()

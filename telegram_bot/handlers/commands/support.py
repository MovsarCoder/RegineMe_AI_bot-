from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from telegram_bot.keyboard.keyboard_builder import make_row_inline_keyboards
from telegram_bot.states.state import SupportStates
from telegram_bot.keyboard.keyboards import cancel_support
from database.crud import CrudSupport

router = Router()


@router.message(F.text.startswith("🛠 Техническая поддержка — вопросы и проблемы"))
@router.message(Command('support'))
async def start_support_request(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "🛠 Пожалуйста, опишите вашу проблему или задайте вопрос.\n"
        "Наша команда поддержки рассмотрит заявку и ответит вам в ближайшее время.",
        reply_markup=make_row_inline_keyboards(cancel_support)
    )

    await state.set_state(SupportStates.text_requests)


@router.message(SupportStates.text_requests, F.text)
async def receive_support_text(message: Message, state: FSMContext):
    text = message.text
    create_request = await CrudSupport().create_request(
        message.from_user.id,
        message.from_user.username,
        text
    )

    if create_request:
        await message.answer("✅ Ваша заявка принята!\n"
                             "Мы свяжемся с вами в ближайшее время.")
        await state.clear()


@router.callback_query(F.data == 'cancel_support')
async def cancel_support_request(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Заявка в техническую поддержку была отменена.")
    await callback.answer()

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from telegram_bot.keyboard.keyboard_builder import make_row_inline_keyboards
from telegram_bot.states.state import CooperationStates
from telegram_bot.keyboard.keyboards import cancel_cooperation
from database.crud import CrudCooperation

router = Router()


@router.message(F.text.startswith("🤝 Сотрудничество — партнерские программы и предложения"))
@router.message(Command('cooperation'))
async def start_cooperation_application(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "📩 Пожалуйста, опишите ваше предложение по сотрудничеству.\n"
        "Мы внимательно рассмотрим каждую заявку. После отправки вам ответят в ближайшее время.",
        reply_markup=make_row_inline_keyboards(cancel_cooperation)
    )

    await state.set_state(CooperationStates.text_requests)


@router.message(CooperationStates.text_requests, F.text)
async def receive_cooperation_text(message: Message, state: FSMContext):
    get_text = message.text
    create_requests = await CrudCooperation().create_request(
        message.from_user.id,
        message.from_user.username,
        get_text
    )

    if create_requests:
        await message.answer("✅ Спасибо за ваше обращение!\n"
                             "Ваша заявка успешно отправлена. Мы свяжемся с вами в ближайшее время.")
        await state.clear()


@router.callback_query(F.data == 'cancel_cooperation')
async def cancel_cooperation_request(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Заявка на сотрудничество была отменена.")
    await callback.answer()

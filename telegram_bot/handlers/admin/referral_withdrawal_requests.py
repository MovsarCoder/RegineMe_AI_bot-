from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.crud import CrudWithdrawal
from telegram_bot.keyboard.keyboard_builder import make_tasks_inline_keyboard, make_row_inline_keyboards
from telegram_bot.keyboard.keyboards import admin_keyboard, get_withdrawal_action_buttons

router = Router()


@router.callback_query(F.data == "referral_withdrawal_requests")
async def show_withdrawal_requests(callback: CallbackQuery):
    await callback.answer()
    crud = CrudWithdrawal()
    requests = await crud.get_all_withdrawal_requests()

    if not requests:
        await callback.message.edit_text(
            "<b>❌ Пока что нет новых заявок на вывод средств (рефералы).</b>",
            reply_markup=make_row_inline_keyboards(admin_keyboard)
        )
        return

    await callback.message.edit_text(
        '📋 <b>Список заявок на вывод средств (рефералы):</b>',
        reply_markup=make_tasks_inline_keyboard(tasks=requests, callback_data_name="withdrawal")
    )


@router.callback_query(F.data.startswith("withdrawal_"))
async def handle_withdrawal_request(callback: CallbackQuery):
    await callback.answer()
    request_id = callback.data.removeprefix("withdrawal_")

    crud = CrudWithdrawal()
    request = await crud.get_withdrawal_by_id(int(request_id))

    if not request:
        await callback.message.edit_text("❌ Заявка не найдена или была удалена.")
        return

    response = (
        f"<b>Заявка на вывод #{request.id}</b>\n"
        f"👤 Пользователь: @{request.username} (ID: {request.telegram_id})\n"
        f"💰 Сумма: <b>{request.amount:.2f} ₽</b>\n"
        f"💳 Карта: {request.card_type} {request.card_number}\n"
        f"🕒 Создана: {request.request_created_at}"
    )

    await callback.message.edit_text(
        response,
        reply_markup=make_row_inline_keyboards(get_withdrawal_action_buttons(int(request_id)))
    )


@router.callback_query(F.data.startswith("cancel_withdrawal_request_"))
async def cancel_withdrawal_request(callback: CallbackQuery):
    request_id = int(callback.data.removeprefix("cancel_withdrawal_request_"))
    await callback.answer()

    crud = CrudWithdrawal()
    request = await crud.get_withdrawal_by_id(request_id)
    if not request:
        await callback.message.edit_text("❌ Заявка уже была удалена.")
        return

    await crud.cancel_request(request_id)
    await callback.message.edit_text(f"❌ Заявка #{request_id} отклонена и удалена из списка.")
    await callback.answer("Заявка успешно отклонена.")

    # Уведомляем пользователя
    await callback.bot.send_message(
        chat_id=request.telegram_id,
        text="Ваш запрос на вывод средств, к сожалению, отклонён. Если у вас есть вопросы, свяжитесь с поддержкой."
    )


@router.callback_query(F.data.startswith("accept_withdrawal_"))
async def accept_withdrawal_request(callback: CallbackQuery):
    request_id = int(callback.data.removeprefix("accept_withdrawal_request_"))
    await callback.answer()

    crud = CrudWithdrawal()
    request = await crud.get_withdrawal_by_id(request_id)
    if not request:
        await callback.message.edit_text("❌ Заявка уже была обработана или удалена.")
        return

    await crud.accept_request(request_id)
    # Обновляем список после одобрения
    requests = await crud.get_all_withdrawal_requests()

    response = (
        f"✅ Заявка #{request_id} успешно одобрена и обработана.\n\n"
        f"<b>Заявка #{request_id}</b>\n"
        f"👤 Пользователь: @{request.username} (ID: {request.telegram_id})\n"
        f"💰 Сумма: <b>{request.amount:.2f} ₽</b>\n"
        f"💳 Карта: {request.card_type} {request.card_number}\n"
        f"🕒 Создана: {request.request_created_at}"
    )

    # Уведомляем пользователя
    await callback.bot.send_message(
        chat_id=request.telegram_id,
        text="Ваш запрос на вывод средств одобрен. Ожидайте зачисления на карту."
    )

    if requests:
        await callback.message.edit_text(
            response,
            reply_markup=make_tasks_inline_keyboard(tasks=requests, callback_data_name="withdrawal")
        )
    else:
        await callback.message.edit_text(
            "📋 Все заявки обработаны.",
            reply_markup=make_row_inline_keyboards(admin_keyboard)
        )

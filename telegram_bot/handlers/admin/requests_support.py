from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.crud import CrudSupport
from telegram_bot.keyboard.keyboard_builder import make_tasks_inline_keyboard, make_row_inline_keyboards
from telegram_bot.keyboard.keyboards import get_cancel_support_buttons, admin_keyboard

router = Router()


@router.callback_query(F.data == 'show_requests_support')
async def show_requests_support(callback: CallbackQuery):
    await callback.answer()
    tasks = await CrudSupport().get_all_requests()

    if tasks:
        await callback.message.edit_text(
            '📨 <b>Список входящих запросов в поддержку:</b>',
            reply_markup=make_tasks_inline_keyboard(
                tasks=tasks,
                callback_data_name='support_task'
            )
        )
    else:
        await callback.message.edit_text("<b>❌ Нет никаких запросов!</b>")


@router.callback_query(F.data.startswith("support_task_"))
async def handle_support_request(callback: CallbackQuery):
    request_id = int(callback.data.removeprefix("support_task_"))

    task = await CrudSupport().get_requests_by_id(request_id)

    response = (
        f"<b>Запрос #{task.id}</b>\n"
        f"👤 Пользователь: @{task.username} (ID: {task.telegram_id})\n\n"
        f"📩 Сообщение:\n{task.text_requests}\n\n"
        f"🕒 Дата: {task.request_created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await callback.message.edit_text(
        response,
        reply_markup=make_row_inline_keyboards(get_cancel_support_buttons(request_id))
    )


@router.callback_query(F.data.startswith("deleted_support_requests_"))
async def delete_support_request(callback: CallbackQuery):
    request_id = int(callback.data.removeprefix("deleted_support_requests_"))
    await callback.answer()

    crud = CrudSupport()
    task = await crud.get_requests_by_id(request_id)

    if task:
        await crud.cancel_request(request_id)
        await callback.message.edit_text(f"❌ Запрос #{request_id} удалён.")

        await callback.bot.send_message(
            chat_id=task.telegram_id,
            text='Ваш запрос в поддержку был обработан. Спасибо за обращение!'
        )
    else:
        await callback.message.answer("❌ Запрос не найден или уже удалён.", reply_markup=make_row_inline_keyboards(admin_keyboard))


@router.callback_query(F.data == 'show_requests_support_2')
async def show_requests_support_2(callback: CallbackQuery):
    await callback.answer()
    tasks = await CrudSupport().get_all_requests()

    if tasks:
        await callback.message.edit_text(
            '📨 <b>Список входящих запросов в поддержку:</b>',
            reply_markup=make_tasks_inline_keyboard(
                tasks=tasks,
                callback_data_name='support_task'
            )
        )
    else:
        await callback.message.edit_text("<b>❌ Нет никаких запросов!</b>", reply_markup=make_row_inline_keyboards(admin_keyboard))

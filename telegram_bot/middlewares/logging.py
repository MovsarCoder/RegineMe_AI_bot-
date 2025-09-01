import traceback
import logging

from datetime import datetime
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import Update
from database.crud import CrudUser


class ErrorMiddleware(BaseMiddleware):
    """
    Middleware для глобального перехвата ошибок в Aiogram 3.
    При возникновении исключений:
    - логирует ошибку в консоль;
    - отправляет уведомление админу;
    - записывает информацию в базу данных.
    """

    async def __call__(
            self,
            handler: Callable[[Update, dict], Awaitable[Any]],
            event: Update,
            data: dict
    ) -> Any:
        try:
            return await handler(event, data)

        except Exception as e:
            bot: Bot = data.get("bot")
            tb = traceback.format_exc()
            logging.error(f"Ошибка при обработке события: {tb}")

            # Безопасно определяем Telegram ID
            telegram_id = None
            telegram_name = None
            if event.message:
                telegram_id = event.message.from_user.id
                telegram_name = event.message.from_user.username
            elif event.callback_query:
                telegram_id = event.callback_query.from_user.id
                telegram_name = event.callback_query.from_user.username
            elif event.inline_query:
                telegram_id = event.inline_query.from_user.id
                telegram_name = event.inline_query.from_user.username

            # Получаем текущую дату и время и форматируем в нужный формат
            formatted_time = datetime.now().strftime("%H:%M %d.%m.%Y")
            # Список администраторов
            ADMIN_IDS = await CrudUser().check_is_admin_user()

            # Отправка админу
            if bot:
                try:
                    for tg_id in ADMIN_IDS:
                        await bot.send_message(
                            chat_id=tg_id,
                            text=f"❌ Ошибка!"
                                 f"\nТелеграм ID: {telegram_id}"
                                 f"\nТелеграм Ник: @{telegram_name}"
                                 f"\nВремя: {formatted_time}"
                                 f"\n\n<b>{type(e).__name__}:</b> {e}\n\n<pre>{tb[-700:-1]}</pre>",
                            parse_mode="HTML"
                        )
                except Exception as ex:
                    print(f'Ошибка: {ex}')

from aiogram.types import TelegramObject, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any

from database.crud import CrudGroup, CrudUser


class SubscriptionMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.crud_group = CrudGroup()
        self.crud_user = CrudUser()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id
            bot = data['bot']

            # Проверяем подписку на все группы (включая админов)
            groups = await self.crud_group.get_all_groups()
            not_subscribed = []

            # Если пользователь является администратором, то проверка на подписки не будет.
            if event.from_user.id in await self.crud_user.check_is_admin_user():
                return await handler(event, data)

            for group in groups:
                try:
                    member = await bot.get_chat_member(chat_id=f"@{group.group_username}", user_id=user_id)
                    if member.status not in ['member', 'creator', 'administrator']:
                        not_subscribed.append(group)
                except Exception as e:
                    print(f"[Middleware Error] {e}")
                    continue

            if not_subscribed:
                keyboard = [
                    [InlineKeyboardButton(text=g.group_name, url=f"https://t.me/{g.group_username}")]
                    for g in not_subscribed
                ]

                await event.answer(
                    "📢 Чтобы продолжить пользоваться ботом, подпишитесь на все каналы:",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
                )
                return  # Прерываем цепочку обработчиков

            return await handler(event, data)

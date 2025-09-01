from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.crud import CrudUser
from telegram_bot.keyboard.keyboard_builder import make_row_inline_keyboards
from telegram_bot.keyboard.keyboards import referral_system

router = Router()


@router.message(Command("profile"))
async def profile_command(message: Message):
    telegram_id = message.from_user.id
    crud = CrudUser()
    user = await crud.get_user_by_id(telegram_id)

    if not user:
        await message.answer("🚫 Пользователь не найден в базе данных.")
        return

    # Данные пользователя
    username = f"@{user.username}" if user.username else "—"
    firstname = user.firstname or "—"
    lastname = user.lastname or "—"
    platform = user.platform or "—"
    day_count = user.day_count if user.day_count else 0
    reg_date = user.registration_date.strftime("%d.%m.%Y %H:%M")
    is_active = "🟢 Активен" if user.is_active else "🔴 Неактивен"
    is_admin = "✅ Да" if user.is_admin else "❌ Нет"

    # Подписка
    active_sub = next((s for s in user.subscriptions), None)
    if active_sub:
        plan_name = {
            'ONE_MONTH': 'Месячный',
            'THREE_MONTH': '3-х месячный',
            'SIX_MONTH': 'Полугодовой'
        }.get(active_sub.plan_name, active_sub.plan_name)

        sub_text = (
            f"<b>💳 Подписка</b>\n"
            f"├ 💼 Тариф: <code>{plan_name}</code>\n"
            f"├ 📅 Куплена: {active_sub.purchased_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"└ ⏳ Истекает: {active_sub.expires_at.strftime('%d.%m.%Y %H:%M')}\n"
        )
    else:
        sub_text = (
            "<b>💳 Подписка</b>\n"
            "└ 📭 Нет активной подписки\n"
        )

    # Подсчет активных обращений
    active_support_requests = sum(1 for r in user.support_request)
    active_coop_requests = sum(1 for r in user.cooperation_request)

    requests_text = (
        f"<b>📨 Активные обращения</b>\n"
        f"├ 🤝 Сотрудничество: <code>{active_coop_requests}</code>\n"
        f"└ 🆘 Поддержка: <code>{active_support_requests}</code>\n"
    )

    # Профиль
    profile_text = (
        f"<b>👤 Профиль пользователя</b> {username}\n"
        f"<code>{'━' * 30}</code>\n"
        f"<b>🧾 Основное</b>\n"
        f"├ 🆔 ID: <code>{user.id}</code>\n"
        f"├ 📱 Telegram ID: <code>{user.telegram_id}</code>\n"
        f"├ 👤 Username: {username}\n"
        f"├ 🧑 Имя: {firstname}\n"
        f"├ 👨‍👩‍👧 Фамилия: {lastname}\n"
        f"├ 📲 Платформа: {platform}\n"
        f"├ ⏳ Запросы в день: <code>{day_count}</code>\n"
        f"├ 🗓 Зарегистрирован: {reg_date}\n"
        f"├ 🔐 Статус: {is_active}\n"
        f"└ 🛡 Админ: {is_admin}\n"
        f"<code>{'━' * 30}</code>\n"
        f"{sub_text}"
        f"<code>{'━' * 30}</code>\n"
        f"{requests_text}"
        f"<code>{'━' * 30}</code>"
    )

    await message.answer(profile_text, reply_markup=make_row_inline_keyboards(referral_system))

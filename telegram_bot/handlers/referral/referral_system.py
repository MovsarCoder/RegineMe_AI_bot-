from aiogram import Router, F
from aiogram.types import CallbackQuery

from telegram_bot.config.settings import GetBotName
from database.crud import CrudUser
from telegram_bot.keyboard.keyboard_builder import make_row_inline_keyboards
from telegram_bot.keyboard.keyboards import referral_menu_keyboard

router = Router()
BOT_USERNAME = GetBotName.BOT_USERNAME


def get_referral_link(telegram_id: int, bot_username: str) -> str:
    """Генерирует реферальную ссылку для пользователя."""
    return f"https://t.me/{bot_username}?start=ref_{telegram_id}"


@router.callback_query(F.data == 'referral_system')
async def referral_system_info(callback: CallbackQuery):
    await callback.answer()

    crud = CrudUser()
    user = await crud.get_user_with_refs(callback.from_user.id)

    if not user:
        await callback.message.edit_text("❌ Пользователь не найден.")
        return

    referred_users = user.referred_users or []
    referred_count = len(referred_users)
    referral_balance = user.referral_balance or 0
    paid_referred_count = sum(
        1 for u in referred_users if any(s for s in u.subscriptions)
    )

    message = (
        f"🎁 Ваша реферальная ссылка:\n"
        f"<code>{get_referral_link(callback.from_user.id, BOT_USERNAME)}</code>\n\n"
        f"👥 Приглашено друзей: {referred_count}\n"
        f"💰 Получено денег: {referral_balance} ₽\n"
        f"✅ Приглашённых, которые купили подписку: {paid_referred_count}\n\n"
        f"📤 Поделитесь ссылкой с друзьями, чтобы получить бонус!"
    )

    await callback.message.edit_text(
        text=f"Информация про реферальную систему:\n{message}",
        reply_markup=make_row_inline_keyboards(referral_menu_keyboard)
    )

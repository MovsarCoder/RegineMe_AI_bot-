import uuid
from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

from database.crud import CrudUser, CrudSubscription
from database.models import PlanType
from telegram_bot.config.settings import GetBotName, YooKassaInfo
from yookassa import Payment, Configuration

from telegram_bot.keyboard.keyboard_builder import make_row_inline_keyboards, make_tasks_inline_keyboard
from telegram_bot.keyboard.keyboards import subscription_keyboard

router = Router()
Configuration.account_id = YooKassaInfo.SHOP_ID
Configuration.secret_key = YooKassaInfo.PAY_TOKEN

prices = {
    PlanType.ONE_MONTH: {"label": "1 месяц – 190 ₽", "days": 30},
    PlanType.THREE_MONTH: {"label": "3 месяца – 490 ₽", "days": 90},
    PlanType.SIX_MONTH: {"label": "6 месяцев – 890 ₽", "days": 180}
}


async def check_payment_status(payment_id: str) -> bool:
    payment = Payment.find_one(payment_id)
    return payment.status == "succeeded" and payment.paid


@router.message(F.text.startswith("💎 Подписка — доступ к PRO-функциям"))
@router.message(Command("subscription"))
async def show_subscription_plans(message: Message):
    await message.answer("🔔 Выберите подписку:",
                         reply_markup=make_row_inline_keyboards(subscription_keyboard(prices)))


@router.callback_query(F.data.in_([plan.name for plan in PlanType]))
async def handle_subscription_choice(callback: CallbackQuery):
    plan = PlanType(callback.data)
    plan_info = prices[plan]

    user_crud = CrudUser()
    user = await user_crud.get_user_by_id(telegram_id=callback.from_user.id)
    if not user:
        await callback.message.answer("❌ Вы не зарегистрированы.")
        await callback.answer()
        return

    payment = Payment.create({
        "amount": {
            "value": str(plan_info["days"] // 30 * 190),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://t.me/{GetBotName.BOT_USERNAME}"
        },
        "capture":
            True,
        "description":
            f"Подписка {plan_info['label']} для {callback.from_user.username}"
    }, uuid.uuid4())

    cb_data = f"check_payment:{payment.id}:{plan.name}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", url=payment.confirmation.confirmation_url)],
        [InlineKeyboardButton(text="✅ Проверить оплату", callback_data=cb_data)]
    ])

    await callback.message.edit_text(f"💳 Подписка <b>{plan_info['label']}</b>", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("check_payment:"))
async def check_payment(callback: CallbackQuery):
    _, payment_id, plan_name = callback.data.split(":")
    plan_info = prices[PlanType(plan_name)]

    user_crud = CrudUser()
    subscription_crud = CrudSubscription()
    user = await user_crud.get_user_by_id(callback.from_user.id)
    if not user:
        await callback.message.edit_text("❌ Пользователь не найден.")
        await callback.answer()
        return

    if not await check_payment_status(payment_id):
        await callback.message.answer("❌ Оплата ещё не прошла.")
        await callback.answer()
        return

    now = datetime.now(timezone(timedelta(hours=3)))
    expires_at = now + timedelta(days=plan_info["days"] + 1)
    subscription = await subscription_crud.add_subscription(
        user_id=user.id,
        plan_name=plan_name,
        expires_at=expires_at,
        payment_id=payment_id
    )

    await callback.message.edit_text(
        f"🚀 PRO-подписка <b>{plan_info['label']}</b> активирована!\n"
        f"⏳ Срок действия до: <code>{subscription.expires_at.strftime('%Y-%m-%d %H:%M')}</code>\n\n"
        f"📸 Все лимиты на улучшение фото и видео сняты!\n"
        f"✨ Попробуйте новые возможности, которых нет у обычных пользователей!"
    )
    await callback.answer()

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database.crud import CrudUser, CrudWithdrawal
from telegram_bot.states.state import WithdrawStates

router = Router()


@router.callback_query(F.data == 'referral_withdraw')
async def start_withdraw(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("💸 Введите сумму, которую хотите снять с реферального баланса:")
    await state.set_state(WithdrawStates.waiting_for_amount)
    await callback.answer()


@router.message(WithdrawStates.waiting_for_amount)
async def process_withdraw_amount(message: Message, state: FSMContext):
    crud_user = CrudUser()

    try:
        amount = float(message.text.replace(',', '.'))

        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0. Попробуйте снова:")
            return

        user = await crud_user.get_user_by_id(message.from_user.id)
        if not user:
            await message.answer("⚠️ Пользователь не найден.")
            await state.clear()
            return

        if amount > user.referral_balance:
            await message.answer(f"❌ Недостаточно средств. Ваш баланс: <b>{user.referral_balance}</b>")
            return

        await state.update_data(amount=amount)
        await message.answer("💳 Укажите тип карты (например: ОЗОН-Банк, СберБанк, Т-БАНК, Мир):")
        await state.set_state(WithdrawStates.waiting_for_card_type)

    except ValueError:
        await message.answer("❌ Введите корректное число. Пример: <b>150.75</b>")


@router.message(WithdrawStates.waiting_for_card_type)
async def process_card_type(message: Message, state: FSMContext):
    card_type = message.text.strip()

    if not card_type or len(card_type) < 3:
        await message.answer("❌ Пожалуйста, укажите корректный тип карты.")
        return

    await state.update_data(card_type=card_type)
    await message.answer("💳 Введите номер карты (16 цифр):")
    await state.set_state(WithdrawStates.waiting_for_card_number)


@router.message(WithdrawStates.waiting_for_card_number)
async def process_card_number(message: Message, state: FSMContext):
    card_number = message.text.strip().replace(' ', '')

    if not card_number.isdigit() or len(card_number) != 16:
        await message.answer("❌ Номер карты должен содержать 16 цифр. Попробуйте ещё раз:")
        return

    await state.update_data(card_number=card_number)
    data = await state.get_data()

    crud_user = CrudUser()
    crud_withdrawal = CrudWithdrawal()

    user = await crud_user.get_user_by_id(message.from_user.id)
    if not user:
        await message.answer("⚠️ Пользователь не найден.")
        await state.clear()
        return

    # Создаём заявку на вывод
    success = await crud_withdrawal.create_withdrawal(
        telegram_id=user.telegram_id,
        username=user.username or message.from_user.username,
        amount=data['amount'],
        card_type=data['card_type'],
        card_number=data['card_number']
    )

    if not success:
        await message.answer("❌ У вас уже есть активная заявка на вывод. Пожалуйста, дождитесь её обработки.")
    else:
        await message.answer(
            f"✅ Заявка на вывод <b>{data['amount']}</b> ₽ успешно создана!\n"
            f"💳 Карта: {data['card_type']} {data['card_number']}\n"
            f"⏳ Ожидайте подтверждения от администрации.",
        )

    await state.clear()

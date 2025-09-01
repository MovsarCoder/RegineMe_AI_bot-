from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import logging

from telegram_bot.keyboard.keyboard_builder import make_row_keyboards
from telegram_bot.keyboard.keyboards import select_type_improvement_graphics
from database.crud import CrudUser
from telegram_bot.config.settings import GetBotName

router = Router()
BOT_NAME = GetBotName.BOT_NAME

# Текст приветствия
welcome_message = f"""
<b>👋 Добро пожаловать в <u>{BOT_NAME}</u>!</b>

🎉 <b>Каждый день вы получаете 5 бесплатных улучшений!</b>  
🚀 Используйте их для обработки фото и видео с помощью нейросетей.

📌 <b>Что умеет бот?</b>
🖼️ <b>ФОТО:</b>  
↳ Увеличение разрешения (до 4K)  
↳ Удаление шумов и артефактов  
↳ Восстановление деталей лица и текстур  

🎥 <b>ВИДЕО:</b>  
↳ Повышение качества  
↳ Стабилизация  
↳ Увеличение битрейта (чётче, плавнее)

💡 <b>Как начать?</b>
1️⃣ Выберите, что хотите улучшить: <i>Фото</i> или <i>Видео</i>  
2️⃣ Отправьте файл <b>высокого качества (как файл)</b>  
3️⃣ Получите <b>AI-улучшенную</b> версию за пару секунд!

🎁 <b>Реферальная система:</b>  
Приведи друга — и получи <b>50₽</b> на баланс за каждого приглашённого!  
Твоя ссылка находится в профиле, в разделе <b>«Реферальная система»</b>.

💎 <b>Хотите больше улучшений?</b>  
Оформите подписку и получите неограниченный доступ: <b>/subscription</b>

🤝 <b>Сотрудничество</b>  
Хотите стать партнером или предложить совместный проект?  
Нажмите кнопку ниже и заполните форму — мы обязательно с вами свяжемся!

🛠️ <b>Техническая поддержка</b>  
Возникли вопросы или проблемы с работой бота?  
Нажмите кнопку ниже, чтобы связаться с нашей службой поддержки.

💬 <i>Готовы преобразить свои медиафайлы? Жмите кнопку ниже!</i>
"""


def extract_referred_id(payload: str | None) -> int | None:
    """
    Извлекает telegram_id пригласившего из payload, если он есть.
    """
    if payload and payload.startswith("ref_"):
        try:
            return int(payload.split("_")[1])
        except (IndexError, ValueError):
            pass
    return None


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, command: CommandObject):
    """
    Обработка команды /start. Регистрирует пользователя, проверяет реферала.
    """
    await state.clear()

    referred_by_telegram_id = extract_referred_id(command.args)
    crud = CrudUser()

    try:
        user = await crud.add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            firstname=message.from_user.first_name,
            lastname=message.from_user.last_name,
            platform="Telegram",
            day_count=5,
            is_active=True,
            is_admin=False,
            referred_by_telegram_id=referred_by_telegram_id,
        )
        if user:
            logging.info(f"✅ Пользователь {user.telegram_id} успешно зарегистрирован.")
        else:
            logging.info(f"👤 Пользователь {message.from_user.id} уже существует.")
    except Exception as e:
        logging.error(f"❌ Ошибка при добавлении пользователя {message.from_user.id}: {e}", exc_info=True)

    await message.answer(
        text=welcome_message,
        reply_markup=make_row_keyboards(select_type_improvement_graphics),
    )

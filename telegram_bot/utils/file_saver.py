import os
from uuid import uuid4

from aiogram.types import Message
from aiogram import Bot

# Папка, в которую будут сохраняться фото
MEDIA_DIR = "media/photos"

# Создаём папку, если её ещё нет
os.makedirs(MEDIA_DIR, exist_ok=True)


async def save_file_from_message(message: Message, bot: Bot) -> str:
    if message.photo:
        file_id = message.photo[-1].file_id
        ext = ".jpg"
    elif message.video:
        file_id = message.video.file_id
        ext = ".mp4"
    else:
        raise ValueError("Unsupported media type")

    file = await bot.get_file(file_id)

    filename = f"{uuid4().hex}{ext}"
    save_path = os.path.join("media", "videos", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    await bot.download(file, save_path)
    return save_path

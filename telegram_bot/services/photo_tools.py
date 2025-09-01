import asyncio
import shutil


async def enhance_photo(input_path: str) -> str:
    # Здесь можно вставить вызов Real-ESRGAN или другой модели
    await asyncio.sleep(2)  # Эмуляция ожидания

    output_path = input_path.replace(".jpg", "_enhanced.jpg")
    shutil.copy(input_path, output_path)
    return output_path

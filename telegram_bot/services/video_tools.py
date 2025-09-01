import asyncio
import shutil


async def enhance_video(input_path: str) -> str:
    await asyncio.sleep(2)  # Имитируем обработку

    output_path = input_path.replace(".mp4", "_enhanced.mp4")
    shutil.copy(input_path, output_path)
    return output_path

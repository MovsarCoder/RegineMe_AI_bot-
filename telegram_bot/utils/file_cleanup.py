import os


def remove_files_quietly(*paths: str):
    for path in paths:
        try:
            os.remove(path)
        except Exception:
            pass  # Тихо игнорируем все ошибки (например, если файл уже удалён)

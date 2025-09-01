FROM python:3.11-slim

# Рабочая директория в контейнере
WORKDIR /app

# Скопировать все файлы проекта
COPY . .

# Установка зависимостей
RUN pip install -r requirements.txt

# Запуск main.py
CMD ["python", "main.py"]
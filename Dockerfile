#шаблон создания образа Django-приложения
FROM python:3.9-slim

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Рабочая директория
WORKDIR /app

# Зависимости
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копирование проекта
COPY . .

# Открываем порт
EXPOSE 8000

# Запуск сервера разработки
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
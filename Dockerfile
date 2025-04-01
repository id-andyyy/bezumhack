FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов проекта
COPY main.py .
COPY models.py .
COPY database.py .
COPY favicon.ico .

# Создание директории для статических файлов
RUN mkdir -p static
COPY static/* static/

# Создание директории templates
RUN mkdir -p templates

# Открываем порт
EXPOSE 8000

# Запуск приложения
CMD ["python", "main.py"]
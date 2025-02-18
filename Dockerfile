FROM python:3.12-slim

# Устанавливаем нужные системные пакеты (включая libpq-dev для PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Обновляем pip и устанавливаем Poetry
RUN pip install --upgrade pip && pip install poetry

# Создаём рабочую директорию внутри контейнера
WORKDIR /

# Копируем только файлы,
# чтобы сначала установить зависимости перед копированием остальных файлов
COPY ./pyproject.toml ./pyproject.toml
COPY ./poetry.lock ./poetry.lock
COPY ./app ./app

# Настраиваем Poetry для установки зависимостей в ту же среду, где и система
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

# Команда запуска; замените на вашу, если у вас другой скрипт или фреймворк
CMD ["python", "./app/main.py"]
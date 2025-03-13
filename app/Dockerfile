# app/Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry
# RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install
# RUN poetry install --only main --no-root --no-interaction

# Проверяем установленные пакеты (для отладки)
RUN pip list

COPY app .

CMD ["python", "main.py"]
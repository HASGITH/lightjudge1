FROM python:3.13-slim

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y g++ build-essential && \
    rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем весь проект
COPY . /app

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Старт приложения
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]

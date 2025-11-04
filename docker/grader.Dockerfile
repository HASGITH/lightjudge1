# Берём полный образ Python с уже установленными системными утилитами
FROM python:3.13

# Обновляем apt и ставим g++ и make
RUN apt-get update && \
    apt-get install -y g++ build-essential && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем весь проект
COPY . /app

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запуск приложения
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]

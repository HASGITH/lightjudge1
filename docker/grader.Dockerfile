# Базовый Python 3.13
FROM python:3.13

# Устанавливаем g++ и утилиты сборки
RUN apt-get update && apt-get install -y g++ build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]

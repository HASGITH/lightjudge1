FROM python:3.13

# Неинтерактивный режим
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
COPY . /app

# Устанавливаем g++ и зависимости Python
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential g++ \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Запускаем приложение
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]

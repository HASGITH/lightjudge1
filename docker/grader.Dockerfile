FROM python:3.13

# Неинтерактивный режим для apt
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
COPY . /app

# Обновить и установить компилятор в один шаг, с очисткой кеша
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential g++ \
 && rm -rf /var/lib/apt/lists/*

# Установить зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]

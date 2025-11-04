FROM python:3.13-slim
RUN apt-get update && apt-get install -y g++ build-essential
WORKDIR /app
COPY . /app
RUN pip install -r requiments.txt
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]

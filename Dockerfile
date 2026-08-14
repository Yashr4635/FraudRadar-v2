FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    unzip \
    curl \
    tesseract-ocr \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["sh", "-c", "reflex run --env prod --frontend-port ${PORT:-3000}"]

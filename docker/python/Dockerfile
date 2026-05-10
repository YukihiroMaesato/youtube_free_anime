FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

COPY ./python/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

USER appuser

CMD ["tail", "-f", "/dev/null"]
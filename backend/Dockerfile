FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=core_api.settings.cloud
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "core_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]

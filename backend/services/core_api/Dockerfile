FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/core_api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY shared ./shared
COPY services/core_api ./

EXPOSE 8001

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn core_api.wsgi:application --bind 0.0.0.0:8001 --workers 2 --access-logfile - --error-logfile -"]

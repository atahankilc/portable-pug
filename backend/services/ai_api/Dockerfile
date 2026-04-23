FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

COPY services/ai_api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY shared ./shared
COPY services/ai_api ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

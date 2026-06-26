FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
ARG PIP_INDEX_URL=https://pypi.org/simple
RUN pip install --no-cache-dir -i "$PIP_INDEX_URL" -r requirements.txt

COPY . .

CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8080"]
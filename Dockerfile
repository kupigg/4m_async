FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host ${UVICORN_HOST:-0.0.0.0} --port ${UVICORN_PORT:-8000} --workers ${UVICORN_WORKERS:-4} --backlog ${UVICORN_BACKLOG:-4096} --limit-concurrency ${UVICORN_LIMIT_CONCURRENCY:-10000} --timeout-keep-alive ${UVICORN_TIMEOUT_KEEP_ALIVE:-5}"]

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host ${UVICORN__HOST:-0.0.0.0} --port ${UVICORN__PORT:-8000} --workers ${UVICORN__WORKERS:-4} --backlog ${UVICORN__BACKLOG:-4096} --limit-concurrency ${UVICORN__LIMIT_CONCURRENCY:-10000} --timeout-keep-alive ${UVICORN__TIMEOUT_KEEP_ALIVE:-5}"]

# Async Cinema API

Асинхронный API онлайн-кинотеатра на FastAPI. В качестве основного хранилища используется Elasticsearch, для кеширования ответов ES-запросов используется Redis.

## 1. Запуск через Docker

### Шаг 1: подготовить переменные окружения
```bash
cp .env.example .env
```

### Шаг 2: поднять сервисы
```bash
docker compose up --build
```

### Шаг 3: открыть документацию API
- Swagger UI: `http://localhost:${TEST_API_PORT}/docs`
- OpenAPI: `http://localhost:${TEST_API_PORT}/openapi.json`

### Шаг 4: остановить сервисы
```bash
docker compose down
```

## 2. Локальный запуск без Docker

### Шаг 1: создать и активировать виртуальное окружение
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Шаг 2: установить зависимости
```bash
python -m pip install -r requirements.txt
```

### Шаг 3: подготовить окружение
```bash
cp .env.example .env
```

### Шаг 4: запустить приложение
```bash
set -a
. ./.env
set +a
uvicorn main:app --host "$UVICORN__HOST" --port "$UVICORN__PORT"
```

## 3. Тесты

### Unit-тесты

Перед запуском установите зависимости проекта:

```bash
python -m pip install -r requirements.txt
pytest -v
```

### Функциональные тесты

Функциональные тесты асинхронные и написаны на `pytest` + `aiohttp`. Тестовый compose-файл поднимает API, Elasticsearch, Redis и отдельный контейнер с тестами:

```bash
cp .env.example .env
docker compose -f tests/docker-compose.yml up --build --abort-on-container-exit tests
```

Все адреса, порты, имена индексов, docker-образы и healthcheck-настройки для тестового compose берутся из `.env`. Перед запуском можно проверить итоговую конфигурацию:

```bash
docker compose --env-file .env -f tests/docker-compose.yml config
```

После прогона можно остановить и удалить контейнеры:

```bash
docker compose -f tests/docker-compose.yml down
```

Если API, Elasticsearch и Redis уже запущены, тесты можно выполнить локально:

```bash
python -m pip install -r tests/requirements.txt
set -a
. ./.env
set +a
python -m tests.functional.utils.wait_for_services
pytest tests/functional -v
```

Основные переменные для функциональных тестов:

```bash
TEST_API__BASE_URL
TEST_API__ASGI_BASE_URL
TEST_ELASTICSEARCH__URL
TEST_ELASTICSEARCH__MOVIES_INDEX
TEST_ELASTICSEARCH__GENRES_INDEX
TEST_ELASTICSEARCH__PERSONS_INDEX
TEST_REDIS__URL
TEST_WAIT__TIMEOUT
TEST_WAIT__INTERVAL
TEST_API_PORT
TEST_ELASTICSEARCH_PORT
TEST_REDIS_PORT
```

### Все локальные pytest-тесты

```bash
pytest -v
```

## 4. Кеширование

Ответы запросов к Elasticsearch кешируются в Redis. TTL задаётся переменной:

```bash
REDIS__CACHE_TTL=300
```

## 5. Примеры запросов

Популярные фильмы:
```bash
curl "http://localhost:${TEST_API_PORT}/api/v1/films?sort=-imdb_rating&page_size=50&page_number=1"
```

Поиск фильмов:
```bash
curl "http://localhost:${TEST_API_PORT}/api/v1/films/search/?query=star&page_number=1&page_size=50"
```

Страница фильма:
```bash
curl "http://localhost:${TEST_API_PORT}/api/v1/films/<uuid>/"
```

Поиск персон:
```bash
curl "http://localhost:${TEST_API_PORT}/api/v1/persons/search/?query=captain&page_number=1&page_size=50"
```

Список персон:
```bash
curl "http://localhost:${TEST_API_PORT}/api/v1/persons/?page_number=1&page_size=50"
```

Фильмы персоны:
```bash
curl "http://localhost:${TEST_API_PORT}/api/v1/persons/<uuid>/film/?page_number=1&page_size=50"
```

Список жанров:
```bash
curl "http://localhost:${TEST_API_PORT}/api/v1/genres/"
```

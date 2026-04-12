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
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`

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
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 3. Тесты
```bash
pytest -v
```

## 4.  Примеры запросов

Популярные фильмы:
```bash
curl "http://localhost:8000/api/v1/films?sort=-imdb_rating&page_size=50&page_number=1"
```

Поиск фильмов:
```bash
curl "http://localhost:8000/api/v1/films/search/?query=star&page_number=1&page_size=50"
```

Страница фильма:
```bash
curl "http://localhost:8000/api/v1/films/<uuid>/"
```

Поиск персон:
```bash
curl "http://localhost:8000/api/v1/persons/search/?query=captain&page_number=1&page_size=50"
```

Список жанров:
```bash
curl "http://localhost:8000/api/v1/genres/"
```


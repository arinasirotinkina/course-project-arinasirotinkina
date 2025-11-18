![CI](https://github.com/<org>/<repo>/actions/workflows/ci.yml/badge.svg)

# SecDev Course Template

Стартовый шаблон для студенческого репозитория (HSE SecDev 2025).

## Быстрый старт
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
uvicorn app.main:app --reload
pre-commit install --hook-type pre-push
```

Проверить работу API http://127.0.0.1:8000/docs

## Ритуал перед PR
```bash
ruff --fix .
black .
isort .
pytest -q
pre-commit run --all-files
```

## Тесты
```bash
pytest -q
```

## CI
В репозитории настроен workflow **CI** (GitHub Actions) — required check для `main`.
Badge добавится автоматически после загрузки шаблона в GitHub.

## Контейнеры
```bash
docker build -t secdev-app .
docker run --rm -p 8000:8000 secdev-app
# или
docker compose up --build
```

## Эндпойнты
- `GET /wishes/` → `[WishResponse, ...]` — получить все желания с фильтрацией по цене (`max_price`)
- `GET /wishes/search?query=...` → `[WishResponse, ...]` — поиск желаний по названию
- `POST /wishes/` → `WishResponse` — создать новое желание
- `PUT /wishes/{wish_id}` → `WishResponse` — обновить существующее желание
- `DELETE /wishes/{wish_id}` → `{"message": "Желание удалено"}` — удалить желание
---
- `GET /health` → `{"status": "ok"}`
- `POST /items?name=...` — демо-сущность
- `GET /items/{id}`

## Формат ошибок
Все ошибки — JSON-обёртка:
```json
{
  "error": {"code": "not_found", "message": "item not found"}
}
```

См. также: `SECURITY.md`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.

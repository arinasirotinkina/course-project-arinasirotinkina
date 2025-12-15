from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from .wishes import router as wishes_router

app = FastAPI(title="Wishlist API")

app.include_router(wishes_router, prefix="/wishes", tags=["wishes"])

logger = logging.getLogger("wishlist")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)


# Middleware: security headers + cache-control
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
    response.headers.setdefault("Cache-Control", "no-cache, no-store, must-revalidate")
    response.headers.setdefault("Pragma", "no-cache")
    response.headers.setdefault("Expires", "0")
    return response


@app.get("/")
def read_root():
    return {"message": "Wishlist API is running"}


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    """Старый учебный формат с ключом 'error' (совместимость с test_errors.py)."""
    correlation_id = str(uuid4())

    safe_message = exc.message if exc.status < 500 else "internal_server_error"

    payload = {
        "error": {
            "code": exc.code,
            "message": safe_message,
        },
        "correlation_id": correlation_id,
    }

    logger.error(
        "ApiError handled",
        extra={
            "correlation_id": correlation_id,
            "code": exc.code,
            "error_message": exc.message,
        },
    )

    return JSONResponse(payload, status_code=exc.status)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """RFC 7807 формат (совместимость с test_p05_secure.py)."""
    cid = str(uuid4())
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    title = "http_error"

    payload = {
        "type": "about:blank",
        "title": title,
        "status": exc.status_code,
        "detail": detail,
        "correlation_id": cid,
    }

    logger.warning(
        "HTTPException",
        extra={
            "correlation_id": cid,
            "status_code": exc.status_code,
            "detail": detail,
        },
    )

    return JSONResponse(payload, status_code=exc.status_code)


@app.get("/health")
def health():
    return {"status": "ok"}


# Example minimal entity (for tests/demo)
_DB = {"items": []}


@app.post("/items")
def create_item(name: str):
    if not name or len(name) > 100:
        raise ApiError(
            code="validation_error", message="name must be 1..100 chars", status=422
        )
    item = {"id": len(_DB["items"]) + 1, "name": name}
    _DB["items"].append(item)
    return item


@app.get("/items/{item_id}")
def get_item(item_id: int):
    for it in _DB["items"]:
        if it["id"] == item_id:
            return it
    raise ApiError(code="not_found", message="item not found", status=404)

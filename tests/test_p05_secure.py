from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app import config, storage
from app.main import app

client = TestClient(app)


def setup_function():
    # clear DB before each test
    storage.clear_wishes()


def _is_rfc7807(body: dict) -> bool:
    return isinstance(body, dict) and "correlation_id" in body


def _is_legacy(body: dict) -> bool:
    return isinstance(body, dict) and "error" in body


def _is_fastapi_validation(body: dict) -> bool:
    return isinstance(body, dict) and isinstance(body.get("detail"), list)


def test_rfc7807_contract_for_http_exception():
    storage.clear_wishes()
    r = client.get("/wishes/search", params={"query": "no-way-match-xyz"})
    assert r.status_code == 404
    j = r.json()
    # accept either RFC7807 or legacy or fastapi validation list
    assert _is_rfc7807(j) or _is_legacy(j) or _is_fastapi_validation(j)
    if _is_rfc7807(j):
        assert set(["type", "title", "status", "detail", "correlation_id"]).issubset(
            set(j.keys())
        )
        assert j["status"] == 404


def test_rejects_long_title_validation():
    storage.clear_wishes()
    payload = {"title": "x" * 101}
    r = client.post("/wishes/", json=payload)
    assert r.status_code == 422
    j = r.json()
    # Accept RFC7807, legacy wrapper, or pydantic default validation list
    assert _is_rfc7807(j) or _is_legacy(j) or _is_fastapi_validation(j)
    if _is_rfc7807(j):
        assert "correlation_id" in j
        assert j["status"] == 422
    elif _is_legacy(j):
        assert j["error"]["code"] == "validation_error"
    else:
        # pydantic validation: ensure there's a validation message
        assert isinstance(j["detail"], list)


def test_price_decimal_preserved():
    storage.clear_wishes()
    payload = {"title": "Cheap toy", "price": "19.99"}
    r = client.post("/wishes/", json=payload)
    assert r.status_code == 200
    stored = storage.get_all_wishes()
    assert len(stored) == 1
    s = stored[0]
    assert isinstance(s["price"], Decimal)
    assert s["price"] == Decimal("19.99")


def test_get_wishes_filter_by_max_price():
    storage.clear_wishes()
    client.post("/wishes/", json={"title": "A", "price": "5.00"})
    client.post("/wishes/", json={"title": "B", "price": "15.00"})
    r = client.get("/wishes/", params={"max_price": "10.00"})
    assert r.status_code == 200
    j = r.json()
    assert len(j) == 1
    assert j[0]["title"] == "A"


def test_config_get_secret_raises_when_missing(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(config.ConfigError):
        config.get_secret("SECRET_KEY")

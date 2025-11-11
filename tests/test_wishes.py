from fastapi.testclient import TestClient

from app import storage
from app.main import app

client = TestClient(app)


def setup_function():
    # очищаем таблицу wishes перед каждым тестом
    storage.clear_wishes()


def _find_by_id(items: list, wid: str):
    for it in items:
        if it.get("id") == wid:
            return it
    return None


def test_create_wish():
    response = client.post("/wishes/", json={"title": "Ноутбук", "price": "50000"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Ноутбук"
    assert "id" in data
    # убедимся, что запись в БД
    stored = storage.get_wish_by_id(data["id"])
    assert stored is not None
    assert stored["title"] == "Ноутбук"


def test_get_wishes():
    r0 = client.get("/wishes/")
    assert r0.status_code == 200
    assert isinstance(r0.json(), list)

    # добавим пару желаний и проверим, что список увеличился
    client.post("/wishes/", json={"title": "A"})
    client.post("/wishes/", json={"title": "B"})
    r = client.get("/wishes/")
    assert r.status_code == 200
    j = r.json()
    assert isinstance(j, list)
    assert len(j) == 2


def test_ttt():
    r = client.get("/wishes/search", params={"query": "тест"})
    print(r.status_code, r.json())


def test_search_wishes():
    client.post("/wishes/", json={"title": "книга"})
    response = client.get("/wishes/search", params={"query": "книга"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["title"] == "книга" for item in data)


def test_update_wish():
    create_resp = client.post("/wishes/", json={"title": "Старое название"})
    assert create_resp.status_code == 200
    wish_id = create_resp.json()["id"]

    response = client.put(f"/wishes/{wish_id}", json={"title": "Новое название"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == wish_id
    assert updated["title"] == "Новое название"

    # дополнительно проверим через GET /wishes/
    r = client.get("/wishes/")
    assert r.status_code == 200
    items = r.json()
    found = _find_by_id(items, wish_id)
    assert found is not None
    assert found["title"] == "Новое название"


def test_delete_wish():
    create_resp = client.post("/wishes/", json={"title": "Для удаления"})
    assert create_resp.status_code == 200
    wish_id = create_resp.json()["id"]

    response = client.delete(f"/wishes/{wish_id}")
    assert response.status_code == 200

    # убедимся, что в БД больше нет записи
    stored = storage.get_wish_by_id(wish_id)
    assert stored is None

    # а также проверим, что GET /wishes/ не содержит удалённого id
    r = client.get("/wishes/")
    assert r.status_code == 200
    assert _find_by_id(r.json(), wish_id) is None

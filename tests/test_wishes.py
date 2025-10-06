from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_wish():
    response = client.post("/wishes/", json={"title": "Ноутбук", "price": 50000})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Ноутбук"


def test_get_wishes():
    response = client.get("/wishes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_wishes():
    client.post("/wishes/", json={"title": "Книга"})
    response = client.get("/wishes/search?query=книга")
    assert response.status_code == 200


def test_update_wish():
    create_resp = client.post("/wishes/", json={"title": "Старое название"})
    wish_id = create_resp.json()["id"]
    response = client.put(f"/wishes/{wish_id}", json={"title": "Новое название"})
    assert response.status_code == 200


def test_delete_wish():
    create_resp = client.post("/wishes/", json={"title": "Для удаления"})
    wish_id = create_resp.json()["id"]
    response = client.delete(f"/wishes/{wish_id}")
    assert response.status_code == 200

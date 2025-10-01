from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()

# Простое хранилище в памяти
wishes_db = []


class WishCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    link: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class WishUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    link: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class WishResponse(BaseModel):
    id: str
    title: str
    link: Optional[str]
    price: Optional[float]
    notes: Optional[str]
    created_at: str


# 1. GET - Получить все желания с фильтрацией по цене
@router.get("/", response_model=List[WishResponse])
def get_wishes(max_price: Optional[float] = Query(None, ge=0)):
    result = wishes_db.copy()

    if max_price is not None:
        result = [
            w for w in result if w["price"] is not None and w["price"] <= max_price
        ]

    return result


# 2. GET - Найти желания по названию
@router.get("/search", response_model=List[WishResponse])
def search_wishes(query: str = Query(..., min_length=1)):
    query_lower = query.lower()
    result = [w for w in wishes_db if query_lower in w["title"].lower()]

    if not result:
        raise HTTPException(status_code=404, detail="Ничего не найдено")

    return result


# 3. POST - Добавить новое желание
@router.post("/", response_model=WishResponse)
def create_wish(wish: WishCreate):
    new_wish = {
        "id": str(uuid4()),
        "title": wish.title,
        "link": wish.link,
        "price": wish.price,
        "notes": wish.notes,
        "created_at": datetime.now().isoformat(),
    }

    wishes_db.append(new_wish)
    return new_wish


# 4. PUT - Изменить существующее желание
@router.put("/{wish_id}", response_model=WishResponse)
def update_wish(wish_id: str, wish_update: WishUpdate):
    for wish in wishes_db:
        if wish["id"] == wish_id:
            # Обновляем только переданные поля
            if wish_update.title is not None:
                wish["title"] = wish_update.title
            if wish_update.link is not None:
                wish["link"] = wish_update.link
            if wish_update.price is not None:
                wish["price"] = wish_update.price
            if wish_update.notes is not None:
                wish["notes"] = wish_update.notes

            return wish

    raise HTTPException(status_code=404, detail="Желание не найдено")


# 5. DELETE - Удалить желание
@router.delete("/{wish_id}")
def delete_wish(wish_id: str):
    for i, wish in enumerate(wishes_db):
        if wish["id"] == wish_id:
            wishes_db.pop(i)
            return {"message": "Желание удалено"}

    raise HTTPException(status_code=404, detail="Желание не найдено")

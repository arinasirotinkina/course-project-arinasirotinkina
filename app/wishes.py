import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, condecimal

from . import storage

router = APIRouter()
logger = logging.getLogger("wishlist.wishes")

# Инициализация хранилища
storage.init_db()


# ======== Модели ========
class WishCreate(BaseModel):
    model_config = {"extra": "forbid"}
    title: str = Field(..., min_length=1, max_length=100)
    link: Optional[str] = None
    price: Optional[condecimal(gt=-1)] = None
    notes: Optional[str] = None


class WishUpdate(BaseModel):
    model_config = {"extra": "forbid"}
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    link: Optional[str] = None
    price: Optional[condecimal(gt=-1)] = None
    notes: Optional[str] = None


class WishResponse(BaseModel):
    id: str
    title: str
    link: Optional[str]
    price: Optional[Decimal]
    notes: Optional[str]
    created_at: str


# ======== Вспомогательные функции ========
def _to_decimal(value) -> Optional[Decimal]:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("invalid decimal")


# ======== Эндпоинты ========
@router.get("/", response_model=List[WishResponse])
def get_wishes(max_price: Optional[Decimal] = Query(None, gt=-1)):
    """Получить все желания с опциональной фильтрацией по максимальной цене."""
    if max_price is not None:
        try:
            max_price = _to_decimal(max_price)
        except ValueError:
            raise HTTPException(status_code=422, detail="invalid_max_price")
        result = storage.get_wishes_by_max_price(max_price)
    else:
        result = storage.get_all_wishes()
    return result


@router.get("/search", response_model=List[WishResponse])
def search_wishes(query: str = Query(..., min_length=1)):
    """Поиск желаний по подстроке в названии."""
    result = storage.search_wishes_by_title(query)
    if not result:
        raise HTTPException(status_code=404, detail="nothing_found")
    return result


@router.post("/", response_model=WishResponse)
def create_wish(wish: WishCreate):
    """Создание нового желания."""
    try:
        price = _to_decimal(wish.price)
    except ValueError:
        raise HTTPException(status_code=422, detail="invalid_price")

    new_wish = {
        "id": str(uuid4()),
        "title": wish.title.strip(),
        "link": (wish.link.strip() if wish.link else None),
        "price": price,
        "notes": (wish.notes.strip() if wish.notes else None),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    stored = storage.insert_wish(new_wish)
    logger.info("wish_created", extra={"id": stored["id"], "title": stored["title"]})
    return stored


@router.put("/{wish_id}", response_model=WishResponse)
def update_wish(wish_id: str, wish_update: WishUpdate):
    """Обновление существующего желания."""
    fields = {}

    if wish_update.title is not None:
        fields["title"] = wish_update.title.strip()
    if wish_update.link is not None:
        fields["link"] = wish_update.link.strip()
    if wish_update.price is not None:
        try:
            fields["price"] = _to_decimal(wish_update.price)
        except ValueError:
            raise HTTPException(status_code=422, detail="invalid_price")
    if wish_update.notes is not None:
        fields["notes"] = wish_update.notes.strip()

    updated = storage.update_wish_in_db(wish_id, fields)
    if not updated:
        raise HTTPException(status_code=404, detail="wish_not_found")

    logger.info("wish_updated", extra={"id": wish_id})
    return updated


@router.delete("/{wish_id}")
def delete_wish(wish_id: str):
    """Удаление желания по ID."""
    ok = storage.delete_wish_in_db(wish_id)
    if ok:
        logger.info("wish_deleted", extra={"id": wish_id})
        return {"message": "Желание удалено"}
    raise HTTPException(status_code=404, detail="wish_not_found")

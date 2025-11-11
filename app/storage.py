from __future__ import annotations

import os
import sqlite3
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional

DB_PATH = os.environ.get("WISHLIST_DB_PATH", "./wishlist.db")
_conn: Optional[sqlite3.Connection] = None


def _connect(path: str = DB_PATH) -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(path, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        init_db()
    return _conn


def init_db(path: Optional[str] = None) -> None:
    conn = _connect(path or DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS wishes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        link TEXT,
        price TEXT,
        notes TEXT,
        created_at TEXT NOT NULL
    )
    """
    )
    conn.commit()


def clear_wishes() -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM wishes")
    conn.commit()


def _row_to_dict(row: sqlite3.Row) -> Dict:
    d = dict(row)
    if d.get("price") is not None:
        try:
            d["price"] = Decimal(d["price"])
        except (InvalidOperation, TypeError, ValueError):
            d["price"] = None
    return d


def insert_wish(w: Dict) -> Dict:
    conn = _connect()
    cur = conn.cursor()
    price = str(w["price"]) if w.get("price") is not None else None
    cur.execute(
        "INSERT INTO wishes(id, title, link, price, notes, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (w["id"], w["title"], w.get("link"), price, w.get("notes"), w["created_at"]),
    )
    conn.commit()
    return get_wish_by_id(w["id"])


def get_all_wishes() -> List[Dict]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM wishes ORDER BY created_at")
    rows = cur.fetchall()
    return [_row_to_dict(r) for r in rows]


def get_wish_by_id(wid: str) -> Optional[Dict]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM wishes WHERE id = ?", (wid,))
    row = cur.fetchone()
    return _row_to_dict(row) if row else None


def update_wish_in_db(wid: str, fields: Dict) -> Optional[Dict]:
    if not fields:
        return None
    to_set = []
    params = []
    for key in ("title", "link", "price", "notes"):
        if key in fields:
            val = (
                str(fields[key])
                if key == "price" and fields[key] is not None
                else fields[key]
            )
            to_set.append(f"{key} = ?")
            params.append(val)
    if not to_set:
        return None
    params.append(wid)
    conn = _connect()
    cur = conn.cursor()
    cur.execute(f"UPDATE wishes SET {', '.join(to_set)} WHERE id = ?", params)
    conn.commit()
    return get_wish_by_id(wid) if cur.rowcount else None


def delete_wish_in_db(wid: str) -> bool:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM wishes WHERE id = ?", (wid,))
    deleted = cur.rowcount > 0
    conn.commit()
    return deleted


def search_wishes_by_title(query: str) -> List[Dict]:
    q = f"%{query.strip().lower()}%"
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM wishes WHERE LOWER(title) LIKE ? ORDER BY created_at", (q,)
    )
    rows = cur.fetchall()
    return [_row_to_dict(r) for r in rows]


def get_wishes_by_max_price(max_price: Decimal) -> List[Dict]:
    try:
        max_price = Decimal(max_price)
    except (InvalidOperation, ValueError, TypeError):
        return []
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM wishes WHERE CAST(price AS REAL) <= CAST(? AS REAL) ORDER BY created_at",
        (str(max_price),),
    )
    rows = cur.fetchall()
    return [_row_to_dict(r) for r in rows]

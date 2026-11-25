"""Q&A 이력 SQLite 저장소 (qna_posts). 질문·답변은 로컬 파일에만 저장됩니다."""
from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from .config import RAG_DIR

QNA_DB_PATH = RAG_DIR / "qna.db"
_lock = threading.Lock()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS qna_posts (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at        TEXT NOT NULL,
    question          TEXT NOT NULL,
    answer            TEXT NOT NULL,
    recommended_codes TEXT NOT NULL DEFAULT '[]',
    model_name        TEXT NOT NULL DEFAULT '',
    views             INTEGER NOT NULL DEFAULT 0
)"""


@contextmanager
def _conn(path: Path | None = None):
    p = path or QNA_DB_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    con.row_factory = sqlite3.Row
    try:
        con.execute(_SCHEMA)
        yield con
        con.commit()
    finally:
        con.close()


def _row(r: sqlite3.Row) -> dict:
    d = dict(r)
    d["recommended_codes"] = json.loads(d["recommended_codes"] or "[]")
    return d


def save_post(question: str, answer: str, codes: list[str], model_name: str, path: Path | None = None) -> int:
    with _lock, _conn(path) as con:
        cur = con.execute(
            "INSERT INTO qna_posts (created_at, question, answer, recommended_codes, model_name) VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(timespec="seconds"), question, answer,
             json.dumps(codes, ensure_ascii=False), model_name))
        return int(cur.lastrowid)


def list_posts(keyword: str = "", limit: int = 50, offset: int = 0, path: Path | None = None) -> list[dict]:
    like = f"%{keyword.strip()}%"
    with _lock, _conn(path) as con:
        rows = con.execute(
            "SELECT id, created_at, question, recommended_codes, model_name, views, substr(answer,1,120) AS preview "
            "FROM qna_posts WHERE question LIKE ? OR answer LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?",
            (like, like, max(1, min(limit, 200)), max(0, offset))).fetchall()
    return [_row(r) for r in rows]


def get_post(post_id: int, count_view: bool = True, path: Path | None = None) -> dict | None:
    with _lock, _conn(path) as con:
        if count_view:
            con.execute("UPDATE qna_posts SET views = views + 1 WHERE id = ?", (post_id,))
        r = con.execute("SELECT * FROM qna_posts WHERE id = ?", (post_id,)).fetchone()
    return _row(r) if r else None


def delete_post(post_id: int, path: Path | None = None) -> bool:
    with _lock, _conn(path) as con:
        return con.execute("DELETE FROM qna_posts WHERE id = ?", (post_id,)).rowcount > 0

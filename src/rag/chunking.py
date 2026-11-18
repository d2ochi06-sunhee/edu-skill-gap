"""의미가 유지되는 크기로 청킹하고 출처 메타데이터를 붙입니다.

원칙: 절(section) 경계를 넘지 않고, 문단 → 문장 순으로 쪼개며, 인접 청크는 일부 겹치게 합니다.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from .loaders import Document

_SENT_SPLIT = re.compile(r"(?<=[.!?。])\s+|\n")


@dataclass
class Chunk:
    chunk_id: str
    text: str
    metadata: dict


def _split_long(paragraph: str, size: int) -> list[str]:
    parts, cur = [], ""
    for sent in _SENT_SPLIT.split(paragraph):
        sent = sent.strip()
        if not sent:
            continue
        while len(sent) > size:
            parts.append(sent[:size])
            sent = sent[size:]
        if cur and len(cur) + len(sent) + 1 > size:
            parts.append(cur)
            cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    if cur:
        parts.append(cur)
    return parts


def split_text(text: str, size: int, overlap: int) -> list[str]:
    units: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if para:
            units.extend(_split_long(para, size) if len(para) > size else [para])

    chunks, cur = [], ""
    for u in units:
        if cur and len(cur) + len(u) + 2 > size:
            chunks.append(cur)
            tail = cur[-overlap:] if overlap else ""
            tail = tail[tail.find(" ") + 1:] if " " in tail else tail   # 단어 경계에서 시작
            cur = f"{tail}\n{u}".strip() if tail else u
        else:
            cur = f"{cur}\n\n{u}".strip() if cur else u
    if cur:
        chunks.append(cur)
    if len(chunks) >= 2 and len(chunks[-1]) < size * 0.2:   # 짧은 꼬리 조각은 앞 청크에 병합
        chunks[-2] = f"{chunks[-2]}\n\n{chunks[-1]}"
        chunks.pop()
    return chunks


def chunk_document(doc: Document, size: int = 600, overlap: int = 100) -> list[Chunk]:
    out: list[Chunk] = []
    n = 0
    for sec in doc.sections:
        for piece in split_text(sec.text, size, overlap):
            if len(piece) < 15:          # 의미 없는 초소형 조각은 색인하지 않음
                continue
            n += 1
            cid = hashlib.sha1(f"{doc.doc_id}|{n}|{piece}".encode("utf-8")).hexdigest()[:24]
            out.append(Chunk(cid, piece, {
                "doc_id": doc.doc_id,
                "doc_title": doc.title,
                "page": sec.page if sec.page is not None else 0,   # 0 = 페이지 정보 없음
                "section": sec.section or "",
                "url": sec.url or doc.url,
                "format": doc.fmt,
                "chunk_index": n,
            }))
    return out

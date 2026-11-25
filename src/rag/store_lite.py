"""경량 색인: 임베딩 모델과 벡터 DB 없이 BM25 키워드 검색만 사용합니다(배포용).

- 색인은 청크를 JSONL 로 저장할 뿐이라 ONNX/Torch/chromadb 가 필요 없습니다.
- 근거 게이트: BM25 원점수가 임계값(기본 10) 미만이면 자료에 없는 질문으로 봅니다.
"""
from __future__ import annotations

import json
import threading

from .chunking import chunk_document
from .config import LITE_CHUNKS_PATH, LITE_MANIFEST_PATH, RagSettings
from .hybrid import BM25, LRUCache, expand_query
from .loaders import Document
from .store import Hit, RagStore


class LiteStore(RagStore):
    def __init__(self, settings: RagSettings):
        self.settings = settings
        self.embedder = None
        self._lock = threading.Lock()
        self._cache = LRUCache(256)
        self._bm25: BM25 | None = None
        self._bm25_rows: list[tuple[str, dict]] = []
        self._rows: list[dict] = []
        manifest = self._load_manifest()
        if manifest.get("params") == self._params:
            self._rows = self._read_rows()

    @property
    def _params(self) -> dict:
        return {"mode": "lite", "chunk_size": self.settings.chunk_size, "chunk_overlap": self.settings.chunk_overlap}

    @staticmethod
    def _read_rows() -> list[dict]:
        if not LITE_CHUNKS_PATH.exists():
            return []
        with LITE_CHUNKS_PATH.open(encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    @staticmethod
    def _load_manifest() -> dict:
        if LITE_MANIFEST_PATH.exists():
            try:
                return json.loads(LITE_MANIFEST_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {"params": None, "docs": {}}

    def _save_manifest(self, m: dict) -> None:
        LITE_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        LITE_CHUNKS_PATH.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in self._rows),
                                    encoding="utf-8")
        LITE_MANIFEST_PATH.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")

    def _count(self) -> int:
        return len(self._rows)

    def _upsert_document(self, doc: Document, manifest: dict, fp: str | None) -> int:
        chunks = chunk_document(doc, self.settings.chunk_size, self.settings.chunk_overlap)
        self._rows = [r for r in self._rows if r["meta"].get("doc_id") != doc.doc_id]
        self._rows += [{"id": c.chunk_id, "text": c.text, "meta": c.metadata} for c in chunks]
        manifest["docs"][doc.doc_id] = {"hash": doc.content_hash, "fp": fp, "chunks": len(chunks),
                                        "title": doc.title, "format": doc.fmt}
        return len(chunks)

    def _drop(self, doc_id: str, manifest: dict) -> None:
        self._rows = [r for r in self._rows if r["meta"].get("doc_id") != doc_id]
        manifest["docs"].pop(doc_id, None)

    def _ensure_bm25(self) -> BM25:
        if self._bm25 is None:
            self._bm25_rows = [(r["text"], r["meta"]) for r in self._rows]
            self._bm25 = BM25([t for t, _ in self._bm25_rows])
        return self._bm25

    def hybrid_search(self, query: str, top_k: int = 5, threshold: float | None = None,
                      w_bm25: float = 1.0, w_vec: float = 1.0, pool: int = 30) -> list[Hit]:
        """BM25 순위로 검색합니다. BM25 점수가 임계값 미만이면 근거 없음으로 처리합니다(점수는 0~1 이 아닌 원점수)."""
        if not self._rows:
            return []
        if threshold is None:
            threshold = self.settings.lite_threshold
        key = (query, top_k, round(threshold, 3))
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        bm = self._ensure_bm25()
        expanded = expand_query(query)
        hits = []
        for rank, (i, score) in enumerate(bm.top(expanded, max(pool, top_k)), 1):
            if score < threshold:
                break
            text, meta = self._bm25_rows[i]
            hits.append(Hit(text=text, score=score, metadata=meta, bm25_rank=rank))
            if len(hits) >= top_k:
                break
        self._cache.put(key, hits)
        return hits

    search = hybrid_search

    def stats(self) -> dict:
        m = self._load_manifest()
        return {"chunks": self._count(), "documents": len(m["docs"]), "embedder": "bm25-lite", "mode": "lite",
                "default_threshold": self.settings.lite_threshold,
                "docs": {k: {"title": v["title"], "chunks": v["chunks"], "format": v["format"]}
                         for k, v in m["docs"].items()}}

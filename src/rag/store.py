"""ChromaDB 영속 인덱스: 변경된 문서만 갱신하고, 검색은 기존 벡터 DB를 재사용합니다."""
from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import chromadb

from .chunking import chunk_document
from .config import (CHROMA_DIR, COLLECTION, DASHBOARD_DIR, DEFAULT_LOCAL_DOCS, EXTRA_DOC_DIR, MANIFEST_PATH,
                     ROOT, SUPPORTED_EXT, URL_LIST_PATH, RagSettings)
from .embedder import Embedder
from .loaders import Document, load_dashboard_data, load_document, load_url

EMBED_BATCH = 32


@dataclass
class Hit:
    text: str
    score: float          # 코사인 유사도 (1 - 코사인 거리)
    metadata: dict


def _fingerprint(path: Path) -> str:
    st = path.stat()
    return f"{st.st_size}:{int(st.st_mtime)}"


def latest_dashboard() -> Path | None:
    files = sorted(DASHBOARD_DIR.glob("hr_career_platform_v2_*.html"))
    return files[-1] if files else None


def discover_sources() -> list[tuple[str, Path]]:
    """(종류, 경로) 목록. 종류: file | dashboard"""
    out: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for rel in DEFAULT_LOCAL_DOCS:
        p = (ROOT / rel).resolve()
        if p.exists():
            seen.add(p)
            out.append(("file", p))
    if EXTRA_DOC_DIR.exists():
        for p in sorted(EXTRA_DOC_DIR.rglob("*")):
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXT and p.resolve() not in seen:
                out.append(("file", p.resolve()))
    dash = latest_dashboard()
    if dash:
        out.append(("dashboard", dash.resolve()))
    return out


def read_url_list() -> list[str]:
    if not URL_LIST_PATH.exists():
        return []
    lines = [l.strip() for l in URL_LIST_PATH.read_text(encoding="utf-8").splitlines()]
    return [l for l in lines if l and not l.startswith("#")]


class RagStore:
    def __init__(self, settings: RagSettings, embedder: Embedder):
        self.settings = settings
        self.embedder = embedder
        self._lock = threading.Lock()
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self._col = self._open_collection()

    # ------------------------------------------------------------ 컬렉션 / 매니페스트
    @property
    def _params(self) -> dict:
        return {"embedder": self.embedder.embedder_id,
                "chunk_size": self.settings.chunk_size, "chunk_overlap": self.settings.chunk_overlap}

    def _open_collection(self):
        manifest = self._load_manifest()
        if manifest.get("params") != self._params:
            # 임베딩 모델·청킹 설정이 바뀌면 벡터 공간이 달라지므로 전체 재색인
            try:
                self._client.delete_collection(COLLECTION)
            except Exception:
                pass
            manifest = {"params": self._params, "docs": {}}
            self._save_manifest(manifest)
        return self._client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    @staticmethod
    def _load_manifest() -> dict:
        if MANIFEST_PATH.exists():
            try:
                return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {"params": None, "docs": {}}

    @staticmethod
    def _save_manifest(m: dict) -> None:
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")

    # ------------------------------------------------------------ 색인
    def _upsert_document(self, doc: Document, manifest: dict, fp: str | None) -> int:
        chunks = chunk_document(doc, self.settings.chunk_size, self.settings.chunk_overlap)
        if doc.doc_id in manifest["docs"]:      # 기존 청크 제거는 이미 색인된 문서에만 필요
            self._col.delete(where={"doc_id": doc.doc_id})
        for i in range(0, len(chunks), EMBED_BATCH):
            batch = chunks[i:i + EMBED_BATCH]
            self._col.add(
                ids=[c.chunk_id for c in batch],
                documents=[c.text for c in batch],
                embeddings=self.embedder.embed_passages([c.text for c in batch]),
                metadatas=[c.metadata for c in batch],
            )
        manifest["docs"][doc.doc_id] = {"hash": doc.content_hash, "fp": fp, "chunks": len(chunks),
                                        "title": doc.title, "format": doc.fmt}
        return len(chunks)

    def _drop(self, doc_id: str, manifest: dict) -> None:
        self._col.delete(where={"doc_id": doc_id})
        manifest["docs"].pop(doc_id, None)

    def sync(self, include_web: bool = False, force: bool = False, progress=None) -> dict:
        """변경된 문서만 다시 색인합니다. 해시가 같으면 임베딩 호출 없이 건너뜁니다."""
        with self._lock:
            t0 = time.time()
            manifest = self._load_manifest()
            if manifest.get("params") != self._params:
                manifest = {"params": self._params, "docs": {}}
            if force:
                for doc_id in list(manifest["docs"]):
                    self._drop(doc_id, manifest)
            report = {"added": [], "updated": [], "unchanged": [], "removed": [], "errors": []}
            live_ids: set[str] = set()

            def handle(docs: list[Document], fp: str | None):
                for doc in docs:
                    live_ids.add(doc.doc_id)
                    old = manifest["docs"].get(doc.doc_id)
                    if old and old["hash"] == doc.content_hash:
                        old["fp"] = fp
                        report["unchanged"].append(doc.doc_id)
                        continue
                    if progress:
                        progress(f"색인 중: {doc.title}")
                    self._upsert_document(doc, manifest, fp)
                    report["updated" if old else "added"].append(doc.doc_id)

            for kind, path in discover_sources():
                key = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
                fp = _fingerprint(path)
                known = [d for d, v in manifest["docs"].items() if d == key or d.startswith(key + "#")]
                # 파일 지문(크기·수정시각)이 같으면 파일을 열지도 않습니다.
                if known and all(manifest["docs"][d].get("fp") == fp for d in known):
                    live_ids.update(known)
                    report["unchanged"].extend(known)
                    continue
                try:
                    docs = load_dashboard_data(path) if kind == "dashboard" else [load_document(path)]
                    handle(docs, fp)
                except Exception as exc:
                    report["errors"].append(f"{path.name}: {type(exc).__name__}: {exc}")
                    live_ids.update(known)

            urls = read_url_list()
            for url in urls:
                if url in manifest["docs"] and not include_web:
                    live_ids.add(url)
                    report["unchanged"].append(url)
                    continue
                try:
                    handle([load_url(url)], None)
                except Exception as exc:
                    report["errors"].append(f"{url}: {type(exc).__name__}: {exc}")
                    if url in manifest["docs"]:
                        live_ids.add(url)

            for doc_id in list(manifest["docs"]):
                if doc_id not in live_ids:
                    self._drop(doc_id, manifest)
                    report["removed"].append(doc_id)

            self._save_manifest(manifest)
            report["seconds"] = round(time.time() - t0, 2)
            report["total_chunks"] = self._col.count()
            return report

    # ------------------------------------------------------------ 검색
    def search(self, query: str, top_k: int = 5, threshold: float | None = None) -> list[Hit]:
        if self._col.count() == 0:
            return []
        if threshold is None:
            threshold = self.embedder.default_threshold
        res = self._col.query(
            query_embeddings=[self.embedder.embed_query(query)],
            n_results=min(max(1, top_k), self._col.count()),
            include=["documents", "metadatas", "distances"],
        )
        hits = []
        for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            score = 1.0 - float(dist)
            if score >= threshold:
                hits.append(Hit(text=text, score=score, metadata=meta))
        return hits

    def stats(self) -> dict:
        m = self._load_manifest()
        return {"chunks": self._col.count(), "documents": len(m["docs"]),
                "embedder": self.embedder.embedder_id, "default_threshold": self.embedder.default_threshold,
                "docs": {k: {"title": v["title"], "chunks": v["chunks"], "format": v["format"]}
                         for k, v in m["docs"].items()}}

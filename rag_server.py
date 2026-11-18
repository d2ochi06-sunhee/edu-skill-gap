"""대시보드용 RAG 챗봇 서버 (표준 라이브러리 HTTP 서버, 의존성 추가 없음).

실행:  python rag_server.py            → http://127.0.0.1:8765  (대시보드 + 챗봇 API)
       python rag_server.py --reindex  → 변경된 문서만 색인하고 종료
API:   GET  /api/status
       POST /api/ask      {"question": "...", "top_k": 5, "threshold": 0.8}
       POST /api/reindex  {"include_web": false, "force": false}
"""
from __future__ import annotations

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.rag.config import get_anthropic_key, get_settings
from src.rag.embedder import create_embedder
from src.rag.qa import answer_question
from src.rag.store import RagStore, latest_dashboard

SETTINGS = get_settings()
_state: dict = {"store": None, "error": None}
_init_lock = threading.Lock()


def get_store() -> RagStore:
    """임베더·벡터 DB 는 처음 한 번만 만들고 이후 재사용합니다."""
    with _init_lock:
        if _state["store"] is None:
            embedder = create_embedder(SETTINGS)
            store = RagStore(SETTINGS, embedder)
            report = store.sync()          # 변경된 문서만 갱신
            print("[rag] 초기 동기화:", {k: len(v) if isinstance(v, list) else v for k, v in report.items()})
            _state["store"] = store
        return _state["store"]


class Handler(BaseHTTPRequestHandler):
    server_version = "HRRag/1.0"

    def _origin_ok(self) -> str | None:
        origin = self.headers.get("Origin")
        if origin is None:
            return ""
        host, port = self.server.server_address[:2]
        allowed = {"null", f"http://127.0.0.1:{port}", f"http://localhost:{port}"}
        return origin if origin in allowed else None

    def _send(self, code: int, body: bytes, ctype: str = "application/json; charset=utf-8"):
        origin = self._origin_ok()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        origin = self._origin_ok()
        self.send_response(204 if origin is not None else 403)
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            page = latest_dashboard()
            if not page:
                return self._json(404, {"error": "dashboard html not found"})
            return self._send(200, page.read_bytes(), "text/html; charset=utf-8")
        if path == "/api/status":
            try:
                s = get_store().stats()
                s.update(llm_configured=bool(get_anthropic_key()), llm_model=SETTINGS.llm_model,
                         default_top_k=SETTINGS.default_top_k)
                return self._json(200, s)
            except Exception as exc:
                return self._json(500, {"error": f"{type(exc).__name__}: {exc}"})
        return self._json(404, {"error": "not found"})

    def do_POST(self):
        if self._origin_ok() is None:
            return self._json(403, {"error": "forbidden origin"})
        path = urlparse(self.path).path
        try:
            length = min(int(self.headers.get("Content-Length") or 0), 20_000)
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {"error": "invalid json"})
        try:
            store = get_store()
            if path == "/api/ask":
                question = str(body.get("question", ""))[:1000]
                top_k = max(1, min(int(body.get("top_k", SETTINGS.default_top_k)), 20))
                thr = body.get("threshold")
                thr = float(thr) if thr is not None else None
                a = answer_question(store, SETTINGS, question, top_k=top_k, threshold=thr)
                return self._json(200, {"answer": a.answer, "found": a.found, "sources": a.sources,
                                        "llm_used": a.llm_used, "note": a.note})
            if path == "/api/reindex":
                return self._json(200, store.sync(include_web=bool(body.get("include_web")),
                                                  force=bool(body.get("force"))))
        except Exception as exc:
            return self._json(500, {"error": f"{type(exc).__name__}: {exc}"})
        return self._json(404, {"error": "not found"})

    def log_message(self, fmt, *args):   # 질문 내용이 로그에 남지 않도록 요청 로그를 줄임
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--reindex", action="store_true", help="변경된 문서만 색인하고 종료")
    ap.add_argument("--force", action="store_true", help="전체 재색인")
    args = ap.parse_args()
    if args.reindex:
        store = get_store()
        print(json.dumps(store.sync(force=args.force, include_web=True), ensure_ascii=False, indent=1))
        return
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)   # 로컬 접속만 허용
    print(f"[rag] http://127.0.0.1:{args.port}  (Ctrl+C 로 종료)")
    threading.Thread(target=get_store, daemon=True).start()          # 백그라운드 예열
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

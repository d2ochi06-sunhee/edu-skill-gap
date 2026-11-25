"""대시보드용 RAG 챗봇 서버 (표준 라이브러리 HTTP 서버, 의존성 추가 없음).

실행:  python rag_server.py            → http://127.0.0.1:8765  (대시보드 + 챗봇 API)
       python rag_server.py --reindex  → 변경된 문서만 색인하고 종료
API:   GET  /api/status
       POST /api/ask         {"question": "...", "top_k": 5, "threshold": 0.8}
       POST /api/ask_stream  같은 요청, 응답은 줄 단위 JSON(NDJSON) 스트림 (delta … done)
       GET  /api/qna?q=키워드 · GET /api/qna/<id> (조회수+1) · DELETE /api/qna/<id>
       POST /api/reindex  {"include_web": false, "force": false}
"""
from __future__ import annotations

import argparse
import json
import os
import threading
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from src.rag import qna_db
from src.rag.config import get_anthropic_key, get_settings, llm_models
from src.rag.qa import answer_question, stream_answer
from src.rag.store import RagStore, latest_dashboard
from src.rag.store_lite import LiteStore

SETTINGS = get_settings()
PUBLIC = os.getenv("RAG_PUBLIC", "") == "1"     # 인터넷에 공개 배포할 때 1: 삭제·재색인 API 차단, 호출 횟수 제한
RATE_LIMIT, RATE_WINDOW = int(os.getenv("RAG_RATE_LIMIT", "20")), 600   # IP당 10분에 20회(Claude API 비용 보호)
_hits: dict[str, deque] = defaultdict(deque)
_hits_lock = threading.Lock()


def rate_limited(ip: str) -> bool:
    now = time.time()
    with _hits_lock:
        q = _hits[ip]
        while q and now - q[0] > RATE_WINDOW:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            return True
        q.append(now)
        return False
_state: dict = {"store": None, "error": None}
_init_lock = threading.Lock()


def get_store() -> RagStore:
    """임베더·벡터 DB 는 처음 한 번만 만들고 이후 재사용합니다."""
    with _init_lock:
        if _state["store"] is None:
            if SETTINGS.rag_mode == "full":      # 벡터+BM25 (무거움). 기본은 BM25 전용 lite
                from src.rag.embedder import create_embedder
                store = RagStore(SETTINGS, create_embedder(SETTINGS))
            else:
                store = LiteStore(SETTINGS)
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
        if PUBLIC:      # 배포 시: 이 서버가 직접 내보낸 페이지(같은 주소)에서 온 요청만 허용
            own = self.headers.get("Host", "")
            allowed |= {f"https://{own}", f"http://{own}"}
        return origin if origin in allowed else None

    def _client_ip(self) -> str:
        fwd = self.headers.get("X-Forwarded-For", "")
        return fwd.split(",")[0].strip() if fwd else self.client_address[0]

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
            self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
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
                         default_top_k=SETTINGS.default_top_k, llm_chain=llm_models(SETTINGS))
                return self._json(200, s)
            except Exception as exc:
                return self._json(500, {"error": f"{type(exc).__name__}: {exc}"})
        if path == "/api/qna" or path.startswith("/api/qna/"):
            try:
                if path == "/api/qna":
                    qs = parse_qs(urlparse(self.path).query)
                    return self._json(200, {"posts": qna_db.list_posts(
                        qs.get("q", [""])[0][:100], int(qs.get("limit", ["50"])[0]), int(qs.get("offset", ["0"])[0]))})
                post = qna_db.get_post(int(path.rsplit("/", 1)[1]))
                return self._json(200, post) if post else self._json(404, {"error": "not found"})
            except ValueError:
                return self._json(400, {"error": "bad request"})
        return self._json(404, {"error": "not found"})

    def do_DELETE(self):
        if PUBLIC:
            return self._json(403, {"error": "disabled on public deployment"})
        if self._origin_ok() is None:
            return self._json(403, {"error": "forbidden origin"})
        path = urlparse(self.path).path
        if path.startswith("/api/qna/"):
            try:
                ok = qna_db.delete_post(int(path.rsplit("/", 1)[1]))
            except ValueError:
                return self._json(400, {"error": "bad request"})
            return self._json(200 if ok else 404, {"deleted": ok})
        return self._json(404, {"error": "not found"})

    def _stream(self, question: str, top_k: int, thr):
        """NDJSON 스트림: 토큰이 생성되는 즉시 전달(TTFT 단축). 완료되면 SQLite 에 백그라운드 저장."""
        origin = self._origin_ok()
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
        self.end_headers()
        try:
            for ev in stream_answer(get_store(), SETTINGS, question, top_k=top_k, threshold=thr):
                if ev["type"] == "done" and ev["found"] and ev["answer"].strip() and ev["llm_used"]:
                    threading.Thread(target=qna_db.save_post, daemon=True,
                                     args=(question, ev["answer"], ev["codes"], ev["model"])).start()
                self.wfile.write((json.dumps(ev, ensure_ascii=False) + "\n").encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as exc:
            err = {"type": "error", "error": f"{type(exc).__name__}: {exc}"}
            try:
                self.wfile.write((json.dumps(err, ensure_ascii=False) + "\n").encode("utf-8"))
            except OSError:
                pass

    def do_POST(self):
        if self._origin_ok() is None:
            return self._json(403, {"error": "forbidden origin"})
        path = urlparse(self.path).path
        try:
            length = min(int(self.headers.get("Content-Length") or 0), 20_000)
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {"error": "invalid json"})
        if PUBLIC and path == "/api/reindex":
            return self._json(403, {"error": "disabled on public deployment"})
        if path in ("/api/ask", "/api/ask_stream") and rate_limited(self._client_ip()):
            return self._json(429, {"error": "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요."})
        if path == "/api/ask_stream":
            top_k = max(1, min(int(body.get("top_k", SETTINGS.default_top_k)), 20))
            thr = body.get("threshold") if SETTINGS.rag_mode == "full" else None   # lite 는 자체 임계값 사용
            return self._stream(str(body.get("question", ""))[:1000], top_k, float(thr) if thr is not None else None)
        try:
            store = get_store()
            if path == "/api/ask":
                question = str(body.get("question", ""))[:1000]
                top_k = max(1, min(int(body.get("top_k", SETTINGS.default_top_k)), 20))
                thr = body.get("threshold") if SETTINGS.rag_mode == "full" else None
                thr = float(thr) if thr is not None else None
                a = answer_question(store, SETTINGS, question, top_k=top_k, threshold=thr)
                return self._json(200, {"answer": a.answer, "found": a.found, "sources": a.sources,
                                        "llm_used": a.llm_used, "note": a.note,
                                        "codes": a.codes, "model": a.model})
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
    ap.add_argument("--port", type=int, default=int(os.getenv("PORT", "8765")))   # 배포 환경은 PORT 를 지정해 줍니다
    ap.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    ap.add_argument("--reindex", action="store_true", help="변경된 문서만 색인하고 종료")
    ap.add_argument("--force", action="store_true", help="전체 재색인")
    args = ap.parse_args()
    if args.reindex:
        store = get_store()
        print(json.dumps(store.sync(force=args.force, include_web=True), ensure_ascii=False, indent=1))
        return
    srv = ThreadingHTTPServer((args.host, args.port), Handler)   # 기본은 로컬만, 배포 시 HOST=0.0.0.0
    print(f"[rag] http://{args.host}:{args.port}  (Ctrl+C 로 종료)")
    threading.Thread(target=get_store, daemon=True).start()          # 백그라운드 예열
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

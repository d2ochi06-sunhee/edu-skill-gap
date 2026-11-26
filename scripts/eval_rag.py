"""RAG 품질·성능 평가: 검색(BM25 vs Vector vs Hybrid) + 생성(환각률·TTFT·완료시간).

실행:  python scripts/eval_rag.py [--n 100] [--gen 10] [--seed 7]
- 정답 세트: 대시보드 교육과정에서 무작위로 뽑은 과정의 제목 일부(앞 3개 단어)를 질문으로, 해당 식별코드를 정답으로 삼습니다.
- 생성 평가는 .env 에 GEMINI_API_KEY 가 있을 때만 실행합니다.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import statistics as st
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

K = 5
ID_RE = re.compile(r"식별코드:\s*([A-Za-z0-9_\-]+)")


def load_courses() -> list[dict]:
    from src.rag.store import latest_dashboard

    html = latest_dashboard().read_text(encoding="utf-8")
    i = html.index("const DATA = ") + len("const DATA = ")
    return json.JSONDecoder().raw_decode(html[i:])[0]["courses"]


def make_queries(courses: list[dict], n: int, seed: int) -> list[tuple[str, str]]:
    rnd = random.Random(seed)
    out = []
    for c in rnd.sample(courses, min(n, len(courses))):
        words = re.sub(r"[『』()\[\]]", " ", c["t"]).split()
        if len(words) >= 2:
            out.append((" ".join(words[:3]), c["id"]))
    return out


def ids_of(texts: list[str]) -> list[str]:
    """검색된 청크 텍스트 목록 → 순서를 유지한 식별코드 목록(청크 안에 코드가 여러 개일 수 있음)."""
    seen: list[str] = []
    for t in texts:
        for code in ID_RE.findall(t):
            if code not in seen:
                seen.append(code)
    return seen


def retrieval_metrics(queries, search_fn) -> dict:
    hit5, rr, lat = 0, 0.0, []
    for q, gold in queries:
        t0 = time.perf_counter()
        codes = search_fn(q)
        lat.append((time.perf_counter() - t0) * 1000)
        if gold in codes[:K]:
            hit5 += 1
        if gold in codes:
            rr += 1.0 / (codes.index(gold) + 1)
    n = len(queries) or 1
    return {"recall@5": hit5 / n, "mrr": rr / n, "p50_ms": st.median(lat) if lat else 0.0,
            "p95_ms": sorted(lat)[int(len(lat) * 0.95) - 1] if lat else 0.0}


def eval_retrieval(store, queries) -> dict:
    from src.rag.hybrid import expand_query

    pool = 30
    bm = store._ensure_bm25()

    def bm25_fn(q):
        return ids_of([store._bm25_rows[i][0] for i, _ in bm.top(expand_query(q), pool)])

    def vec_fn(q):
        res = store._col.query(query_embeddings=[store.embedder.embed_query(q)], n_results=pool, include=["documents"])
        return ids_of(res["documents"][0])

    def hybrid_fn(q):
        return ids_of([h.text for h in store.hybrid_search(q, top_k=pool, threshold=0.0)])

    store._cache.clear()
    result = {name: retrieval_metrics(queries, fn) for name, fn in
              (("BM25", bm25_fn), ("Vector", vec_fn), ("Hybrid(RRF)", hybrid_fn))}
    t0 = time.perf_counter()                       # 같은 질문 재조회 → LRU 캐시 적중 지연
    for q, _ in queries:
        hybrid_fn(q)
    result["Hybrid 캐시 적중"] = {"p50_ms": (time.perf_counter() - t0) * 1000 / (len(queries) or 1)}
    return result


def eval_generation(store, settings, queries, valid_ids: set[str]) -> dict | None:
    from src.rag.config import get_llm_key
    from src.rag.qa import CODE_RE, stream_answer

    if not get_llm_key():
        return None
    ttft, total, recommended, fake = [], [], 0, 0
    for q, _ in queries:
        t0, first, parts = time.perf_counter(), None, []
        for ev in stream_answer(store, settings, q, top_k=K, threshold=0.0):
            if ev["type"] == "delta":
                first = first or (time.perf_counter() - t0)
                parts.append(ev["text"])
        total.append(time.perf_counter() - t0)
        if first is not None:
            ttft.append(first)
        for code in CODE_RE.findall("".join(parts)):        # 검증 전 원문 기준으로 환각 측정
            recommended += 1
            fake += code not in valid_ids
    return {"질문수": len(queries), "추천 코드 수": recommended, "환각률(%)": 100 * fake / recommended if recommended else 0.0,
            "TTFT 평균(ms)": 1000 * st.mean(ttft) if ttft else None, "완료시간 평균(ms)": 1000 * st.mean(total)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100, help="검색 평가 질문 수")
    ap.add_argument("--gen", type=int, default=10, help="생성 평가 질문 수(API 비용 발생)")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    from src.rag.config import get_settings
    from src.rag.embedder import create_embedder
    from src.rag.store import RagStore

    settings = get_settings()
    store = RagStore(settings, create_embedder(settings))
    store.sync()
    courses = load_courses()
    queries = make_queries(courses, args.n, args.seed)
    print(f"[평가 세트] 질문 {len(queries)}건 · 임베더 {store.embedder.embedder_id}\n")

    print("== 검색 품질 ==")
    print(f"{'방식':<16}{'Recall@5':>10}{'MRR':>8}{'p50(ms)':>10}{'p95(ms)':>10}")
    for name, m in eval_retrieval(store, queries).items():
        if "recall@5" in m:
            print(f"{name:<16}{m['recall@5']:>10.3f}{m['mrr']:>8.3f}{m['p50_ms']:>10.2f}{m['p95_ms']:>10.2f}")
        else:
            print(f"{name:<16}{'':>10}{'':>8}{m['p50_ms']:>10.3f}")

    print("\n== 생성·그라운딩 품질 ==")
    gen = eval_generation(store, settings, queries[:args.gen], {c["id"] for c in courses})
    if gen is None:
        print("GEMINI_API_KEY 가 없어 생략했습니다.")
    else:
        for k, v in gen.items():
            print(f"{k}: {v:.1f}" if isinstance(v, float) else f"{k}: {v}")


if __name__ == "__main__":
    main()

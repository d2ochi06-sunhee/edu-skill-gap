"""기존 대시보드 HTML에 RAG 챗봇(검색 엔진·자료 내장)을 합쳐 날짜가 붙은 새 파일로 저장합니다.

사용:  python scripts/build_dashboard_rag.py [--base dashboard/hr_career_platform_v2_2026-11-16.html] [--out ...]
- 문서(PDF/CSV/MD/대시보드 가이드)는 청킹해 JSON 으로 내장하고, 교육과정은 대시보드의 DATA 를 브라우저에서 재사용합니다.
- 결과 HTML 한 파일만 열면 서버 없이 검색·출처 표시가 동작합니다.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rag.chunking import chunk_document          # noqa: E402
from src.rag.config import get_settings              # noqa: E402
from src.rag.loaders import load_dashboard_data, load_document  # noqa: E402
from src.rag.store import discover_sources           # noqa: E402

WEB = ROOT / "src" / "rag" / "web"


def export_chunks(settings) -> list[dict]:
    rows = []
    for kind, path in discover_sources():
        docs = load_dashboard_data(path) if kind == "dashboard" else [load_document(path)]
        for doc in docs:
            if doc.doc_id.endswith("#courses"):       # 교육과정은 브라우저에서 DATA 로 생성
                continue
            for c in chunk_document(doc, settings.chunk_size, settings.chunk_overlap):
                m = c.metadata
                rows.append({"t": c.text, "d": m["doc_title"], "p": m["page"], "s": m["section"], "u": m["url"]})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=str(ROOT / "dashboard" / "hr_career_platform_v2_2026-11-16.html"))
    ap.add_argument("--out", default=str(ROOT / "dashboard" / f"hr_career_platform_v2_{date.today():%Y-%m-%d}_rag.html"))
    ap.add_argument("--chunks-only", help="청크 JSON 만 저장")
    args = ap.parse_args()

    rows = export_chunks(get_settings())
    if args.chunks_only:
        Path(args.chunks_only).write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        print(len(rows), "chunks")
        return

    html = Path(args.base).read_bytes().decode("utf-8")
    assert html.count("</style>") == 1 and html.count("</body>") == 1, "예상과 다른 대시보드 구조"
    css = (WEB / "chat.css").read_text(encoding="utf-8")
    markup = (WEB / "chat.html").read_text(encoding="utf-8")
    engine = (WEB / "engine.js").read_text(encoding="utf-8")
    ui = (WEB / "chat.js").read_text(encoding="utf-8")
    payload = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    scripts = (f"\n<script>\nconst RAG_DOCS = {payload};\n</script>\n<script>\n{engine}\n</script>\n{ui}\n")
    # 근거 없는 '선배 조언'(grades.advice)은 화면에서 제거
    advice_line = "      <p><b>🗣️ 선배 조언</b><br>${esc(gr.advice)}</p>\n"
    assert advice_line in html, "선배 조언 줄을 찾지 못했습니다"
    html = html.replace(advice_line, "").replace("자격증, 선배 조언</summary>", "자격증</summary>")
    out = html.replace("</style>", css + "</style>").replace("</body>", markup + scripts + "</body>")
    Path(args.out).write_bytes(out.encode("utf-8"))
    print(f"{len(rows)} 문서 청크 내장 → {args.out}")


if __name__ == "__main__":
    main()

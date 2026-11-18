"""문서 형식별 로딩·정제·텍스트 추출 (PDF / CSV / Markdown·TXT / 웹 HTML).

모든 로더는 `Document` 를 반환하며, Document 는 청킹 이전의 의미 단위(페이지 또는 절)인
`Section` 목록을 가집니다. 각 Section 은 문서명·페이지·섹션·URL 출처를 이미 알고 있습니다.
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .config import GITHUB_BLOB, ROOT


@dataclass
class Section:
    text: str
    page: int | None = None
    section: str = ""
    url: str = ""          # 절 단위 고유 링크가 있으면 문서 URL 대신 사용


@dataclass
class Document:
    doc_id: str            # 안정적인 문서 식별자 (상대경로 또는 URL)
    title: str             # 화면에 보여 줄 문서명
    url: str               # 링크 (웹 문서 URL 또는 GitHub 링크)
    fmt: str               # pdf / csv / md / txt / html
    sections: list[Section] = field(default_factory=list)

    @property
    def content_hash(self) -> str:
        h = hashlib.sha256()
        for s in self.sections:
            h.update(f"{s.page}|{s.section}|{s.text}".encode("utf-8"))
        return h.hexdigest()


# ------------------------------------------------------------------ 공통 정제
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f​﻿]")


def clean_text(text: str) -> str:
    """유니코드 정규화, 제어문자·과다 공백 제거, 줄바꿈 하이픈 결합."""
    text = unicodedata.normalize("NFC", text)
    text = _CTRL.sub("", text)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _rel(path: Path) -> Path | None:
    try:
        return path.resolve().relative_to(ROOT)
    except ValueError:
        return None


def _doc_url(path: Path) -> str:
    rel = _rel(path)
    if rel is None:
        return path.resolve().as_uri()
    return GITHUB_BLOB + rel.as_posix().replace(" ", "%20")


def _doc_id(path: Path) -> str:
    rel = _rel(path)
    return rel.as_posix() if rel else path.resolve().as_posix()


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


# ------------------------------------------------------------------ Markdown / TXT
_MD_HEAD = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_NUM_HEAD = re.compile(r"^(?:\d+(?:\.\d+)*[.)]|제\s?\d+\s?[장절조]|[가-하][.)]|[①-⑩])\s+\S.{0,50}$")


def _split_markdown(text: str) -> list[Section]:
    """제목 계층을 따라 절 단위로 분할. section 에는 'A > B' 형태의 경로를 저장합니다."""
    stack: list[tuple[int, str]] = []
    buf: list[str] = []
    out: list[Section] = []
    in_code = False

    def flush():
        body = clean_text("\n".join(buf))
        if body:
            out.append(Section(text=body, section=" > ".join(t for _, t in stack)))
        buf.clear()

    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
        m = None if in_code else _MD_HEAD.match(line)
        if m:
            flush()
            level, title = len(m.group(1)), re.sub(r"[*_`]", "", m.group(2)).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
        else:
            buf.append(line)
    flush()
    return out


def _split_txt(text: str) -> list[Section]:
    """번호형 제목(1. / 제1장 / 가.)이 있으면 절로 구분합니다."""
    cur, buf, out = "", [], []

    def flush():
        body = clean_text("\n".join(buf))
        if body:
            out.append(Section(text=body, section=cur))
        buf.clear()

    for line in text.splitlines():
        if _NUM_HEAD.match(line.strip()):
            flush()
            cur = line.strip()
        else:
            buf.append(line)
    flush()
    return out


def load_markdown(path: Path) -> Document:
    text = _read_text(path)
    ext = path.suffix.lower()
    sections = _split_markdown(text) if ext == ".md" else _split_txt(text)
    return Document(_doc_id(path), path.name, _doc_url(path), ext.lstrip("."), sections)


# ------------------------------------------------------------------ PDF
_PAGE_NO = re.compile(r"[-–]?\s*\d{1,4}\s*[-–]?|\d+\s*/\s*\d+|Page\s*\d+", re.I)


def load_pdf(path: Path) -> Document:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [(p.extract_text() or "") for p in reader.pages]

    # 머리글·바닥글: 여러 페이지에 반복되는 짧은 줄 제거
    line_counts: Counter = Counter()
    for p in pages:
        for ln in {l.strip() for l in p.splitlines() if l.strip()}:
            if len(ln) < 60:
                line_counts[ln] += 1
    repeated = set()
    if len(pages) >= 4:
        repeated = {ln for ln, c in line_counts.items() if c >= max(3, len(pages) * 0.5)}

    sections: list[Section] = []
    heading = ""
    for idx, raw in enumerate(pages, start=1):
        kept = []
        for ln in raw.splitlines():
            s = ln.strip()
            if not s:
                kept.append("")
                continue
            if s in repeated or _PAGE_NO.fullmatch(s):
                continue
            if _NUM_HEAD.match(s) or _MD_HEAD.match(s):
                heading = clean_text(re.sub(r"^#+\s*", "", s))
            kept.append(s)
        text = clean_text("\n".join(kept))
        if len(text) >= 20:
            sections.append(Section(text=text, page=idx, section=heading))
    return Document(_doc_id(path), path.name, _doc_url(path), "pdf", sections)


# ------------------------------------------------------------------ CSV
def load_csv(path: Path, rows_per_section: int = 8) -> Document:
    """CSV 는 '컬럼명: 값' 으로 풀어 쓴 행 묶음을 의미 단위로 사용합니다."""
    rows = list(csv.DictReader(io.StringIO(_read_text(path))))
    sections: list[Section] = []
    for start in range(0, len(rows), rows_per_section):
        part = rows[start:start + rows_per_section]
        lines = []
        for n, row in enumerate(part, start=start + 1):
            cells = "; ".join(f"{k.strip()}: {str(v).strip()}"
                              for k, v in row.items() if k and v not in (None, ""))
            lines.append(f"[행 {n}] {cells}")
        sections.append(Section(text=clean_text("\n".join(lines)),
                                section=f"행 {start + 1}–{start + len(part)}"))
    return Document(_doc_id(path), path.name, _doc_url(path), "csv", sections)


# ------------------------------------------------------------------ HTML / 웹
_DROP_TAGS = ["script", "style", "noscript", "nav", "header", "footer", "aside", "form", "svg", "iframe"]


def html_to_sections(html: str) -> tuple[str, list[Section]]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for t in soup(_DROP_TAGS):
        t.decompose()
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    root = soup.find("main") or soup.find("article") or soup.body or soup

    sections: list[Section] = []
    stack: list[tuple[int, str]] = []
    buf: list[str] = []

    def flush():
        body = clean_text("\n".join(buf))
        if body:
            sections.append(Section(text=body, section=" > ".join(t for _, t in stack)))
        buf.clear()

    for el in root.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th", "pre", "blockquote"]):
        txt = el.get_text(" ", strip=True)
        if not txt:
            continue
        if el.name[0] == "h" and el.name[1:].isdigit():
            flush()
            lvl = int(el.name[1])
            while stack and stack[-1][0] >= lvl:
                stack.pop()
            stack.append((lvl, txt))
        else:
            buf.append(txt)
    flush()
    return title, sections


def load_html_file(path: Path) -> Document:
    title, sections = html_to_sections(_read_text(path))
    return Document(_doc_id(path), title or path.name, _doc_url(path), "html", sections)


def load_url(url: str, timeout: int = 20) -> Document:
    import requests

    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "edu-skill-gap-rag/1.0"})
    resp.raise_for_status()
    ctype = resp.headers.get("content-type", "").lower()
    if "pdf" in ctype or url.lower().split("?")[0].endswith(".pdf"):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(resp.content)
            tmp = Path(f.name)
        try:
            doc = load_pdf(tmp)
        finally:
            tmp.unlink(missing_ok=True)
        doc.doc_id, doc.url, doc.title = url, url, url.rsplit("/", 1)[-1] or url
        return doc
    if resp.encoding in (None, "ISO-8859-1"):
        resp.encoding = resp.apparent_encoding
    title, sections = html_to_sections(resp.text)
    return Document(url, title or url, url, "html", sections)


# ------------------------------------------------------------------ 대시보드 내장 데이터
def _fmt(v) -> str:
    if isinstance(v, list):
        return " / ".join(_fmt(x) for x in v)
    if isinstance(v, dict):
        return "; ".join(f"{k}: {_fmt(x)}" for k, x in v.items())
    return str(v)


def load_dashboard_data(path: Path) -> list[Document]:
    """대시보드 HTML 에 내장된 `const DATA = {...}` 를 직무·직급 가이드와 교육과정 문서로 변환합니다."""
    import json

    html = _read_text(path)
    marker = "const DATA = "
    i = html.index(marker) + len(marker)
    data, _ = json.JSONDecoder().raw_decode(html[i:])

    rel = _doc_id(path)
    link = _doc_url(path)
    grades = [g.get("name", "") for g in data.get("grades", [])]
    docs: list[Document] = []

    # 1) 직급 가이드
    secs = []
    for g in data.get("grades", []):
        body = "\n".join(f"{k}: {_fmt(v)}" for k, v in g.items() if k != "advice" and v not in ("", None, []))
        secs.append(Section(clean_text(body), section=f"직급 {g.get('name', '')} ({g.get('years', '')})"))
    docs.append(Document(f"{rel}#grades", "대시보드 · 직급별 성장 가이드", link, "dashboard", secs))

    # 2) 직무(도메인) 가이드
    secs = []
    for d in data.get("domains", []):
        t = d.get("task", {}) or {}
        lines = [f"분야: {d.get('full') or d.get('short', '')}", f"요약: {d.get('brief', '')}"]
        if t:
            lines += [f"핵심 업무: {t.get('name', '')}", f"쉬운 설명: {t.get('easy', '')}",
                      f"지식: {t.get('k', '')}", f"기술: {t.get('s', '')}", f"태도: {t.get('a', '')}"]
            for n, lv in enumerate(t.get("levels", []) or []):
                lines.append(f"{grades[n] if n < len(grades) else n + 1} 수준 달성 기준: {lv}")
            for r in t.get("roles", []) or []:
                lines.append(f"역할 [{r.get('badge', '')}]: {r.get('role', '')}")
        secs.append(Section(clean_text("\n".join(lines)), section=d.get("short", "")))
    docs.append(Document(f"{rel}#domains", "대시보드 · 인사 직무별 업무 기준", link, "dashboard", secs))

    # 3) 교육과정 (과정 1건 = 1절, 과정별 고유 링크 보존)
    secs = []
    for c in data.get("courses", []):
        cat = (data.get("cats", {}).get(c.get("cat"), {}) or {})
        cat_name = cat.get("name", c.get("cat", "")) if isinstance(cat, dict) else str(cat)
        target = ", ".join(grades[i] for i in c.get("grades", []) if i < len(grades))
        text = (f"교육과정: {c.get('t', '')}\n교육기관: {c.get('inst', '')}\n플랫폼: {c.get('plat', '')}\n"
                f"분야: {cat_name}\n추천 직급: {target or '전체'}")
        secs.append(Section(clean_text(text), section=f"{c.get('plat', '')} · {cat_name}", url=c.get("url", "")))
    docs.append(Document(f"{rel}#courses", "대시보드 · 교육과정 목록", link, "dashboard", secs))
    return docs


# ------------------------------------------------------------------ 진입점
def load_document(path: Path) -> Document:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return load_pdf(path)
    if ext == ".csv":
        return load_csv(path)
    if ext in (".md", ".txt"):
        return load_markdown(path)
    if ext in (".html", ".htm"):
        return load_html_file(path)
    raise ValueError(f"지원하지 않는 형식: {path.name}")

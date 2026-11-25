"""하이브리드 검색 부품: BM25(어휘) + RRF 순위 융합 + LRU 쿼리 캐시. 외부 의존성 없음."""
from __future__ import annotations

import math
import re
import threading
from collections import OrderedDict, defaultdict

_TOKEN = re.compile(r"[0-9A-Za-z_]+|[가-힣]+")
_SUFFIX = re.compile(r"(이란|에서|에게|으로|이다|입니다|인가요|하는|하고|해서|합니다|에는|에서의|를|을|은|는|이|가|의|에|와|과|로|도)$")

# 도메인 특화 질의 확장: 질문에 키가 있으면 값 단어를 같이 검색합니다.
SYNONYMS: dict[str, list[str]] = {
    "채용": ["리크루팅", "선발", "면접"],
    "평가": ["인사평가", "성과관리", "KPI"],
    "급여": ["임금", "보상", "페이롤"],
    "노무": ["근로기준법", "노동법", "인사노무"],
    "교육": ["훈련", "연수", "러닝"],
    "엑셀": ["컴활", "OA", "스프레드시트"],
}


def tokenize(text: str) -> list[str]:
    """한글은 조사 제거 후 2~3자 n-gram 을 함께 만들어 형태 변화에 강하게 합니다."""
    out: list[str] = []
    for raw in _TOKEN.findall(str(text).lower()):
        tok = _SUFFIX.sub("", raw) if re.fullmatch(r"[가-힣]{3,}", raw) else raw
        tok = tok if len(tok) >= 2 or not re.fullmatch(r"[가-힣]", tok) else raw
        out.append(tok)
        if re.search(r"[가-힣]", tok) and len(tok) > 2:
            out.extend(tok[i:i + 2] for i in range(len(tok) - 1))
    return out


def expand_query(query: str) -> str:
    extra = [w for key, words in SYNONYMS.items() if key in query for w in words]
    return query + " " + " ".join(extra) if extra else query


class BM25:
    """BM25Okapi 와 동일한 점수식(k1=1.5, b=0.75)을 직접 구현한 것입니다."""

    def __init__(self, docs: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf: list[dict[str, int]] = []
        self.dl: list[int] = []
        df: dict[str, int] = defaultdict(int)
        self.post: dict[str, list[int]] = defaultdict(list)
        for i, d in enumerate(docs):
            freq: dict[str, int] = defaultdict(int)
            for t in tokenize(d):
                freq[t] += 1
            self.tf.append(freq)
            self.dl.append(sum(freq.values()))
            for t in freq:
                df[t] += 1
                self.post[t].append(i)
        self.n = len(docs)
        self.avgdl = (sum(self.dl) / self.n) if self.n else 0.0
        self.idf = {t: math.log(1 + (self.n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def scores(self, query: str) -> dict[int, float]:
        out: dict[int, float] = defaultdict(float)
        for t in set(tokenize(query)):
            idf = self.idf.get(t)
            if idf is None:
                continue
            for i in self.post[t]:
                f = self.tf[i][t]
                norm = self.k1 * (1 - self.b + self.b * self.dl[i] / (self.avgdl or 1))
                out[i] += idf * f * (self.k1 + 1) / (f + norm)
        return out

    def top(self, query: str, n: int) -> list[tuple[int, float]]:
        return sorted(self.scores(query).items(), key=lambda x: -x[1])[:n]


def rrf(rank_lists: list[tuple[float, list]], k: int = 60) -> dict:
    """Score(d) = Σ w / (k + rank(d)).  rank_lists = [(가중치, [문서키, ...순위순]), ...]"""
    fused: dict = defaultdict(float)
    for weight, ranked in rank_lists:
        for rank, key in enumerate(ranked, 1):
            fused[key] += weight / (k + rank)
    return fused


class LRUCache:
    """스레드 안전 LRU. 같은 질문 반복 시 임베딩·검색을 건너뜁니다."""

    def __init__(self, size: int = 256):
        self.size = size
        self._d: OrderedDict = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            if key in self._d:
                self._d.move_to_end(key)
                return self._d[key]
        return None

    def put(self, key, value) -> None:
        with self._lock:
            self._d[key] = value
            self._d.move_to_end(key)
            while len(self._d) > self.size:
                self._d.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._d.clear()

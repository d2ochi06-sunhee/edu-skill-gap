"""임베딩 모델 래퍼. 문서 청크와 사용자 질문을 반드시 같은 모델로 벡터화합니다.

백엔드:
- fastembed            : ONNX 기반 다국어 모델 (기본: intfloat/multilingual-e5-large)
- sentence-transformers: PyTorch 기반 모델
- hash                 : 모델 없이 글자 n-gram 을 해싱하는 어휘 임베딩.
                         ONNX/Torch 가 동작하지 않는 환경에서만 쓰는 최후 대체 수단이며
                         의미 검색이 아니라 표면 어휘 유사도입니다.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Sequence

from .config import RagSettings


class Embedder:
    backend: str = ""
    model: str = ""
    default_threshold: float = 0.5

    @property
    def embedder_id(self) -> str:
        return f"{self.backend}:{self.model}"

    def embed_passages(self, texts: Sequence[str]) -> list[list[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError


class FastEmbedEmbedder(Embedder):
    backend = "fastembed"

    def __init__(self, model: str):
        from fastembed import TextEmbedding

        self.model = model
        self._m = TextEmbedding(model_name=model)
        # e5 계열은 코사인 유사도가 높은 구간에 몰리므로 임계값 기본값을 높게 둡니다.
        self.default_threshold = 0.80 if "e5" in model.lower() else 0.50

    def embed_passages(self, texts):
        if hasattr(self._m, "passage_embed"):
            return [v.tolist() for v in self._m.passage_embed(list(texts))]
        return [v.tolist() for v in self._m.embed(list(texts))]

    def embed_query(self, text):
        if hasattr(self._m, "query_embed"):
            return next(iter(self._m.query_embed(text))).tolist()
        return next(iter(self._m.embed([text]))).tolist()


class SentenceTransformerEmbedder(Embedder):
    backend = "sentence-transformers"

    def __init__(self, model: str):
        from sentence_transformers import SentenceTransformer

        self.model = model
        self._m = SentenceTransformer(model)
        self._e5 = "e5" in model.lower()
        self.default_threshold = 0.80 if self._e5 else 0.50

    def _enc(self, texts, prefix):
        texts = [prefix + t for t in texts] if self._e5 else list(texts)
        return self._m.encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()

    def embed_passages(self, texts):
        return self._enc(texts, "passage: ")

    def embed_query(self, text):
        return self._enc([text], "query: ")[0]


_TOKEN = re.compile(r"[0-9A-Za-z]+|[가-힣]+")
_DIM = 4096


class HashEmbedder(Embedder):
    backend = "hash"
    model = "char-ngram-4096"
    default_threshold = 0.30

    def _vec(self, text: str) -> list[float]:
        vec = [0.0] * _DIM
        for tok in _TOKEN.findall(text.lower()):
            grams = {tok} | {tok[i:i + n] for n in (2, 3) for i in range(len(tok) - n + 1)}
            for g in grams:
                h = int.from_bytes(hashlib.md5(g.encode("utf-8")).digest()[:4], "little")
                vec[h % _DIM] += 1.0 + 0.5 * (len(g) - 1)   # 긴 n-gram 에 가중
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_passages(self, texts):
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        return self._vec(text)


def create_embedder(settings: RagSettings) -> Embedder:
    backend = settings.embed_backend.lower()
    errors: list[str] = []
    order = ["fastembed", "sentence-transformers", "hash"] if backend == "auto" else [backend]
    for name in order:
        try:
            if name == "fastembed":
                return FastEmbedEmbedder(settings.embed_model)
            if name in ("sentence-transformers", "st"):
                return SentenceTransformerEmbedder(settings.embed_model)
            if name == "hash":
                return HashEmbedder()
            raise ValueError(f"알 수 없는 임베딩 백엔드: {name}")
        except Exception as exc:  # 네이티브 런타임/모델 다운로드 실패 시 다음 후보로
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
    raise RuntimeError("임베딩 백엔드를 초기화하지 못했습니다 → " + " | ".join(errors))

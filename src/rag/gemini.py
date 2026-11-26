"""Gemini API 스트리밍 클라이언트 (requests 만 사용, 추가 의존성 없음).

qa.py 가 쓰는 `client.messages.stream(...)` → `.text_stream` 모양을 그대로 제공합니다.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from types import SimpleNamespace

import requests

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
MIN_OUTPUT_TOKENS = 4096     # Gemini 는 추론 토큰도 출력 한도에 포함되어, 작게 잡으면 답이 잘립니다


class GeminiError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(f"Gemini API {status_code}: {message}")
        self.status_code = status_code


def _iter_text(response):
    """SSE 응답에서 답변 텍스트만 꺼냅니다(추론 내용은 제외)."""
    for raw in response.iter_lines():
        if not raw.startswith(b"data:"):
            continue
        event = json.loads(raw[5:].decode("utf-8"))
        if "error" in event:
            raise GeminiError(event["error"].get("code", 500), event["error"].get("message", ""))
        for cand in event.get("candidates", [])[:1]:
            for part in cand.get("content", {}).get("parts", []):
                if part.get("text") and not part.get("thought"):
                    yield part["text"]


class GeminiClient:
    def __init__(self, api_key: str, timeout: float = 30.0):
        self._session = requests.Session()
        self._session.headers["x-goog-api-key"] = api_key      # 키는 URL 이 아닌 헤더로 전달(로그 노출 방지)
        self._timeout = timeout
        self.messages = SimpleNamespace(stream=self._stream)

    @contextmanager
    def _stream(self, model: str, max_tokens: int, system: str, messages: list[dict]):
        body = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": m["content"]}]} for m in messages],
            "generationConfig": {"maxOutputTokens": max(max_tokens, MIN_OUTPUT_TOKENS)},
        }
        with self._session.post(f"{BASE_URL}/{model}:streamGenerateContent", params={"alt": "sse"},
                                json=body, stream=True, timeout=self._timeout) as response:
            if response.status_code != 200:
                raise GeminiError(response.status_code, response.text[:300])
            yield SimpleNamespace(text_stream=_iter_text(response))

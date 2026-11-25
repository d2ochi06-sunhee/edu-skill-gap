"""하이브리드 검색·폴백 체인·코드 검증·Q&A DB 단위 테스트 (네트워크/네이티브 라이브러리 불필요)."""
import tempfile
from pathlib import Path
from types import SimpleNamespace

from src.rag import qa, qna_db
from src.rag.config import RagSettings, llm_models
from src.rag.hybrid import BM25, LRUCache, rrf
from src.rag.store import Hit


def test_bm25_prefers_keyword_match():
    docs = ["엑셀 실무 컴활 2급", "노무 관리 근로기준법", "채용 면접 기법"]
    assert BM25(docs).top("근로기준법 노무", 3)[0][0] == 1


def test_rrf_formula():
    f = rrf([(1.0, ["a", "b"]), (1.0, ["b", "a"])])
    assert abs(f["a"] - (1 / 61 + 1 / 62)) < 1e-12 and f["a"] == f["b"]


def test_lru_evicts_oldest():
    c = LRUCache(2)
    c.put(1, "a"); c.put(2, "b"); c.get(1); c.put(3, "c")
    assert c.get(2) is None and c.get(1) == "a"


def _hits():
    return [Hit(text="식별코드: EDU_1\n교육과정: 엑셀", score=0.9, metadata={"doc_title": "t"})]


def test_validate_codes_strips_fabricated():
    text, ok, bad = qa.validate_codes("추천 [식별코드: EDU_1] 그리고 [식별코드: FAKE_9]", _hits())
    assert ok == ["EDU_1"] and bad == ["FAKE_9"] and "FAKE_9" not in text


class _Overload(Exception):
    status_code = 503


class _FakeClient:
    def __init__(self, behaviors):
        self.behaviors, self.calls = behaviors, []
        self.messages = SimpleNamespace(stream=self._stream)

    def _stream(self, model, **kw):
        self.calls.append(model)
        beh = self.behaviors[model]
        outer = self

        class Ctx:
            def __enter__(s):
                if isinstance(beh, Exception):
                    raise beh
                return SimpleNamespace(text_stream=iter(beh))

            def __exit__(s, *a):
                return False
        return Ctx()


def test_fallback_to_next_model_on_503():
    cl = _FakeClient({"m1": _Overload(), "m2": ["안녕", "하세요"]})
    out = list(qa._stream_models(cl, ["m1", "m2"], "s", "u"))
    assert cl.calls == ["m1", "m2"] and ("delta", "안녕") in out and out[-1] == ("model", "m2")


def test_all_models_down_raises():
    cl = _FakeClient({"m1": _Overload(), "m2": _Overload()})
    try:
        list(qa._stream_models(cl, ["m1", "m2"], "s", "u"))
        assert False
    except _Overload:
        pass


def test_graceful_fallback_lists_sources():
    assert "검색된 근거 1건" in qa.fallback_answer(_hits())


def test_model_chain_dedup():
    assert llm_models(RagSettings(llm_model="a", llm_chain="a,b")) == ["a", "b"]


def test_qna_db_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "q.db"
        pid = qna_db.save_post("엑셀 과정?", "답", ["EDU_1"], "m", p)
        assert qna_db.list_posts("엑셀", path=p)[0]["id"] == pid
        assert qna_db.get_post(pid, path=p)["views"] == 1
        assert qna_db.get_post(pid, path=p)["recommended_codes"] == ["EDU_1"]
        assert qna_db.delete_post(pid, path=p) and not qna_db.list_posts(path=p)

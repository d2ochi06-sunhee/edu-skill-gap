"""Streamlit Community Cloud 배포용 진입점: HR 커리어 대시보드 + 자료 기반 챗봇(BM25 경량 검색).

배포 설정: Main file path = deploy/streamlit_app.py  (이 폴더의 requirements.txt 가 설치됨)
Secrets  : GEMINI_API_KEY = "발급받은 키"
"""
import os
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    for _k in ("GEMINI_API_KEY", "RAG_DASHBOARD"):
        if _k in st.secrets:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass
os.environ.setdefault("RAG_DASHBOARD", "hr_career_platform_v2_2026-11-21_rag_clean.html")
os.environ.setdefault("RAG_MODE", "lite")

from src.rag.config import get_llm_key, get_settings  # noqa: E402
from src.rag.qa import stream_answer  # noqa: E402
from src.rag.store import latest_dashboard  # noqa: E402
from src.rag.store_lite import LiteStore  # noqa: E402

MAX_QUESTIONS_PER_SESSION = 30      # LLM API 비용·한도 보호

st.set_page_config(page_title="HR 커리어 플랫폼", page_icon="💼", layout="wide")


@st.cache_resource(show_spinner="자료 색인을 준비하는 중…")
def get_store() -> LiteStore:
    store = LiteStore(get_settings())
    store.sync()
    return store


@st.cache_data(show_spinner=False)
def load_dashboard_html() -> str:
    html = latest_dashboard().read_text(encoding="utf-8")
    # 내장 챗봇 위젯은 별도 서버(/api)가 필요하므로 숨기고, 아래 '자료 챗봇' 탭을 사용합니다.
    return html.replace("</head>", "<style>.rag-fab,.rag-panel{display:none!important}</style></head>", 1)


tab_dash, tab_chat = st.tabs(["📊 커리어 진단 대시보드", "💬 자료 챗봇"])

with tab_dash:
    if hasattr(st, "iframe"):       # 최신 Streamlit (components.html 은 제거 예정)
        st.iframe(load_dashboard_html(), height=2600)
    else:
        components.html(load_dashboard_html(), height=2600, scrolling=True)

with tab_chat:
    st.subheader("자료 기반 질문")
    st.caption("수집된 교육과정·NCS 자료에서 찾은 내용으로만 답합니다. 자료에 없는 질문은 답하지 않아요. "
               "질문은 Google Gemini API로 전송되니 이름 등 개인정보는 입력하지 마세요.")
    if not get_llm_key():
        st.warning("GEMINI_API_KEY 가 설정되지 않아 답변 대신 검색된 근거만 보여 드립니다.")

    st.session_state.setdefault("chat", [])
    st.session_state.setdefault("asked", 0)
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])
            if msg.get("sources"):
                with st.expander(f"근거 {len(msg['sources'])}건"):
                    for s in msg["sources"]:
                        st.markdown(f"**[{s['n']}] {s['title']}**" + (f" · p.{s['page']}" if s["page"] else ""))
                        st.caption(s["snippet"])

    question = st.chat_input("예) 채용 면접 교육과정 추천해줘")
    if question:
        st.session_state.chat.append({"role": "user", "text": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            if st.session_state.asked >= MAX_QUESTIONS_PER_SESSION:
                result = {"answer": "이번 접속에서 가능한 질문 횟수를 모두 사용했어요.", "sources": []}
                st.markdown(result["answer"])
            else:
                st.session_state.asked += 1
                result = {}

                def deltas():
                    for ev in stream_answer(get_store(), get_settings(), question[:1000], top_k=5):
                        if ev["type"] == "delta":
                            yield ev["text"]
                        else:
                            result.update(ev)

                streamed = st.write_stream(deltas())
                if not streamed:            # 스트림 없이 끝난 경우(자료 없음·API 키 없음·장애 대체 답변)
                    st.markdown(result.get("answer", ""))
                elif result.get("answer") and result["answer"] != streamed:
                    st.markdown(result["answer"])    # 검증으로 정리된 최종 답변이 다르면 교체 표시
                if result.get("sources"):
                    with st.expander(f"근거 {len(result['sources'])}건"):
                        for s in result["sources"]:
                            st.markdown(f"**[{s['n']}] {s['title']}**" + (f" · p.{s['page']}" if s["page"] else ""))
                            st.caption(s["snippet"])
        st.session_state.chat.append({"role": "assistant", "text": result.get("answer", ""),
                                      "sources": result.get("sources", [])})

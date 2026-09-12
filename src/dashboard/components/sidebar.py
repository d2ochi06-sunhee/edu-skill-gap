"""
Streamlit 사이드바 컴포넌트
- 기본 직무 필터링
- 성인학습자/재직자 대상 필터링
- 공공데이터포털 API 연동 상태
"""
import streamlit as st

def render_sidebar(categories, targets):
    with st.sidebar:
        st.markdown("### 🏛️ 대학평생교육원 EDA")
        st.markdown("**수도권 기본직무 마이크로디그리**")
        st.markdown("---")
        
        selected_category = st.selectbox(
            "📋 분석 대상 기본직무",
            options=["전체"] + list(categories)
        )
        
        selected_target = st.selectbox(
            "👥 타겟 학습자 그룹",
            options=["전체"] + list(targets)
        )
        
        st.markdown("---")
        st.markdown("#### 🔗 수도권 공공데이터 API 연동")
        st.markdown("""
        - <span style="background-color:#DEF7EC;color:#03543F;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:600;">연동</span> **한국산업인력공단 NCS**
        - <span style="background-color:#DEF7EC;color:#03543F;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:600;">연동</span> **국가평생교육진흥원 K-MOOC**
        - <span style="background-color:#E1EFFE;color:#1E429F;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:600;">준비</span> **원격훈련 모니터링통계**
        - <span style="background-color:#DEF7EC;color:#03543F;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:600;">등록</span> **서울시 평생학습포털**
        - <span style="background-color:#DEF7EC;color:#03543F;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:600;">등록</span> **경기데이터드림**
        """, unsafe_allow_html=True)
        st.caption("🔑 `.env` 보안 환경변수 관리 중")
        
        st.markdown("---")
        st.info("💡 **팀 협업 포인트**:\n평일 온라인(K-MOOC)과 주말 대학평생교육원(실습)의 연계 비율을 탭3과 탭4에서 확인해보세요!")
        
        return selected_category, selected_target

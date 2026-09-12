"""
수도권 대학평생교육원 연계 마이크로디그리 & 하이브리드 재교육 EDA 대시보드
Main Entrypoint
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# 프로젝트 루트 경로 등록
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config.settings import SAMPLE_DATA_DIR, BASIC_JOB_FIELDS
from src.processors.analyzer import EduDataAnalyzer
from src.dashboard.components.sidebar import render_sidebar
from src.dashboard.components.metrics import render_kpi_metrics
from src.dashboard.tabs.tab1_ncs import render_tab1
from src.dashboard.tabs.tab2_kmooc import render_tab2
from src.dashboard.tabs.tab3_remote import render_tab3
from src.dashboard.tabs.tab4_builder import render_tab4

# 1. 페이지 설정 및 모던 스타일링
st.set_page_config(
    page_title="대학평생교육원 기본직무 마이크로디그리 EDA",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E40AF, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #475569;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 2. 데이터 로드 (캐싱 적용)
@st.cache_data
def load_all_data():
    df_ncs = pd.read_csv(SAMPLE_DATA_DIR / "ncs_curriculums.csv")
    df_kmooc = pd.read_csv(SAMPLE_DATA_DIR / "kmooc_courses.csv")
    df_stats = pd.read_csv(SAMPLE_DATA_DIR / "remote_learning_stats.csv")
    return df_ncs, df_kmooc, df_stats

df_ncs, df_kmooc, df_stats = load_all_data()
analyzer = EduDataAnalyzer(df_ncs, df_kmooc, df_stats)

# 3. 사이드바 렌더링
categories = BASIC_JOB_FIELDS
targets = df_stats["target_group"].unique()
selected_category, selected_target = render_sidebar(categories, targets)

# 필터링 적용
filtered_ncs = df_ncs if selected_category == "전체" else df_ncs[df_ncs["category"] == selected_category]
filtered_kmooc = df_kmooc if selected_category == "전체" else df_kmooc[df_kmooc["category"] == selected_category]
filtered_stats = df_stats if selected_target == "전체" else df_stats[df_stats["target_group"] == selected_target]

# 4. 헤더 영역
st.markdown('<div class="main-title">수도권 대학평생교육원 기반 기본직무 마이크로디그리 & 하이브리드 재교육 EDA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">한국산업인력공단 NCS(기본직무) · 국가평생교육진흥원 K-MOOC(대학평생교육원) · 원격훈련모니터링 통계 기반 산학 재교육 탐색 대시보드</div>', unsafe_allow_html=True)

# 5. KPI 메트릭 카드 렌더링
render_kpi_metrics(filtered_ncs, filtered_kmooc, filtered_stats)
st.markdown("<br>", unsafe_allow_html=True)

# 6. 4대 분석 탭 네비게이션
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. [NCS 표준] 기본직무 역량 체계",
    "🏫 2. [대학 자원] 평생교육원 K-MOOC & Gap 분석",
    "📈 3. [운영 모델] 원격훈련 통계 & 하이브리드 비율",
    "🚀 4. [설계기] 평생교육 마이크로디그리 패키징"
])

with tab1:
    render_tab1(filtered_ncs)

with tab2:
    render_tab2(filtered_kmooc, analyzer)

with tab3:
    render_tab3(filtered_stats)

with tab4:
    render_tab4(analyzer, categories)

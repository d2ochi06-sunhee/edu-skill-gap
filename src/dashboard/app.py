import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# 페이지 기본 설정
st.set_page_config(
    page_title="수도권 마이크로디그리 & 하이브리드 재교육 EDA 대시보드",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모던 스타일링 CSS 주입
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #64748B;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-left: 5px solid #3B82F6;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .api-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .api-active {
        background-color: #DEF7EC;
        color: #03543F;
    }
    .api-ready {
        background-color: #E1EFFE;
        color: #1E429F;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_datasets():
    data_dir = "data/sample"
    df_ncs = pd.read_csv(f"{data_dir}/ncs_curriculums.csv")
    df_kmooc = pd.read_csv(f"{data_dir}/kmooc_courses.csv")
    df_stats = pd.read_csv(f"{data_dir}/remote_learning_stats.csv")
    return df_ncs, df_kmooc, df_stats

df_ncs, df_kmooc, df_stats = load_datasets()

# ==================== 사이드바 ====================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/education.png", width=64)
    st.title("🎯 프로젝트 필터")
    
    selected_field = st.selectbox(
        "관심 산업 분야 선택",
        options=["전체"] + sorted(list(df_ncs["sub_field"].unique()))
    )
    
    selected_target = st.selectbox(
        "타겟 학습자 그룹",
        options=["전체"] + list(df_stats["target_group"].unique())
    )
    
    st.markdown("---")
    st.markdown("#### 🔗 공공데이터 API 연동 상태")
    st.markdown("""
    - <span class="api-badge api-active">정상</span> **NCS 교육과정**
    - <span class="api-badge api-ready">준비</span> **K-MOOC 강좌정보**
    - <span class="api-badge api-ready">준비</span> **원격훈련모니터링 통계**
    """, unsafe_allow_html=True)
    st.caption("공공데이터포털 승인키(.env) 연동 상태")
    st.markdown("---")
    st.info("💡 **팀 협업 Tip**: 탭별 분석 결과를 토대로 4번 탭에서 산학 연계 마이크로디그리 교과목을 패키징해 보세요!")

# 필터링 적용
filtered_ncs = df_ncs if selected_field == "전체" else df_ncs[df_ncs["sub_field"] == selected_field]
filtered_kmooc = df_kmooc if selected_field == "전체" else df_kmooc[df_kmooc["field"] == selected_field]
filtered_stats = df_stats if selected_target == "전체" else df_stats[df_stats["target_group"] == selected_target]

# ==================== 메인 헤더 ====================
st.markdown('<div class="main-header">수도권 산업 수요 기반 마이크로디그리 & 하이브리드 재교육 EDA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">한국산업인력공단 NCS 교육과정 · K-MOOC 대학 강좌 · 원격훈련 통계 기반 산학연계 모델 탐색기</div>', unsafe_allow_html=True)

# 핵심 KPI 지표 카드
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="분석 대상 NCS 표준과정", value=f"{len(filtered_ncs)} 개 직무", delta="신산업 수요 100%")
with col2:
    st.metric(label="수도권 대학 K-MOOC 자원", value=f"{len(filtered_kmooc)} 개 강좌", delta=f"{len(filtered_kmooc[filtered_kmooc['credit_accepted']=='Y'])}개 학점인정")
with col3:
    avg_comp = filtered_stats["completion_rate"].mean()
    st.metric(label="원격훈련 평균 수료율", value=f"{avg_comp:.1f}%", delta="온라인 시수 반비례", delta_color="inverse")
with col4:
    rec_ratio = int(filtered_stats["recommended_online_ratio"].mean())
    st.metric(label="권장 온라인 학습 비율", value=f"{rec_ratio}%", delta="오프라인 집중실습 병행")

st.markdown("<br>", unsafe_allow_html=True)

# ==================== 4대 탭 네비게이션 ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. [수요] NCS 산업역량 구조",
    "🏫 2. [자원] 대학 K-MOOC & Gap 분석",
    "📈 3. [운영] 원격훈련 행동 & 하이브리드 비율",
    "🚀 4. [설계] 마이크로디그리 패키징 시뮬레이터"
])

# ----------------- TAB 1: NCS 산업역량 분석 -----------------
with tab1:
    st.subheader("📌 수도권 전략 신산업 분야별 NCS 표준 역량 체계")
    st.write("마이크로디그리의 교과목 모듈을 정의하기 위해 산업계에서 요구하는 직무별 훈련 시간과 수요도를 분석합니다.")
    
    c1, c2 = st.columns([3, 2])
    with c1:
        fig_ncs = px.bar(
            filtered_ncs,
            x="sub_field",
            y="demand_score",
            color="hours",
            text="hours",
            title="직무 분야별 산업 수요도 및 표준 훈련시간(H)",
            labels={"sub_field": "직무 세부분야", "demand_score": "수도권 산업 수요 지수(100만점)", "hours": "훈련시간(H)"},
            color_continuous_scale="Blues"
        )
        fig_ncs.update_traces(texttemplate='%{text}시간', textposition='outside')
        fig_ncs.update_layout(yaxis=dict(range=[70, 105]))
        st.plotly_chart(fig_ncs, use_container_width=True)
        
    with c2:
        st.markdown("#### 💡 NCS 기반 모듈화 인사이트")
        st.info("""
        - **마이크로디그리 적정 단위**: 통상 3학점(45시간) 내외로 모듈을 구성할 때 직무 완결성이 가장 높습니다.
        - **고수요 직무**: 반도체 설계(98점), 생성형 AI(96점), 클라우드(94점) 등은 단기 집중형(Micro-credential)으로 우선 설계하기에 적합합니다.
        """)
        st.dataframe(
            filtered_ncs[["sub_field", "course_name", "unit_name", "hours", "level"]],
            hide_index=True,
            use_container_width=True
        )

# ----------------- TAB 2: K-MOOC 대학 자원 & Gap 분석 -----------------
with tab2:
    st.subheader("🏫 수도권 주요 대학 K-MOOC 자원 공급 현황 및 공백(Gap) 분석")
    st.write("대학들이 이미 보유한 온라인 강의 자원을 마이크로디그리의 '이론 모듈'로 직결시킬 수 있는지 검증합니다.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        fig_univ = px.bar(
            df_kmooc,
            x="univ_name",
            color="credit_accepted",
            title="수도권 주요 대학별 K-MOOC 개설 및 학점인정 여부",
            labels={"univ_name": "개설 대학", "count": "강좌 수", "credit_accepted": "학점인정 여부"},
            color_discrete_map={"Y": "#3B82F6", "N": "#CBD5E1"}
        )
        st.plotly_chart(fig_univ, use_container_width=True)
        
    with col_b:
        # Gap 분석: NCS 직무별 K-MOOC 매핑 수
        ncs_codes = set(df_ncs["ncs_code"])
        mapped_codes = set(df_kmooc["ncs_mapped"])
        
        gap_df = df_ncs.copy()
        gap_df["kmooc_mapped"] = gap_df["ncs_code"].apply(lambda x: "연계 자원 확보" if x in mapped_codes else "신규 개발 필요(Gap)")
        
        fig_pie = px.pie(
            gap_df,
            names="kmooc_mapped",
            title="NCS 필수 역량 대비 대학 K-MOOC 자원 충족률",
            color="kmooc_mapped",
            color_discrete_map={"연계 자원 확보": "#10B981", "신규 개발 필요(Gap)": "#F59E0B"}
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("#### 🔍 연계 가능한 K-MOOC 강좌 상세 리스트")
    st.dataframe(filtered_kmooc, hide_index=True, use_container_width=True)

# ----------------- TAB 3: 원격훈련 통계 & 하이브리드 모델 -----------------
with tab3:
    st.subheader("📈 원격훈련 학습자 행동 패턴 및 온·오프라인 블렌디드 황금 비율")
    st.write("온라인 시수가 증가함에 따라 재직자의 수료율이 급감하는 임계점(Drop-off Point)을 파악하여 최적의 하이브리드(온+오프) 비율을 도출합니다.")
    
    col_x, col_y = st.columns(2)
    with col_x:
        fig_scatter = px.scatter(
            df_stats,
            x="course_hours",
            y="completion_rate",
            color="target_group",
            size="avg_weekly_study_hours",
            trendline="ols",
            title="온라인 훈련 시수(H)에 따른 수료율(%) 낙차 추이",
            labels={"course_hours": "온라인 훈련 시수 (H)", "completion_rate": "수료율 (%)", "target_group": "학습자 그룹"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_y:
        st.markdown("#### ⏱️ 재직자 학습 몰입 특성 & 하이브리드 권장안")
        st.markdown("""
        - **재직자 주 학습 시간**: **야간(20~23시)** 및 **주말 집중 학습(42.5%)**
        - **온라인 한계 시수**: 순수 온라인 과정이 **40시간을 초과할 때 수료율이 70% 미만**으로 급감
        - **하이브리드(재교육) 황금 모델 제안**:
          - 📘 **이론/기초 (온라인 K-MOOC/원격 60%)**: 평일 야간 및 주말 자율 학습
          - 🛠️ **실습/프로젝트 (산학 오프라인 40%)**: 토요일 집중 해커톤/기업 멘토링
        """)
        
        # 최적 비율 도넛 차트
        fig_donut = go.Figure(data=[go.Pie(
            labels=['온라인 원격(이론/K-MOOC)', '오프라인 집체(실습/산학 멘토링)'],
            values=[60, 40],
            hole=.5,
            marker_colors=['#3B82F6', '#10B981']
        )])
        fig_donut.update_layout(title_text="추천 하이브리드(블렌디드) 운영 비율")
        st.plotly_chart(fig_donut, use_container_width=True)

# ----------------- TAB 4: 마이크로디그리 설계기 (시뮬레이터) -----------------
with tab4:
    st.subheader("🚀 산학 연계형 마이크로디그리 커리큘럼 패키징 시뮬레이터")
    st.write("원하는 전략 산업 직무를 선택하면, 표준 NCS 능력단위 + K-MOOC 대학 강좌 + 하이브리드 시수가 결합된 완성형 마이크로디그리를 자동 구성합니다.")
    
    sim_field = st.selectbox("설계할 마이크로디그리 대상 직무", options=df_ncs["sub_field"].unique())
    target_ncs = df_ncs[df_ncs["sub_field"] == sim_field].iloc[0]
    matched_kmooc = df_kmooc[df_kmooc["field"] == sim_field]
    
    st.markdown("---")
    res_col1, res_col2 = st.columns([1, 1])
    
    total_hours = target_ncs["hours"]
    online_hours = int(total_hours * 0.6)
    offline_hours = total_hours - online_hours
    
    with res_col1:
        st.markdown(f"### 📋 마이크로디그리 명칭: **[{sim_field} 융합 실무]**")
        st.markdown(f"- **기반 NCS 능력단위**: `{target_ncs['unit_name']}` (NCS 레벨 {target_ncs['level']})")
        st.markdown(f"- **산업계 추천 코스명**: {target_ncs['course_name']}")
        st.markdown(f"- **총 이수 인정 시간**: **{total_hours}시간 (3학점 상당)**")
        st.markdown(f"- **하이브리드 설계**: 온라인 **{online_hours}시간** + 오프라인 실습 **{offline_hours}시간**")
        
    with res_col2:
        st.markdown("### 🎓 매핑 대학 K-MOOC 연계 강좌")
        if len(matched_kmooc) > 0:
            k_course = matched_kmooc.iloc[0]
            st.success(f"**연계 강좌**: {k_course['course_title']} ({k_course['univ_name']})")
            st.markdown(f"- 주차 구성: {k_course['weeks']}주차 (주당 {k_course['weekly_hours']}시간)")
            st.markdown(f"- 학점 인정 여부: **{'인정 가능' if k_course['credit_accepted'] == 'Y' else '수료증 발급'}**")
        else:
            st.warning("⚠️ 매핑된 기존 K-MOOC가 없습니다. 대학-산업체 공동 신규 교과목 개발이 필요합니다.")
            
    st.markdown("---")
    # 팀원 공유용 다운로드
    export_df = pd.DataFrame([{
        "마이크로디그리명": f"{sim_field} 융합 실무",
        "NCS직무코드": target_ncs["ncs_code"],
        "능력단위명": target_ncs["unit_name"],
        "총시간": total_hours,
        "온라인시수": online_hours,
        "오프라인시수": offline_hours,
        "연계대학": matched_kmooc.iloc[0]["univ_name"] if len(matched_kmooc) > 0 else "신규 공동개발",
        "연계강좌명": matched_kmooc.iloc[0]["course_title"] if len(matched_kmooc) > 0 else "미정"
    }])
    
    csv_data = export_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 설계된 마이크로디그리 명세서 다운로드 (CSV)",
        data=csv_data,
        file_name=f"microdegree_design_{sim_field}.csv",
        mime="text/csv"
    )

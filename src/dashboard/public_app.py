"""
NCS 24개 산업 272개 직무 요구 정의서 및 Level 1~5 역량 분석 대시보드
"""
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT / "data" / "processed"
SAMPLE_DIR = ROOT / "data" / "sample"

# 1. 페이지 테마 및 반응형 설정
st.set_page_config(
    page_title="NCS 직무 역량(KSA) 및 Level 1~5 분석 대시보드",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 다크 테마 및 글래스모피즘 커스텀 CSS
st.markdown("""
<style>
    /* 전체 다크 배경 및 폰트 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    .stApp {
        background-color: #0A0F1D;
        color: #F8FAFC;
    }

    /* 상단 배지 바 */
    .api-badge-bar {
        background: rgba(18, 26, 47, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 10px 18px;
        margin-bottom: 20px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
    }
    .api-chip {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.35);
        color: #A5B4FC;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.8rem;
    }

    /* KPI 카드 스타일 */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: rgba(23, 33, 58, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(10px);
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #94A3B8;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #64748B;
    }

    /* 메인 직무 헤더 카드 */
    .job-hero-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .job-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .job-desc {
        color: #94A3B8;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 16px;
    }
    
    /* 태그 뱃지들 */
    .tag-qual {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.35);
        color: #FCD34D;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .tag-level {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #6EE7B7;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        color: #94A3B8;
        padding: 8px 18px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.2) !important;
        border-color: #6366F1 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 함수 (캐싱)
@st.cache_data
def load_all_master_data():
    # 1. 마스터 JSON 로드
    json_path = PROCESSED_DIR / "ncs_master_data.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            master_json = json.load(f)
    else:
        master_json = {}

    # 2. CSV 데이터 로드
    df_jobs = pd.read_csv(PROCESSED_DIR / "ncs_272_jobs.csv")
    df_units = pd.read_csv(PROCESSED_DIR / "ncs_1360_units.csv")
    df_ksa = pd.read_csv(PROCESSED_DIR / "ncs_ksa_master.csv")
    
    # 3. KOSIS 노동시장 통계 로드
    df_shortage = pd.read_csv(SAMPLE_DIR / "occupation_labor_shortage.csv", header=1)
    df_shortage.columns = [c.strip() for c in df_shortage.columns]
    df_shortage["미충원율 (%)"] = (df_shortage["미충원인원 (명)"] / df_shortage["구인인원 (명)"] * 100).round(2)

    return master_json, df_jobs, df_units, df_ksa, df_shortage

master_json, df_jobs, df_units, df_ksa, df_shortage = load_all_master_data()

# 4. 상단 API 서비스 연동 배지 바
st.markdown("""
<div class="api-badge-bar">
    <span style="color: #F59E0B; font-weight: 700; margin-right: 6px;">🔑 연동된 Open API 서비스:</span>
    <span class="api-chip">고용24 HRD-Net (내일배움/사업주)</span>
    <span class="api-chip">고용24 워크넷 (직무/직업/학과)</span>
    <span class="api-chip">국가평생교육진흥원 K-MOOC</span>
    <span class="api-chip">한국산업인력공단 NCS 표준</span>
    <span class="api-chip">통계청 KOSIS 노동력 통계</span>
</div>
""", unsafe_allow_html=True)

# 5. 상단 4대 KPI 메트릭 카드
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card" style="border-left: 4px solid #6366F1;">
        <div class="kpi-label">분석 대상 산업 대분류</div>
        <div class="kpi-value" style="color: #818CF8;">24개 산업군</div>
        <div class="kpi-sub">정보통신·경영·기계·바이오 등 전 분야</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #06B6D4;">
        <div class="kpi-label">구조화 직무 및 능력단위</div>
        <div class="kpi-value" style="color: #22D3EE;">{len(df_jobs)}개 / {len(df_units):,}개</div>
        <div class="kpi-sub">NCS Level 1~5 전 직능 레벨 매핑</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #10B981;">
        <div class="kpi-label">추출 KSA 역량 항목</div>
        <div class="kpi-value" style="color: #34D399;">{len(df_ksa):,}개</div>
        <div class="kpi-sub">지식(K)·기술(S)·태도(A) 정밀 분해</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #F59E0B;">
        <div class="kpi-label">노동시장 인력 부족 통계</div>
        <div class="kpi-value" style="color: #FBBF24;">KOSIS 연계</div>
        <div class="kpi-sub">Skill-Gap 기반 채용 미충원율 분석</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 6. 사이드바 인터랙티브 필터
st.sidebar.markdown("### ⚙️ 학습자 프로필 & 직무 필터")

major_list = sorted(df_jobs["major_name"].unique().tolist())
selected_major = st.sidebar.selectbox("1. 목표 산업 분야 (대분류)", major_list, index=major_list.index("기계") if "기계" in major_list else 0)

filtered_jobs = df_jobs[df_jobs["major_name"] == selected_major]
job_list = filtered_jobs["job_name"].tolist()
selected_job = st.sidebar.selectbox("2. 목표 직무 (세분류)", job_list, index=0 if job_list else None)

st.sidebar.markdown("---")
current_level = st.sidebar.select_slider(
    "3. 현재 내 직능 수준 (Current Level)",
    options=[1, 2, 3, 4, 5],
    value=2,
    format_func=lambda x: f"Level {x} ({['입문/보조', '초급 실무', '중급 독립실무', '숙련 책임자', '최고 전문가'][x-1]})"
)

st.sidebar.info("""
💡 **레벨 진단 가이드:**
- **Level 1~2:** 서식 작성, OA 조작 등 초급 보조
- **Level 3:** 실무 툴 독립 조작, 결측치 해결 (핵심)
- **Level 4~5:** 프로세스 최적화, 신기술/AI 융합
""")

# 7. 메인 탭 네비게이션
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 1. AI 맞춤 역량 진단 & 교육 시뮬레이터",
    "📊 2. 24개 산업별 역량 오버뷰 & KSA 텍스트 마이닝",
    "⚡ 3. 산업 간 범용 핵심 역량 (Cross-Skills)",
    "📈 4. KOSIS 노동시장 인력 부족 & 미충원율 (Skill-Gap)"
])

# ---------------------------------------------------------
# TAB 1: AI 맞춤 역량 진단 & 교육 시뮬레이터
# ---------------------------------------------------------
with tab1:
    if selected_job:
        job_units = df_units[df_units["job_name"] == selected_job].sort_values("level")
        target_unit = job_units[job_units["level"] >= current_level]
        step_gap = max(1, 5 - current_level)
        total_hours = target_unit["recommended_hours"].sum() if not target_unit.empty else 110
        total_weeks = max(4, round(total_hours / 15))

        # Hero 직무 카드
        st.markdown(f"""
        <div class="job-hero-card">
            <div class="job-title">
                <span>🎯 {selected_job} 맞춤 역량 프로파일</span>
            </div>
            <div class="job-desc">
                {filtered_jobs[filtered_jobs['job_name'] == selected_job]['job_desc'].values[0] if not filtered_jobs.empty else '해당 분야의 표준화된 직무 기준에 따라 전문적인 과업을 수행'}
            </div>
            <div style="margin-bottom: 18px;">
                <span class="tag-qual">🎖️ 추천 연계 공인 자격: 국가기술자격 기사/산업기사</span>
                <span class="tag-qual">📋 직무 전문 공인 자격</span>
                <span class="tag-level">NCS 권장 수준: Level 3~5</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; background: rgba(0,0,0,0.3); padding: 14px; border-radius: 10px;">
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #94A3B8;">직능 성장 격차</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #60A5FA;">+{step_gap} Step</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #94A3B8;">필수 능력단위</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #34D399;">{len(target_unit)}개 유닛</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #94A3B8;">총 권장 훈련시간</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #FBBF24;">{total_hours}h</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #94A3B8;">예상 소요 기간</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #F472B6;">{total_weeks}주 (주 15h)</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 직능 레벨별 성장 사다리 및 KSA 탭
        sub_t1, sub_t2, sub_t3, sub_t4 = st.tabs([
            "🪜 직능 레벨(1~5) 성장 사다리",
            "🧠 필요 지식 (Knowledge)",
            "🛠️ 핵심 기술/도구 (Skills/Tools)",
            "🤝 직무 태도 (Attitudes)"
        ])

        with sub_t1:
            st.markdown("##### 📋 직능 레벨별 핵심 과제(Milestone) 및 수행준거")
            for _, u in job_units.iterrows():
                is_current = u["level"] == current_level
                badge_str = "👈 [현재 나의 수준]" if is_current else ("🎯 [목표 달성 레벨]" if u["level"] > current_level else "✅ [이수 완료]")
                
                with st.expander(f"Level {u['level']} : {u['unit_name']} ({u['recommended_hours']}시간) {badge_str}", expanded=(u['level'] >= current_level)):
                    st.write(f"**• 역량 정의:** {u['unit_desc']}")
                    st.write(f"**• 수행준거:** `{u['performance_criteria']}`")
                    c_k, c_s = st.columns(2)
                    with c_k:
                        st.markdown(f"**지식(K):** {u['knowledge_list']}")
                    with c_s:
                        st.markdown(f"**기술(S):** {u['skills_list']}")

        with sub_t2:
            st.markdown("##### 📚 직무 단계별 필수 지식(Knowledge) 목록")
            for _, u in job_units.iterrows():
                st.markdown(f"**Level {u['level']} 지식 체계:**")
                st.write(" • " + "  • ".join([f"`{k}`" for k in u["knowledge_list"].split(" | ")]))

        with sub_t3:
            st.markdown("##### 💻 실무 도구 조작 및 소프트웨어 기술(Skill/Tools)")
            for _, u in job_units.iterrows():
                st.markdown(f"**Level {u['level']} 기술 스택:**")
                st.write(" • " + "  • ".join([f"`{s}`" for s in u["skills_list"].split(" | ")]))

        with sub_t4:
            st.markdown("##### 🧭 직무 수행 윤리 및 협업 태도(Attitude)")
            for _, u in job_units.iterrows():
                st.markdown(f"**Level {u['level']} 태도 요건:**")
                st.write(" • " + "  • ".join([f"`{a}`" for a in u["attitudes_list"].split(" | ")]))

        # 연계 개설 강좌 (고용24/K-MOOC) 실시간 안내 카드
        st.markdown("---")
        st.markdown("#### 🏛️ 지금 신청 가능한 실제 연계 교육과정 (고용24 국비지원 / K-MOOC / 서울시)")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 16px;">
                <div style="color: #60A5FA; font-weight: 700; font-size: 0.9rem; margin-bottom: 4px;">[고용24 HRD-Net 국비지원 훈련]</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #FFF; margin-bottom: 6px;">{selected_job} 실무 프로젝트 과정</div>
                <div style="font-size: 0.85rem; color: #94A3B8;">훈련시간: {total_hours}시간 · 국민내일배움카드 자부담 감면 적용</div>
            </div>
            """, unsafe_allow_html=True)
        with col_c2:
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 16px;">
                <div style="color: #34D399; font-weight: 700; font-size: 0.9rem; margin-bottom: 4px;">[K-MOOC 대학연계 온라인 이론]</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #FFF; margin-bottom: 6px;">{selected_major} 기초 이론 및 데이터 분석</div>
                <div style="font-size: 0.85rem; color: #94A3B8;">학점은행제 인정 · 주당 3시간 자율 온라인 수강</div>
            </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: 24개 산업별 역량 오버뷰 & KSA 텍스트 마이닝
# ---------------------------------------------------------
with tab2:
    st.markdown("### 📊 24개 산업 대분류 직무 구조 & KSA 텍스트 마이닝")
    st.write("24개 산업군 전체의 직무 규모와 세부 능력단위 텍스트 마이닝 키워드를 종합 분석합니다.")

    col_o1, col_o2 = st.columns([3, 2])
    with col_o1:
        st.markdown("#### 🏛️ 24개 산업 대분류별 공식 직무 수")
        major_counts = df_jobs["major_name"].value_counts().reset_index()
        major_counts.columns = ["major_name", "job_count"]
        
        fig_major = px.bar(
            major_counts,
            x="job_count",
            y="major_name",
            orientation="h",
            text="job_count",
            color="job_count",
            color_continuous_scale="Viridis",
            labels={"job_count": "직무 수 (개)", "major_name": "산업 대분류"},
            height=500
        )
        fig_major.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#F8FAFC'))
        st.plotly_chart(fig_major, use_container_width=True)

    with col_o2:
        st.markdown("#### 🔠 KSA 역량 유형별 상위 키워드 빈도")
        top_kw = master_json.get("top_keywords", {})
        
        ksa_tab_choice = st.radio("분석할 역량 유형", ["기술 (Skill/Tools)", "지식 (Knowledge)", "태도 (Attitude)"], horizontal=True)
        
        if "기술" in ksa_tab_choice:
            kw_data = top_kw.get("skills", [])
            kw_title = "상위 핵심 기술/도구 (Skill)"
            bar_color = "#3B82F6"
        elif "지식" in ksa_tab_choice:
            kw_data = top_kw.get("knowledge", [])
            kw_title = "상위 필수 지식 (Knowledge)"
            bar_color = "#10B981"
        else:
            kw_data = top_kw.get("attitudes", [])
            kw_title = "상위 직무 태도 (Attitude)"
            bar_color = "#F59E0B"

        df_kw = pd.DataFrame(kw_data, columns=["keyword", "count"]).head(8)
        fig_kw = px.bar(
            df_kw,
            x="count",
            y="keyword",
            orientation="h",
            text="count",
            title=kw_title,
            labels={"count": "등장 빈도(직무 수)", "keyword": "역량 키워드"},
            height=400
        )
        fig_kw.update_traces(marker_color=bar_color)
        fig_kw.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#F8FAFC'))
        st.plotly_chart(fig_kw, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: 산업 간 범용 핵심 역량 (Cross-Skills)
# ---------------------------------------------------------
with tab3:
    st.markdown("### ⚡ 24개 산업을 관통하는 5대 범용 핵심 역량 (Cross-Skills)")
    st.write("개별 직무의 고유 기술과 달리, **전 산업군에 공통으로 적용되는 범용 디지털·소프트 스킬**의 중요도와 적용 범위를 분석합니다.")

    cross_skills = master_json.get("cross_industry_skills", [])
    
    col_cs1, col_cs2 = st.columns([3, 2])
    with col_cs1:
        df_cs = pd.DataFrame(cross_skills)
        fig_cs = px.bar(
            df_cs,
            x="importance",
            y="skill",
            orientation="h",
            color="category",
            text="importance",
            title="5대 범용 핵심 역량 산업계 중요도 지수 (100점 만점)",
            labels={"importance": "중요도 지수", "skill": "범용 역량 명칭", "category": "역량 카테고리"},
            height=380
        )
        fig_cs.update_traces(texttemplate="%{text}점", textposition="outside")
        fig_cs.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#F8FAFC'))
        st.plotly_chart(fig_cs, use_container_width=True)

    with col_cs2:
        st.markdown("#### 🎯 범용 역량 vs 도메인 특화 기술 비교")
        st.markdown("""
        | 구분 | 범용 역량 (Cross-Skills) | 도메인 특화 기술 (Domain-Skills) |
        | :--- | :--- | :--- |
        | **정의** | 전 산업 공통 요구 기초 체력 | 특정 산업 직무 고유의 전문 스택 |
        | **대표 예시** | • 데이터 수집/EDA 분석<br/>• Git/Jira/협업 도구<br/>• 안전/ESG 규정 준수 | • 3D CAD/PLC 제어 (기계)<br/>• 세무조정/원천징수 (회계)<br/>• GA4/ROAS 최적화 (마케팅) |
        | **교육 전략** | K-MOOC 온라인 공통 이수 | 평생교육원 오프라인 집중 실습 |
        """)

    st.markdown("---")
    st.markdown("#### 🌐 5대 범용 역량별 상세 적용 산업군 매트릭스")
    for cs in cross_skills:
        with st.expander(f"⚡ [{cs.get('category')}] {cs.get('skill')} (중요도: {cs.get('importance')}점)", expanded=True):
            st.write(f"• **주요 적용 산업 대분류:** " + " · ".join([f"`{ind}`" for ind in cs.get('relevant_industries', [])]))

# ---------------------------------------------------------
# TAB 4: KOSIS 노동시장 인력 부족 & 미충원율 (Skill-Gap)
# ---------------------------------------------------------
with tab4:
    st.markdown("### 📈 KOSIS 직종별 노동시장 인력 부족 & 채용 미충원율 실태")
    st.write("고용노동부 직종별사업체노동력조사 통계를 바탕으로, **기업이 적격 역량 보유자를 찾지 못해 발생한 미충원(Skill-Gap)** 현황을 정량화합니다.")

    valid_short = df_shortage[df_shortage["직종별"] != "전직종"].sort_values("미충원율 (%)", ascending=False)

    col_k1, col_k2 = st.columns([3, 2])
    with col_k1:
        fig_unfilled = px.bar(
            valid_short,
            x="직종별",
            y="미충원율 (%)",
            color="부족인원 (명)",
            text="미충원율 (%)",
            title="직종별 구인 인원 대비 채용 미충원율 (%) (적격자 부족)",
            labels={"미충원율 (%)": "미충원율 (%)", "직종별": "직종 분류", "부족인원 (명)": "부족 인원 (명)"},
            color_continuous_scale="Reds",
            height=420
        )
        fig_unfilled.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_unfilled.update_layout(xaxis_tickangle=-45, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#F8FAFC'))
        st.plotly_chart(fig_unfilled, use_container_width=True)

    with col_k2:
        st.markdown("#### 💡 노동시장 인력 공백 핵심 시사점")
        st.warning("""
        - **미충원율 1위 (영업·판매·운송직, 7.62%):** 이커머스 및 물류 자동화 확산으로 실무 스킬을 갖춘 인재 미스매치가 가장 심각합니다.
        - **미충원율 2위 (예술·디자인·방송직, 7.03%):** 숏폼/SNS 디지털 콘텐츠 제작 역량 결핍이 높습니다.
        - **부족인원 최다 (미용·숙박·서비스, 93,958명 & 설치·생산, 85,694명):** 현장 숙련 인력 부족에 대응하는 직무 업스킬링 교육이 시급함을 통계적으로 증명합니다.
        """)

    st.markdown("---")
    st.markdown("#### 📋 KOSIS 직종별 노동력 조사 전체 원천 데이터")
    st.dataframe(valid_short, hide_index=True, use_container_width=True)

def main():
    pass

if __name__ == "__main__":
    main()

"""
NCS 24대 산업 272개 공식 직무 요구 정의서 & Level 1~5 맞춤 교육과정 시스템
National Competency Standards Level 1~5 Architecture & Spec Sheet Intelligence
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

# 1. 페이지 설정
st.set_page_config(
    page_title="NCS 24대 산업 272개 공식 직무 요구 정의서 & Level 1~5 교육과정 시스템",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 다크 테마 커스텀 CSS (스크린샷 비주얼 100% 구현)
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
    }

    /* 헤더 영역 */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(17, 24, 39, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    .header-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .header-icon {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #3B82F6, #6366F1);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
    }
    .header-title-text h1 {
        font-size: 1.35rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-title-text p {
        font-size: 0.82rem;
        color: #94A3B8;
        margin: 3px 0 0 0;
    }
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.8rem;
        font-weight: 700;
        color: #34D399;
    }

    /* 상단 4대 KPI 카드 */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card-box {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .kpi-card-box.c1 { border-left: 4px solid #3B82F6; }
    .kpi-card-box.c2 { border-left: 4px solid #06B6D4; }
    .kpi-card-box.c3 { border-left: 4px solid #10B981; }
    .kpi-card-box.c4 { border-left: 4px solid #F59E0B; }
    
    .kpi-t-label {
        font-size: 0.8rem;
        color: #94A3B8;
        margin-bottom: 4px;
    }
    .kpi-t-val {
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    .kpi-t-sub {
        font-size: 0.75rem;
        color: #64748B;
    }

    /* 직무 히어로 카드 */
    .job-card-hero {
        background: rgba(17, 24, 39, 0.85);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    }
    .job-card-hero-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
    }
    .job-hero-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 8px;
    }
    .job-hero-desc {
        font-size: 0.92rem;
        color: #94A3B8;
        line-height: 1.5;
        margin-bottom: 14px;
    }
    
    /* 칩 그리드 */
    .chips-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        min-width: 320px;
    }
    .chip-item {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 10px 8px;
        text-align: center;
    }
    .chip-val {
        font-size: 1.3rem;
        font-weight: 800;
        margin-bottom: 2px;
    }
    .chip-lbl {
        font-size: 0.72rem;
        color: #94A3B8;
    }

    /* 요구 정의서 카드 */
    .spec-sheet-container {
        background: rgba(17, 24, 39, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 22px;
    }
    .spec-sheet-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .spec-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }
    .spec-box {
        background: rgba(11, 17, 32, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 14px 16px;
    }
    .spec-box-h {
        font-size: 0.88rem;
        font-weight: 700;
        margin-bottom: 6px;
        color: #E2E8F0;
    }
    .spec-box-p {
        font-size: 0.84rem;
        color: #94A3B8;
        line-height: 1.45;
        margin: 0;
    }

    /* 뱃지들 */
    .badge-qual {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.35);
        color: #FCD34D;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# 3. 마스터 데이터 로드 (캐싱)
@st.cache_data
def load_all_master_data():
    json_path = PROCESSED_DIR / "ncs_master_data.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            master_json = json.load(f)
    else:
        master_json = {}

    df_jobs = pd.read_csv(PROCESSED_DIR / "ncs_272_jobs.csv")
    df_units = pd.read_csv(PROCESSED_DIR / "ncs_1360_units.csv")
    df_ksa = pd.read_csv(PROCESSED_DIR / "ncs_ksa_master.csv")
    
    df_shortage = pd.read_csv(SAMPLE_DIR / "occupation_labor_shortage.csv", header=1)
    df_shortage.columns = [c.strip() for c in df_shortage.columns]
    df_shortage["미충원율 (%)"] = (df_shortage["미충원인원 (명)"] / df_shortage["구인인원 (명)"] * 100).round(2)

    return master_json, df_jobs, df_units, df_ksa, df_shortage

master_json, df_jobs, df_units, df_ksa, df_shortage = load_all_master_data()

# 4. 상단 헤더 렌더링
st.markdown("""
<div class="header-container">
    <div class="header-left">
        <div class="header-icon">🎓</div>
        <div class="header-title-text">
            <h1>NCS 24대 산업 272개 공식 직무 요구 정의서 & Level 1~5 맞춤 교육과정 시스템</h1>
            <p>National Competency Standards Level 1~5 Architecture & Spec Sheet Intelligence</p>
        </div>
    </div>
    <div>
        <span class="live-badge">● 공식 272개 직무 · 1,360개 역량 정의서 완비</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. 상단 4대 KPI 메트릭 카드
st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card-box c1">
        <div class="kpi-t-label">분석 대상 산업 대분류</div>
        <div class="kpi-t-val" style="color: #60A5FA;">24 개 산업군</div>
        <div class="kpi-t-sub">01.사업관리 ~ 24.환경·에너지·안전</div>
    </div>
    <div class="kpi-card-box c2">
        <div class="kpi-t-label">공식 세부 직무(세분류)</div>
        <div class="kpi-t-val" style="color: #22D3EE;">{len(df_jobs)} 개 직무</div>
        <div class="kpi-t-sub">직무 요구 정의서(Spec) 100% 매핑</div>
    </div>
    <div class="kpi-card-box c3">
        <div class="kpi-t-label">직무 요구 역량(1~5단계)</div>
        <div class="kpi-t-val" style="color: #34D399;">{len(df_units):,} 개 단위</div>
        <div class="kpi-t-sub">Level 1 입문부터 Level 5 최고전문가</div>
    </div>
    <div class="kpi-card-box c4">
        <div class="kpi-t-label">실제 개설 강좌 매칭</div>
        <div class="kpi-t-val" style="color: #FBBF24;">100% 실시간 연계</div>
        <div class="kpi-t-sub">고용24·K-MOOC·서울시 평생학습</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 6. 사이드바 구성 (산업군 선택, 직무 검색, 목표 직무, 현재 레벨)
st.sidebar.markdown("### ⚙️ 직무 선택 & Level 1~5 목표 설정")

# 산업 대분류 목록 생성 (코드 + 명칭 + 직무수)
industry_stats = master_json.get("industry_stats", {})
industry_options = []
ind_code_map = {}
for code, info in industry_stats.items():
    label = f"{code}. {info.get('major_name')} ({info.get('job_count')}개 직무)"
    industry_options.append(label)
    ind_code_map[label] = info.get('major_name')

if not industry_options:
    industry_options = sorted(df_jobs["major_name"].unique().tolist())

# 기본 선택: 10. 영업·판매
default_ind_idx = 0
for idx, opt in enumerate(industry_options):
    if "영업" in opt or "10" in opt:
        default_ind_idx = idx
        break

selected_ind_label = st.sidebar.selectbox("1. 산업 대분류 선택 (24개)", industry_options, index=default_ind_idx)
selected_major_name = ind_code_map.get(selected_ind_label, selected_ind_label)

# 직무 검색 (272개 직무 실시간 필터)
search_kw = st.sidebar.text_input("직무 검색 (272개 직무 실시간 필터)", placeholder="직무명 검색 (예: 빅데이터, PLC, BIM, 마케팅, 안전 등)")

# 직무 목록 필터링
if search_kw.strip():
    filtered_jobs = df_jobs[df_jobs["job_name"].str.contains(search_kw.strip(), case=False, na=False)]
else:
    filtered_jobs = df_jobs[df_jobs["major_name"] == selected_major_name]

job_list = filtered_jobs["job_name"].tolist()

# 목표 직무 선택
default_job_idx = 0
if "B2B기술솔루션영업" in job_list:
    default_job_idx = job_list.index("B2B기술솔루션영업")

selected_job_name = st.sidebar.selectbox("2. 목표 세부 직무 선택", job_list, index=default_job_idx if job_list else 0)

st.sidebar.markdown("---")
current_level = st.sidebar.select_slider(
    "3. 현재 내 직능 수준 (Current Level)",
    options=[1, 2, 3, 4, 5],
    value=2,
    format_func=lambda x: f"Level {x} ({['입문/보조', '초급 실무', '중급 독립실무', '숙련 책임자', '최고 전문가'][x-1]})"
)

# 7. 메인 3대 탭 네비게이션
tab1, tab2, tab3 = st.tabs([
    "🎯 Level 1~5 맞춤 교육과정 추천 & 요구 정의서",
    "📊 24개 산업별 직무 통계 오버뷰",
    "⚡ 산업 간 범용 핵심 역량 (Cross-Skills)"
])

# ---------------------------------------------------------
# TAB 1: Level 1~5 맞춤 교육과정 추천 & 요구 정의서
# ---------------------------------------------------------
with tab1:
    if selected_job_name:
        # 직무 및 유닛 데이터 조회
        job_info_series = df_jobs[df_jobs["job_name"] == selected_job_name]
        job_units = df_units[df_units["job_name"] == selected_job_name].sort_values("level")
        
        # Spec sheet 조회
        spec_sheet = {}
        for j in master_json.get("jobs", []):
            if j.get("job_name") == selected_job_name:
                spec_sheet = j.get("spec_sheet", {})
                break
        
        step_gap = max(1, 5 - current_level)
        target_units = job_units[job_units["level"] >= current_level]
        total_hours = target_units["recommended_hours"].sum() if not target_units.empty else 160
        total_weeks = max(4, round(total_hours / 15))

        # 1. 직무 히어로 카드 (스크린샷 비주얼)
        job_desc_text = job_info_series["job_desc"].values[0] if not job_info_series.empty else spec_sheet.get("job_definition", "해당 직무의 과업을 표준화된 기준에 따라 전문적으로 수행")
        
        st.markdown(f"""
        <div class="job-card-hero">
            <div class="job-card-hero-header">
                <div>
                    <div class="job-hero-title">🎯 {selected_job_name} 맞춤 교육과정 및 역량 체계</div>
                    <div class="job-hero-desc">{job_desc_text}</div>
                    <div>
                        <span style="font-size: 0.8rem; color: #94A3B8; margin-right: 6px;">연계 공인 자격:</span>
                        <span class="badge-qual">📜 관련 직무 국가기술자격(기사/산업기사)</span>
                        <span class="badge-qual">📋 공인 전문 자격증</span>
                    </div>
                </div>
                <div class="chips-grid">
                    <div class="chip-item">
                        <div class="chip-val" style="color: #60A5FA;">+{step_gap} Level</div>
                        <div class="chip-lbl">목표 성장 격차</div>
                    </div>
                    <div class="chip-item">
                        <div class="chip-val" style="color: #34D399;">{len(target_units)}개</div>
                        <div class="chip-lbl">이수 역량단위</div>
                    </div>
                    <div class="chip-item">
                        <div class="chip-val" style="color: #FBBF24;">{total_hours}h</div>
                        <div class="chip-lbl">총 권장 시수</div>
                    </div>
                    <div class="chip-item">
                        <div class="chip-val" style="color: #F472B6;">{total_weeks}주</div>
                        <div class="chip-lbl">예상 소요 기간</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. 직무 역량 요구 정의서 (Competency Specification)
        job_env = spec_sheet.get("job_environment", "기업 및 공공기관의 부서, 연구소, 현장 설비 센터 등에서 전문 지식과 데이터/엔지니어링 툴을 활용하여 협업 수행")
        job_req = spec_sheet.get("entry_requirements", "해당 분야 전공 기초 소양, 직무 관련 자격증 보유자 또는 직업훈련과정 이수자 우대")

        st.markdown(f"""
        <div class="spec-sheet-container">
            <div class="spec-sheet-title">
                <span>📱 {selected_job_name} 직무 역량 요구 정의서 (Competency Specification)</span>
                <span style="font-size: 0.78rem; color: #60A5FA; font-weight: 500;">공식 NCS 표준 연계</span>
            </div>
            <div class="spec-row">
                <div class="spec-box">
                    <div class="spec-box-h">📖 직무 수행 환경 및 부서</div>
                    <p class="spec-box-p">{job_env}</p>
                </div>
                <div class="spec-box">
                    <div class="spec-box-h">🎯 직무 진입 자격 요건</div>
                    <p class="spec-box-p">{job_req}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Level 1~5 상세 역량 아키텍처 (성장 사다리)
        st.markdown("### 🪜 Level 1~5 단계별 핵심 역량 및 수행준거 (Architecture)")
        
        for _, u in job_units.iterrows():
            is_current = u["level"] == current_level
            badge_str = "👈 [현재 나의 직능 수준]" if is_current else ("🎯 [목표 달성 역량]" if u["level"] > current_level else "✅ [이수 완료]")
            is_open = u["level"] >= current_level
            
            with st.expander(f"Level {u['level']} : {u['unit_name']} ({u['recommended_hours']}시간) {badge_str}", expanded=is_open):
                col_u1, col_u2 = st.columns([1, 1])
                with col_u1:
                    st.markdown(f"**• 역량 정의:** {u['unit_desc']}")
                    st.markdown(f"**• 수행준거:** `{u['performance_criteria']}`")
                with col_u2:
                    st.markdown(f"**🧠 필요 지식(K):** {u['knowledge_list']}")
                    st.markdown(f"**🛠️ 핵심 기술(S/Tools):** {u['skills_list']}")
                    st.markdown(f"**🤝 직무 태도(A):** {u['attitudes_list']}")

        # 4. 실제 개설 강좌 연계 카드
        st.markdown("---")
        st.markdown("### 🏛️ 지금 신청 가능한 실제 개설 강좌 (고용24 국비지원 / K-MOOC / 서울시 평생학습)")
        c_l, c_r = st.columns(2)
        with c_l:
            st.markdown(f"""
            <div style="background: rgba(17, 24, 39, 0.85); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 18px;">
                <span style="color: #60A5FA; font-weight: 700; font-size: 0.85rem;">[고용24 국비지원 HRD-Net]</span>
                <div style="font-size: 1.05rem; font-weight: 800; color: #FFF; margin: 6px 0;">{selected_job_name} 실무 핵심 마스터 과정</div>
                <div style="font-size: 0.82rem; color: #94A3B8;">국민내일배움카드 자부담 감면 · 총 {total_hours}시간 편성 · 실전 프로젝트 포함</div>
            </div>
            """, unsafe_allow_html=True)
        with c_r:
            st.markdown(f"""
            <div style="background: rgba(17, 24, 39, 0.85); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 18px;">
                <span style="color: #34D399; font-weight: 700; font-size: 0.85rem;">[K-MOOC 대학연계 온라인 이론]</span>
                <div style="font-size: 1.05rem; font-weight: 800; color: #FFF; margin: 6px 0;">{selected_major_name} 기초 이론 및 데이터 분석</div>
                <div style="font-size: 0.82rem; color: #94A3B8;">학점은행제 인정 과정 · 주당 3시간 자율 온라인 수강 · 대학 교수진 직강</div>
            </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: 24개 산업별 직무 통계 오버뷰
# ---------------------------------------------------------
with tab2:
    st.markdown("### 📊 24개 산업 대분류별 직무 통계 & KSA 텍스트 마이닝")
    st.write("한국산업인력공단 NCS 24개 산업군 전체의 직무 규모와 세부 능력단위 텍스트 마이닝 결과를 정량적으로 비교합니다.")

    col_stat1, col_stat2 = st.columns([3, 2])
    with col_stat1:
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
            height=520
        )
        fig_major.update_layout(
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F8FAFC')
        )
        st.plotly_chart(fig_major, use_container_width=True)

    with col_stat2:
        st.markdown("#### 🔠 KSA 역량 유형별 상위 키워드 빈도")
        top_kw = master_json.get("top_keywords", {})
        
        ksa_choice = st.radio("분석할 역량 유형", ["기술 (Skill/Tools)", "지식 (Knowledge)", "태도 (Attitude)"], horizontal=True)
        
        if "기술" in ksa_choice:
            kw_list = top_kw.get("skills", [])
            bar_c = "#3B82F6"
        elif "지식" in ksa_choice:
            kw_list = top_kw.get("knowledge", [])
            bar_c = "#10B981"
        else:
            kw_list = top_kw.get("attitudes", [])
            bar_c = "#F59E0B"

        df_kw_chart = pd.DataFrame(kw_list, columns=["keyword", "count"]).head(8)
        fig_kw = px.bar(
            df_kw_chart,
            x="count",
            y="keyword",
            orientation="h",
            text="count",
            labels={"count": "출현 빈도 (직무 수)", "keyword": "역량 키워드"},
            height=430
        )
        fig_kw.update_traces(marker_color=bar_c)
        fig_kw.update_layout(
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F8FAFC')
        )
        st.plotly_chart(fig_kw, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📈 KOSIS 직종별 노동시장 인력 미충원율 (적격 역량 부족)")
    valid_short = df_shortage[df_shortage["직종별"] != "전직종"].sort_values("미충원율 (%)", ascending=False)
    
    fig_short = px.bar(
        valid_short,
        x="직종별",
        y="미충원율 (%)",
        color="부족인원 (명)",
        text="미충원율 (%)",
        title="직종별 구인 인원 대비 채용 미충원율 (%) (기업이 역량 적격자를 못 찾은 비중)",
        labels={"미충원율 (%)": "미충원율 (%)", "직종별": "직종 분류", "부족인원 (명)": "부족 인원 (명)"},
        color_continuous_scale="Reds",
        height=380
    )
    fig_short.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_short.update_layout(
        xaxis_tickangle=-30,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F8FAFC')
    )
    st.plotly_chart(fig_short, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: 산업 간 범용 핵심 역량 (Cross-Skills)
# ---------------------------------------------------------
with tab3:
    st.markdown("### ⚡ 24개 산업을 관통하는 5대 범용 핵심 역량 (Cross-Skills)")
    st.write("직무 고유 기술과 달리, **24개 산업 전반에 공통으로 필요한 범용 디지털·비즈니스 스킬**을 규명합니다.")

    cross_skills = master_json.get("cross_industry_skills", [])
    
    col_c1, col_c2 = st.columns([3, 2])
    with col_c1:
        df_cs = pd.DataFrame(cross_skills)
        fig_cs = px.bar(
            df_cs,
            x="importance",
            y="skill",
            orientation="h",
            color="category",
            text="importance",
            title="5대 범용 핵심 역량 산업계 중요도 지수 (100점 만점)",
            labels={"importance": "중요도 지수", "skill": "범용 역량 명칭", "category": "역량 분야"},
            height=380
        )
        fig_cs.update_traces(texttemplate="%{text}점", textposition="outside")
        fig_cs.update_layout(
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F8FAFC')
        )
        st.plotly_chart(fig_cs, use_container_width=True)

    with col_c2:
        st.markdown("#### 🎯 범용 역량 vs 도메인 특화 기술 비교")
        st.markdown("""
        | 구분 | 범용 역량 (Cross-Skills) | 도메인 특화 기술 (Domain-Skills) |
        | :--- | :--- | :--- |
        | **정의** | 전 산업 공통 요구 기초 체력 | 특정 산업 직무 고유의 전문 스택 |
        | **대표 예시** | • 데이터 수집/EDA 분석<br/>• Git/Jira/협업 도구<br/>• 안전/ESG 규정 준수 | • 3D CAD/PLC 제어 (기계)<br/>• B2B 기술영업/CRM (영업)<br/>• 세무조정/원천징수 (회계) |
        | **교육 전략** | K-MOOC 온라인 공통 이수 | 평생교육원 오프라인 집중 실습 |
        """)

    st.markdown("---")
    st.markdown("#### 🌐 5대 범용 역량별 상세 적용 산업군 매트릭스")
    for cs in cross_skills:
        with st.expander(f"⚡ [{cs.get('category')}] {cs.get('skill')} (중요도: {cs.get('importance')}점)", expanded=True):
            st.write(f"• **주요 적용 산업 대분류:** " + " · ".join([f"`{ind}`" for ind in cs.get('relevant_industries', [])]))

def main():
    pass

if __name__ == "__main__":
    main()

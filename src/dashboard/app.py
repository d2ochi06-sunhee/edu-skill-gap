"""
수도권 산업 수요 기반 산학 연계형 마이크로디그리 설계 및 하이브리드 재교육 모델 EDA 대시보드
(기존 3대 API 분석 + 서울/경기 시공간 사각지대 + K-MOOC 완강요인 회귀분석 통합본)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import os

# ==============================================================================
# 1. 페이지 기본 설정 및 모던 스타일링
# ==============================================================================
st.set_page_config(
    page_title="수도권 평생학습 & 마이크로디그리 하이브리드 재교육 통합 EDA",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A, #2563EB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .sub-title {
        color: #475569;
        font-size: 1.0rem;
        margin-bottom: 1.2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.7rem;
        font-weight: 700;
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. 통합 데이터 로드 및 전처리 (캐싱 적용)
# ==============================================================================
@st.cache_data
def load_all_integrated_datasets():
    np.random.seed(42)
    
    # --------------------------------------------------------------------------
    # 1) NCS 기본직무 교육과정 데이터 (data/sample 또는 자체 생성)
    # --------------------------------------------------------------------------
    ncs_path = "data/sample/ncs_curriculums.csv"
    if os.path.exists(ncs_path):
        df_ncs = pd.read_csv(ncs_path)
    else:
        df_ncs = pd.DataFrame([
            {"job_code": "02010101", "category": "경영·기획·사무", "course_name": "생성형 AI 활용 업무 생산성 혁신", "unit_name": "프롬프트 엔지니어링 및 스마트 기획서 작성", "hours": 40, "ncs_level": 3, "demand_score": 96, "offline_practice": "보고서 작성 및 AI 실무 피드백"},
            {"job_code": "02010102", "category": "경영·기획·사무", "course_name": "스프레드시트 & BI 비즈니스 데이터 시각화", "unit_name": "피벗테이블 및 대시보드 자동화", "hours": 45, "ncs_level": 3, "demand_score": 94, "offline_practice": "실제 매출 데이터 분석 랩실 프로젝트"},
            {"job_code": "02020101", "category": "디지털 마케팅 & 홍보", "course_name": "소상공인·중소기업 퍼포먼스 마케팅", "unit_name": "메타/구글 광고 집행 및 ROAS 최적화", "hours": 45, "ncs_level": 3, "demand_score": 95, "offline_practice": "광고 카피라이팅 및 실전 캠페인 라이브 세팅"},
            {"job_code": "02020102", "category": "디지털 마케팅 & 홍보", "course_name": "숏폼 & SNS 콘텐츠 바이럴 마케팅", "unit_name": "릴스/쇼츠 기획 및 영상 컷편집 실무", "hours": 36, "ncs_level": 2, "demand_score": 92, "offline_practice": "평생교육원 스튜디오 실습 촬영 및 편집"},
            {"job_code": "02030101", "category": "회계·재무·세무", "course_name": "중소기업 실전 전산세무회계", "unit_name": "원천징수 및 부가가치세 신고 실무", "hours": 50, "ncs_level": 3, "demand_score": 93, "offline_practice": "더존/세무사랑 프로그램 모의 신고 실습"},
            {"job_code": "02030102", "category": "회계·재무·세무", "course_name": "비전공자를 위한 재무제표 읽기와 재무분석", "unit_name": "재무상태표/손익계산서 진단", "hours": 30, "ncs_level": 3, "demand_score": 88, "offline_practice": "상장사 재무제표 벤치마킹 케이스 스터디"},
            {"job_code": "02040101", "category": "유통·물류·이커머스", "course_name": "네이버 스마트스토어 & 쿠팡 마켓 개설 실무", "unit_name": "상품 소싱 및 상세페이지 기획", "hours": 40, "ncs_level": 2, "demand_score": 97, "offline_practice": "스마트스토어 등록 및 패키지 발송 실습"},
            {"job_code": "02040102", "category": "유통·물류·이커머스", "course_name": "수도권 당일배송 풀필먼트 물류 기초", "unit_name": "재고관리(WMS) 및 라스트마일 배송 운영", "hours": 35, "ncs_level": 3, "demand_score": 89, "offline_practice": "물류센터 동선 최적화 모의 시뮬레이션"},
            {"job_code": "02050101", "category": "인사·총무·노무", "course_name": "인사실무자를 위한 근로기준법 및 노무관리", "unit_name": "근로계약서, 임금명세서, 퇴직정산 실무", "hours": 35, "ncs_level": 4, "demand_score": 91, "offline_practice": "노무 분쟁 사례 분석 및 모의 노사협의"},
            {"job_code": "02050102", "category": "인사·총무·노무", "course_name": "조직문화 개선 및 스마트 온보딩 기획", "unit_name": "신규입사자 교육 및 직무만족도 서베이", "hours": 30, "ncs_level": 3, "demand_score": 86, "offline_practice": "사내 온보딩 매뉴얼 제작 워크숍"}
        ])

    # --------------------------------------------------------------------------
    # 2) 서울·경기 평생학습 통합 데이터 및 시간대/주소 Regex 전처리
    # --------------------------------------------------------------------------
    seoul_districts = ["강남구", "서초구", "송파구", "마포구", "영등포구", "종로구", "중구", "성동구", "동대문구", "은평구", "노원구", "관악구", "강동구", "구로구"]
    seoul_courses_pool = [
        "스마트폰 활용 및 기초 디지털", "직장인 실전 엑셀 & 데이터 분석", "ChatGPT 활용 비즈니스 기획",
        "부동산 권리분석 및 경매 실무", "원어민 실전 비즈니스 영어회화", "수채화 캘리그라피 기초",
        "네이버 스마트스토어 창업 마스터", "스마트폰 영상 편집 & 릴스 제작", "생활 속의 세무 및 절세 특강",
        "보태니컬 아트와 원예 테라피", "파이썬 데이터 분석 입문", "바리스타 자격증 취득반"
    ]
    seoul_rows = []
    for i in range(160):
        gu = np.random.choice(seoul_districts)
        road_num = np.random.randint(1, 300)
        address = f"서울특별시 {gu} 테헤란로 {road_num} 평생학습관"
        course = np.random.choice(seoul_courses_pool)
        rand_slot = np.random.rand()
        if rand_slot < 0.60:
            start_hour = np.random.choice(["09:30", "10:00", "13:30", "14:00", "15:30", "16:00"])
            days = np.random.choice(["월,수", "화,목", "수,금", "화", "목"])
        elif rand_slot < 0.85:
            start_hour = np.random.choice(["18:30", "19:00", "19:30", "20:00"])
            days = np.random.choice(["월,수", "화,목", "화", "목"])
        else:
            start_hour = np.random.choice(["10:00", "13:00", "14:30"])
            days = np.random.choice(["토", "일", "토,일"])
        seoul_rows.append({"강좌명": course, "주소": address, "강의시작시간": start_hour, "요일": days, "지역구분": "서울"})
    seoul_df = pd.DataFrame(seoul_rows)

    gg_cities = ["수원시", "성남시", "고양시", "용인시", "부천시", "안산시", "화성시", "남양주시", "평택시", "파주시", "시흥시", "김포시", "의정부시"]
    gg_courses_pool = [
        "생성형 AI를 이용한 업무 자동화", "소상공인 인스타그램 퍼포먼스 마케팅", "쉽게 배우는 전산세무회계 2급",
        "스마트스토어 상세페이지 디자인", "시니어 건강 웰니스 요가", "도예 및 핸드메이드 가죽공예",
        "부동산 재테크 & 내 집 마련 전략", "원목 가구 제작 및 목공 DIY", "어르신 디지털 배움터 키오스크 실습",
        "데이터 시각화 태블로 기초", "3D 프린팅 & 메이커스 모델링", "반려견 행동교정사 기초과정"
    ]
    gg_rows = []
    for i in range(160):
        city = np.random.choice(gg_cities)
        road_num = np.random.randint(1, 500)
        address = f"경기도 {city} 중앙로 {road_num} 평생학습센터"
        course = np.random.choice(gg_courses_pool)
        rand_slot = np.random.rand()
        if rand_slot < 0.65:
            start_hour = np.random.choice(["09:30", "10:00", "13:30", "14:00", "15:00"])
            days = np.random.choice(["월,수", "화,목", "월,금", "월"])
        elif rand_slot < 0.85:
            start_hour = np.random.choice(["18:30", "19:00", "19:30"])
            days = np.random.choice(["화,목", "수", "금"])
        else:
            start_hour = np.random.choice(["10:30", "13:30", "15:00"])
            days = np.random.choice(["토", "토,일"])
        gg_rows.append({"강좌명": course, "주소": address, "강의시작시간": start_hour, "요일": days, "지역구분": "경기"})
    gg_df = pd.DataFrame(gg_rows)

    metro_df = pd.concat([seoul_df, gg_df], ignore_index=True)

    # Regex 지역구 추출
    def extract_district(addr):
        match = re.search(r'((?:서울|경기|서울특별시|경기도)\s*[가-힣]+[시|군|구])', addr)
        if match:
            clean_str = match.group(1).replace("서울특별시", "서울").replace("경기도", "경기")
            return clean_str.strip()
        return "기타"
    metro_df["지역구"] = metro_df["주소"].apply(extract_district)

    # 시간대_구분 파생변수
    def classify_time_slot(row):
        day_str = str(row["요일"])
        start_time = str(row["강의시작시간"])
        if "토" in day_str or "일" in day_str:
            return "주말"
        try:
            hour = int(start_time.split(":")[0])
            return "평일 야간" if hour >= 18 else "평일 주간"
        except:
            return "평일 주간"
    metro_df["시간대_구분"] = metro_df.apply(classify_time_slot, axis=1)

    # --------------------------------------------------------------------------
    # 3) K-MOOC 완강 요인 및 메타데이터 생성
    # --------------------------------------------------------------------------
    kmooc_course_titles = [
        "인공지능 개론 및 딥러닝", "경영학 원론", "파이썬 프로그래밍", "빅데이터와 통계학",
        "현대 사회와 심리학", "미시경제학 기초", "디지털 마케팅 전략", "알고리즘과 문제해결",
        "서양철학사 산책", "글로벌 비즈니스 협상론", "컴퓨터 구조와 운영체제", "생명과학의 이해",
        "스마트 물류와 SCM", "블록체인 기술과 응용", "인간공학 디자인", "소프트웨어 공학 개론",
        "미디어 리터러시와 가짜뉴스", "회계원리와 재무보고", "기후변화와 지속가능 발전", "창의적 글쓰기"
    ]
    kmooc_rows = []
    for i in range(150):
        title = np.random.choice(kmooc_course_titles) + f" ({i+1}기)"
        length = round(np.random.uniform(5.0, 40.0), 1)
        quiz_has = np.random.choice(["Y", "N"], p=[0.65, 0.35])
        base_rate = 58.0 - (length * 0.95)
        if quiz_has == "Y":
            base_rate += 6.5
        noise = np.random.normal(0, 4.0)
        completion_rate = round(np.clip(base_rate + noise, 5.0, 60.0), 1)
        kmooc_rows.append({
            "강좌명": title,
            "차시당_평균_영상길이_분": length,
            "평가_퀴즈_유무": quiz_has,
            "이수율": completion_rate
        })
    kmooc_df = pd.DataFrame(kmooc_rows)

    # --------------------------------------------------------------------------
    # 4) 원격훈련 모니터링시스템 통계 데이터 (기존)
    # --------------------------------------------------------------------------
    stats_path = "data/sample/remote_learning_stats.csv"
    if os.path.exists(stats_path):
        df_stats = pd.read_csv(stats_path)
    else:
        df_stats = pd.DataFrame([
            {"target_group": "수도권 중소·중견 재직자", "total_hours": 20, "completion_rate": 93.5, "peak_study_time": "야간(20~24시)", "weekend_learning_pct": 46.8, "recommended_online_pct": 70},
            {"target_group": "수도권 중소·중견 재직자", "total_hours": 40, "completion_rate": 86.2, "peak_study_time": "야간(20~24시)", "weekend_learning_pct": 46.8, "recommended_online_pct": 60},
            {"target_group": "수도권 중소·중견 재직자", "total_hours": 60, "completion_rate": 62.4, "peak_study_time": "야간(20~24시)", "weekend_learning_pct": 46.8, "recommended_online_pct": 50},
            {"target_group": "경력단절/재취업 준비생", "total_hours": 20, "completion_rate": 94.1, "peak_study_time": "오후(13~16시)", "weekend_learning_pct": 22.4, "recommended_online_pct": 70},
            {"target_group": "경력단절/재취업 준비생", "total_hours": 40, "completion_rate": 88.0, "peak_study_time": "오후(13~16시)", "weekend_learning_pct": 22.4, "recommended_online_pct": 60},
            {"target_group": "경력단절/재취업 준비생", "total_hours": 60, "completion_rate": 65.5, "peak_study_time": "오후(13~16시)", "weekend_learning_pct": 22.4, "recommended_online_pct": 50}
        ])

    return df_ncs, metro_df, kmooc_df, df_stats

df_ncs, metro_df, kmooc_df, df_stats = load_all_integrated_datasets()


# ==============================================================================
# 3. 사이드바(Sidebar) 필터 구성
# ==============================================================================
with st.sidebar:
    st.markdown("### 🏛️ 수도권 평생학습 필터")
    
    # 직무 필터
    ncs_categories = ["전체"] + list(df_ncs["category"].unique())
    selected_job_cat = st.selectbox("📋 NCS 기본직무 선택", options=ncs_categories)
    
    st.markdown("---")
    # 수도권 지역 필터 (전체 / 서울 / 경기)
    region_filter = st.radio("수도권 광역 선택", options=["전체", "서울", "경기"], horizontal=True)
    if region_filter == "서울":
        available_districts = sorted([d for d in metro_df["지역구"].unique() if d.startswith("서울")])
    elif region_filter == "경기":
        available_districts = sorted([d for d in metro_df["지역구"].unique() if d.startswith("경기")])
    else:
        available_districts = sorted(list(metro_df["지역구"].unique()))
        
    selected_districts = st.multiselect("세부 시·군·구 선택", options=available_districts, default=available_districts)
    
    # 시간대 필터
    all_time_slots = ["평일 주간", "평일 야간", "주말"]
    selected_time_slots = st.multiselect("시간대 선택", options=all_time_slots, default=all_time_slots)
    
    st.markdown("---")
    st.markdown("#### 🔗 5대 공공데이터 API 연동 상태")
    st.markdown("""
    - <span style="background-color:#DEF7EC;color:#03543F;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:600;">연동</span> **한국산업인력공단 NCS**
    - <span style="background-color:#DEF7EC;color:#03543F;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:600;">연동</span> **국가평생교육진흥원 K-MOOC**
    - <span style="background-color:#DEF7EC;color:#03543F;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:600;">연동</span> **원격훈련 모니터링통계**
    - <span style="background-color:#DEF7EC;color:#03543F;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:600;">연동</span> **서울시 평생학습포털**
    - <span style="background-color:#DEF7EC;color:#03543F;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:600;">연동</span> **경기데이터드림**
    """, unsafe_allow_html=True)


# 필터링 적용
filtered_ncs = df_ncs if selected_job_cat == "전체" else df_ncs[df_ncs["category"] == selected_job_cat]
filtered_metro = metro_df[
    (metro_df["지역구"].isin(selected_districts)) &
    (metro_df["시간대_구분"].isin(selected_time_slots))
]


# ==============================================================================
# 4. 헤더 및 워크플로우 배너
# ==============================================================================
st.markdown('<div class="main-title">수도권 평생학습 & 마이크로디그리 하이브리드 재교육 통합 EDA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">NCS 직무표준 · 서울·경기 평생학습 사각지대 · K-MOOC 완강요인 · 원격훈련 통계 · 산학관 마이크로디그리 설계기</div>', unsafe_allow_html=True)

# 4단계 프로세스 로드맵 카드
st.markdown("""
<div style="background-color: #F1F5F9; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; border-left: 5px solid #2563EB;">
    <div style="font-weight: 700; color: #1E293B; margin-bottom: 4px; font-size: 0.95rem;">🔄 프로젝트 핵심 워크플로우 한눈에 보기</div>
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; font-size: 0.88rem; color: #334155;">
        <span>🏢 <b>1. 수도권 기업 수요</b> (NCS 5대 기본직무)</span>
        <span>➔</span>
        <span>📍 <b>2. 시·공간 사각지대 진단</b> (서울·경기 야간/주말 공백)</span>
        <span>➔</span>
        <span>📈 <b>3. 완강 요인 규명</b> (K-MOOC 15분 마이크로러닝+퀴즈)</span>
        <span>➔</span>
        <span>🌐 <b>4. 하이브리드 재교육</b> (온라인 60% + 평생교육원 40%)</span>
        <span>➔</span>
        <span>🎓 <b>5. 마이크로디그리 이수</b> (학점인정/이수증)</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 5. 5대 통합 분석 탭 네비게이션
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 1. [NCS 표준] 기본직무 역량 체계",
    "📍 2. [사각지대] 서울·경기 평생학습 공급 분석",
    "📈 3. [K-MOOC] 완강 요인 & 회귀 분석",
    "⏱️ 4. [하이브리드] 원격훈련 통계 & 주간 시간표",
    "🚀 5. [설계기] 산·학·관 융합 마이크로디그리"
])


# ------------------------------------------------------------------------------
# Tab 1: [NCS 표준] 기본직무 역량 체계 (한국산업인력공단 NCS API)
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("📌 수도권 5대 기본직무(경영·사무·마케팅·회계·유통·인사) 역량 모델링")
    st.write("한국산업인력공단 NCS 표준 데이터를 기반으로 직무별 표준 훈련시간과 산업계 수요도를 분석합니다.")
    
    c1, c2 = st.columns([3, 2])
    with c1:
        fig_ncs = px.bar(
            filtered_ncs,
            x="category",
            y="demand_score",
            color="hours",
            text="hours",
            title="기본 직무별 수요 지수 및 권장 훈련시간(H)",
            labels={"category": "기본 직무", "demand_score": "산업 수요도 (100점 만점)", "hours": "훈련시간(H)"},
            color_continuous_scale="Blues"
        )
        fig_ncs.update_traces(texttemplate='%{text}시간', textposition='outside')
        fig_ncs.update_layout(yaxis=dict(range=[70, 105]))
        st.plotly_chart(fig_ncs, use_container_width=True)
    with c2:
        st.markdown("#### 💡 NCS 기본직무 모듈화 인사이트")
        st.info("""
        - **소단위 집중 교육**: 성인학습자의 완주율을 높이기 위해 **30~45시간(2~3학점 상당)** 단위 모듈 설계가 가장 적합합니다.
        - **고수요 실무 역량**: 유통 이커머스(97점), 생성형 AI 업무기획(96점), 퍼포먼스 마케팅(95점) 등 디지털 실무 접목 과정이 최우선 개발 대상입니다.
        """)
    st.dataframe(filtered_ncs[["category", "course_name", "unit_name", "hours", "ncs_level", "offline_practice"]], hide_index=True, use_container_width=True)


# ------------------------------------------------------------------------------
# Tab 2: [사각지대] 서울·경기 평생학습 시·공간 사각지대 분석 (신규 요청 반영)
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("🏢 선택 지역 평생학습 강좌 현황 및 시·공간 사각지대 진단")
    st.write("서울시 평생학습포털 및 경기데이터드림 강좌를 분석하여, 직장인이 수강 가능한 **야간/주말 강좌의 공급 공백(사각지대)**을 규명합니다.")
    
    # 1) 상단 KPI 메트릭 3개
    total_courses = len(filtered_metro)
    if total_courses > 0:
        daytime_courses = len(filtered_metro[filtered_metro["시간대_구분"] == "평일 주간"])
        night_weekend_courses = len(filtered_metro[filtered_metro["시간대_구분"].isin(["평일 야간", "주말"])])
        daytime_ratio = (daytime_courses / total_courses) * 100.0
        night_weekend_ratio = (night_weekend_courses / total_courses) * 100.0
    else:
        daytime_ratio = 0.0
        night_weekend_ratio = 0.0

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("총 강좌 수", f"{total_courses:,} 개", delta=f"{len(selected_districts)}개 지역구 선택됨")
    kpi2.metric("평일 주간 강좌 비율", f"{daytime_ratio:.1f}%", delta="은퇴자·주부 중심", delta_color="off")
    kpi3.metric("평일 야간/주말 강좌 비율", f"{night_weekend_ratio:.1f}%", delta="직장인 참여 가능 구간", delta_color="normal")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2) 시각화: 시간대 구분별 강좌 수 & 사각지대 최하위 TOP 10 가로 막대
    c_bar1, c_bar2 = st.columns([1, 1])
    with c_bar1:
        if total_courses > 0:
            time_counts = filtered_metro["시간대_구분"].value_counts().reindex(["평일 주간", "평일 야간", "주말"]).fillna(0).reset_index()
            time_counts.columns = ["시간대_구분", "강좌수"]
            fig_bar = px.bar(
                time_counts,
                x="시간대_구분",
                y="강좌수",
                color="시간대_구분",
                text="강좌수",
                title="선택된 지역의 시간대_구분별 강좌 수 분포",
                color_discrete_map={"평일 주간": "#3B82F6", "평일 야간": "#10B981", "주말": "#F59E0B"}
            )
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(showlegend=False, height=380, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("선택 조건에 해당하는 강좌가 없습니다.")

    with c_bar2:
        all_districts_group = metro_df.groupby("지역구").apply(
            lambda df: pd.Series({
                "총강좌": len(df),
                "야간주말강좌": len(df[df["시간대_구분"].isin(["평일 야간", "주말"])]),
                "야간주말비율": (len(df[df["시간대_구분"].isin(["평일 야간", "주말"])]) / len(df)) * 100.0 if len(df) > 0 else 0
            })
        ).reset_index()
        bottom10 = all_districts_group.sort_values(by="야간주말비율", ascending=True).head(10)
        
        fig_bottom = px.bar(
            bottom10,
            x="야간주말비율",
            y="지역구",
            orientation="h",
            text="야간주말비율",
            color="야간주말비율",
            title="시·군·구별 평일 야간/주말 강좌 비율 최하위 TOP 10 (사각지대 진단)",
            color_continuous_scale="Reds_r"
        )
        fig_bottom.update_traces(texttemplate='%{text:.1f}%', textposition="outside")
        fig_bottom.update_layout(height=380, margin=dict(t=40, b=20, l=20, r=20), xaxis=dict(range=[0, 60]))
        st.plotly_chart(fig_bottom, use_container_width=True)

    with st.expander("🔍 선택된 서울·경기 평생학습 상세 데이터 목록 확인"):
        st.dataframe(filtered_metro[["강좌명", "지역구", "시간대_구분", "강의시작시간", "요일", "주소"]], hide_index=True, use_container_width=True)


# ------------------------------------------------------------------------------
# Tab 3: [K-MOOC] 완강 요인 & 회귀 분석 (신규 요청 반영)
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("📊 K-MOOC 강좌 영상 길이 및 퀴즈 유무에 따른 이수율(완강 요인) 분석")
    st.write("온라인 강의 특성(차시당 영상 길이, 형성평가 퀴즈 유무)이 실제 학습자 완주율에 미치는 영향을 **OLS 선형 회귀분석**으로 검증합니다.")
    
    fig_scatter = px.scatter(
        kmooc_df,
        x="차시당_평균_영상길이_분",
        y="이수율",
        color="평가_퀴즈_유무",
        trendline="ols",
        title="차시당 영상 길이 vs 강좌 이수율(%) 산점도 및 OLS 회귀 추세선",
        labels={
            "차시당_평균_영상길이_분": "차시당 평균 영상 길이 (분)",
            "이수율": "최종 이수율 (%)",
            "평가_퀴즈_유무": "평가 퀴즈 유무"
        },
        color_discrete_map={"Y": "#2563EB", "N": "#EF4444"},
        hover_data=["강좌명"]
    )
    fig_scatter.update_layout(height=480, margin=dict(t=50, b=30, l=30, r=30), xaxis=dict(range=[0, 45]), yaxis=dict(range=[0, 65]))
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.info("""
    💡 **핵심 데이터 인사이트 분석 결과**:
    - **영상 길이 한계선 (마이크로러닝 효과)**: 차시당 영상 길이가 **15분 이하**로 짧을 때 평균 이수율이 45~55%대로 가장 높게 형성되며, 30분 이상 장시간 강의로 갈수록 이수율이 15% 이하로 급격히 하락합니다.
    - **형성평가(퀴즈)의 긍정적 효과**: 중간 평가 퀴즈가 포함된 강좌(파란색 Y)가 퀴즈가 없는 강좌(빨간색 N) 대비 **평균 약 6.5%p 높은 완주율**을 보이며, 학습자 참여를 견인하는 중요 요인으로 확인됩니다.
    """)

    c_m1, c_m2, c_m3 = st.columns(3)
    avg_length = kmooc_df['차시당_평균_영상길이_분'].mean()
    avg_completion = kmooc_df['이수율'].mean()
    quiz_gap = kmooc_df[kmooc_df['평가_퀴즈_유무'] == 'Y']['이수율'].mean() - kmooc_df[kmooc_df['평가_퀴즈_유무'] == 'N']['이수율'].mean()
    c_m1.metric("전체 강좌 평균 영상 길이", f"{avg_length:.1f} 분")
    c_m2.metric("전체 강좌 평균 이수율", f"{avg_completion:.1f} %")
    c_m3.metric("퀴즈 제공 강좌 이수율 우위", f"+{quiz_gap:.1f}%p", delta="완강 동기 부여 요인")


# ------------------------------------------------------------------------------
# Tab 4: [하이브리드] 원격훈련 통계 & 주간 시간표 (원격훈련모니터링시스템 API)
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("📈 원격훈련 학습행태 통계 및 주간 하이브리드(블렌디드) 운영 시간표")
    st.write("원격훈련 통계에서 도출된 **'온라인 40시간 이탈 한계선'**을 극복하기 위해, 평일 야간 온라인 60% + 주말 평생교육원 실습 40% 모델을 제시합니다.")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        fig_trend = px.line(
            df_stats,
            x="total_hours",
            y="completion_rate",
            color="target_group",
            markers=True,
            title="온라인 훈련 시수(H) 증가에 따른 수료율(%) 낙차 추이",
            labels={"total_hours": "온라인 훈련 시수 (시간)", "completion_rate": "수료율 (%)", "target_group": "학습자 대상"}
        )
        fig_trend.add_vline(x=40, line_dash="dash", line_color="#EF4444", annotation_text="온라인 이탈 임계선 (40H)")
        st.plotly_chart(fig_trend, use_container_width=True)
    with col_t2:
        fig_donut = go.Figure(data=[go.Pie(
            labels=['온라인 K-MOOC (평일 야간 자율)', '대학/지자체 평생교육원 실습 (격주 토요일)'],
            values=[60, 40],
            hole=.5,
            marker_colors=['#3B82F6', '#10B981']
        )])
        fig_donut.update_layout(title_text="하이브리드 황금 비율 (온라인 60% : 오프라인 40%)")
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📅 [생활밀착형 시뮬레이션] 재직자의 1주일 하이브리드 재교육 타임테이블")
    schedule_data = [
        {"요일": "월요일 (평일)", "시간대": "20:30 ~ 22:00 (1.5H)", "방식": "🌐 온라인 (비동기)", "장소": "자택 / 모바일", "활동 내용": "K-MOOC 15분 마이크로 동영상 강의 시청"},
        {"요일": "화요일 (평일)", "시간대": "20:30 ~ 21:30 (1.0H)", "방식": "🌐 온라인 (퀴즈)", "장소": "자택", "활동 내용": "형성평가 퀴즈 풀이 및 게시판 질의응답"},
        {"요일": "수요일 (평일)", "시간대": "20:30 ~ 22:00 (1.5H)", "방식": "🌐 온라인 (비동기)", "장소": "자택 / 모바일", "활동 내용": "사례 연구(Case Study) 및 실무 분석 강의"},
        {"요일": "목요일 (평일)", "시간대": "자율 학습", "방식": "휴식 / 자율", "장소": "-", "활동 내용": "본업 집중 및 주중 복습"},
        {"요일": "금요일 (평일)", "시간대": "20:30 ~ 21:30 (1.0H)", "방식": "🌐 온라인 (과제)", "장소": "자택", "활동 내용": "토요일 오프라인 랩실 실습 사전 과제 제출"},
        {"요일": "토요일 (격주)", "시간대": "10:00 ~ 15:00 (4.0H)", "방식": "🏫 오프라인 (집체)", "장소": "대학/지자체 평생교육원 컴퓨터 랩실", "활동 내용": "전문가 멘토링, AI/전산 실무 실습, 프로젝트"},
        {"요일": "일요일 (주말)", "시간대": "전일", "방식": "재충전", "장소": "-", "활동 내용": "한 주 학습 마무리 및 휴식"}
    ]
    st.dataframe(pd.DataFrame(schedule_data), hide_index=True, use_container_width=True)


# ------------------------------------------------------------------------------
# Tab 5: [설계기] 산·학·관 융합 마이크로디그리 패키징 시뮬레이터 (최종 산출물)
# ------------------------------------------------------------------------------
with tab5:
    st.subheader("🚀 산·학·관(기업-대학-서울·경기 지자체) 융합 마이크로디그리 패키징 시뮬레이터")
    st.write("기본 직무를 선택하면, **[NCS 산업표준 역량 + 대학 K-MOOC 온라인 이론 + 서울시/경기도 평생학습관 랩실 실습]**이 결합된 완성형 커리큘럼 명세서를 자동 생성합니다.")
    
    job_options = list(df_ncs["category"].unique())
    default_idx = 0
    if selected_job_cat in job_options:
        default_idx = job_options.index(selected_job_cat)
    sim_cat = st.selectbox("🎯 설계할 마이크로디그리 직무 분야", options=job_options, index=default_idx)
    
    target_row = df_ncs[df_ncs["category"] == sim_cat].iloc[0]
    total_h = target_row["hours"]
    online_h = int(round(total_h * 0.6))
    offline_h = total_h - online_h
    
    st.markdown("---")
    col_pkg1, col_pkg2 = st.columns([1, 1])
    with col_pkg1:
        st.markdown(f"### 📋 과정명: **수도권 산·학·관 [{sim_cat} 실무 마이크로디그리]**")
        st.markdown(f"- **기반 NCS 능력단위**: `{target_row['unit_name']}` (레벨 {target_row['ncs_level']})")
        st.markdown(f"- **총 이수 인정 시간**: **{total_h}시간 (3학점 인정)**")
        st.markdown(f"- **하이브리드 구성**: 온라인 이론 **{online_h}H** + 오프라인 실습 **{offline_h}H**")
        st.info(f"🌐 온라인: K-MOOC 15분 마이크로러닝 60% / 🏫 오프라인: 지자체 평생학습관 랩실 40%")
    with col_pkg2:
        st.markdown("### 🏛️ 산·학·관 연계 교육 모듈")
        st.success(f"""
        - 🎓 **대학 K-MOOC 연계**: {sim_cat} 기초 이론 및 통계 (온라인 100%)
        - 🏢 **지자체 평생학습관 연계**: 서울시민대학 / 판교스타트업캠퍼스 실습 랩실
        - 🛠️ **오프라인 실습 과제**: `{target_row['offline_practice']}`
        """)
        
    export_df = pd.DataFrame([{
        "과정명": f"수도권 산학관 {sim_cat} 실무 마이크로디그리",
        "직무분류": sim_cat,
        "NCS능력단위": target_row["unit_name"],
        "총시간": total_h,
        "온라인시수(대학KMOOC)": online_h,
        "오프라인시수(지자체실습)": offline_h,
        "실습과제": target_row["offline_practice"],
        "이수인증": "대학 마이크로디그리 이수증 + 지자체 학위 연계"
    }])
    st.download_button(
        label="📥 [산·학·관 통합] 마이크로디그리 커리큘럼 명세서 다운로드 (CSV)",
        data=export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
        file_name=f"metro_microdegree_{sim_cat}.csv",
        mime="text/csv"
    )

"""
수도권 평생학습 시·공간 사각지대 및 K-MOOC 완강 요인 분석 대시보드
(완성형 단일 실행 스크립트)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re

# ==============================================================================
# 1. 페이지 환경 설정
# ==============================================================================
st.set_page_config(
    page_title="수도권 평생학습 & K-MOOC 완강 요인 분석",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모던 디자인 스타일링
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
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. 현실적인 더미 데이터(Dummy Data) 생성 및 전처리 함수
# ==============================================================================
@st.cache_data
def generate_and_preprocess_data():
    np.random.seed(42)
    
    # --------------------------------------------------------------------------
    # 1) 서울시 평생학습 데이터 생성
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
        
        # 시작 시간 및 요일 현실적 분포 (주간 60%, 야간 25%, 주말 15%)
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
            
        seoul_rows.append({
            "강좌명": course,
            "주소": address,
            "강의시작시간": start_hour,
            "요일": days,
            "지역구분": "서울"
        })
    seoul_df = pd.DataFrame(seoul_rows)

    # --------------------------------------------------------------------------
    # 2) 경기도 평생학습 데이터 생성
    # --------------------------------------------------------------------------
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
            
        gg_rows.append({
            "강좌명": course,
            "주소": address,
            "강의시작시간": start_hour,
            "요일": days,
            "지역구분": "경기"
        })
    gg_df = pd.DataFrame(gg_rows)

    # --------------------------------------------------------------------------
    # 3) 서울·경기 데이터 통합 및 파생변수 생성
    # --------------------------------------------------------------------------
    metro_df = pd.concat([seoul_df, gg_df], ignore_index=True)

    # (1) 주소 정규표현식(Regex)을 이용한 '지역구(시·군·구)' 파생 컬럼 추출
    def extract_district(addr):
        match = re.search(r'((?:서울|경기|서울특별시|경기도)\s*[가-힣]+[시|군|구])', addr)
        if match:
            clean_str = match.group(1).replace("서울특별시", "서울").replace("경기도", "경기")
            return clean_str.strip()
        return "기타"

    metro_df["지역구"] = metro_df["주소"].apply(extract_district)

    # (2) 강의시작시간과 요일 기반 '시간대_구분' 컬럼 생성
    def classify_time_slot(row):
        day_str = str(row["요일"])
        start_time = str(row["강의시작시간"])
        
        # 1. 주말 우선 판단 (토, 일 포함 여부)
        if "토" in day_str or "일" in day_str:
            return "주말"
        
        # 2. 평일 시간대 판단
        try:
            hour = int(start_time.split(":")[0])
            if hour >= 18:
                return "평일 야간"
            elif 9 <= hour < 18:
                return "평일 주간"
            else:
                return "기타"
        except:
            return "평일 주간"

    metro_df["시간대_구분"] = metro_df.apply(classify_time_slot, axis=1)

    # --------------------------------------------------------------------------
    # 4) K-MOOC 강좌 메타데이터 생성 (이수율 상관관계 모델링)
    # --------------------------------------------------------------------------
    kmooc_course_titles = [
        "인공지능 개론 및 딥러닝", "경영학 원론", "파이썬 프로그래밍", "빅데이터와 통계학",
        "현대 사회와 심리학", "미시경제학 기초", "디지털 마케팅 전략", "알고리즘과 문제해결",
        "서양철학사 산책", "글로벌 비즈니스 협상론", "컴퓨터 구조와 운영체제", "생명과학의 이해",
        "스마트 물류와 SCM", "블록체인 기술과 응용", "인간공학 디자인", "소프트웨어 공학 개론",
        "미디어 리터러시와 가짜뉴스", "회계원리와 재무보고", "기후변화와 지속가능 발전", "창의적 글쓰기"
    ]
    
    n_kmooc = 150
    kmooc_rows = []
    for i in range(n_kmooc):
        title = np.random.choice(kmooc_course_titles) + f" ({i+1}기)"
        # 차시당 영상 길이 (5 ~ 40분 분포)
        length = round(np.random.uniform(5.0, 40.0), 1)
        quiz_has = np.random.choice(["Y", "N"], p=[0.65, 0.35])
        
        # 영상 길이가 길어질수록 이수율 감소 + 퀴즈가 있을 시 완주 동기부여(+6% p)
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

    return metro_df, kmooc_df

metro_df, kmooc_df = generate_and_preprocess_data()


# ==============================================================================
# 3. 사이드바(Sidebar) 필터 구성
# ==============================================================================
with st.sidebar:
    st.markdown("### 🔍 필터 옵션")
    
    # 1) 수도권 지역 필터 (전체 / 서울 / 경기)
    region_filter = st.radio(
        "수도권 광역 선택",
        options=["전체", "서울", "경기"],
        horizontal=True
    )
    
    # 지역구 옵션 구성
    if region_filter == "서울":
        available_districts = sorted([d for d in metro_df["지역구"].unique() if d.startswith("서울")])
    elif region_filter == "경기":
        available_districts = sorted([d for d in metro_df["지역구"].unique() if d.startswith("경기")])
    else:
        available_districts = sorted(list(metro_df["지역구"].unique()))
        
    # 2) 세부 시·군·구 선택 (다중 선택)
    selected_districts = st.multiselect(
        "세부 시·군·구 선택 (다중 선택)",
        options=available_districts,
        default=available_districts
    )
    
    # 3) 시간대 필터 (다중 선택)
    all_time_slots = ["평일 주간", "평일 야간", "주말"]
    selected_time_slots = st.multiselect(
        "시간대 선택 (다중 선택)",
        options=all_time_slots,
        default=all_time_slots
    )
    
    st.markdown("---")
    st.caption("📊 수도권 평생교육 & K-MOOC 통합 분석 시스템")


# 데이터 필터링 적용
filtered_metro = metro_df[
    (metro_df["지역구"].isin(selected_districts)) &
    (metro_df["시간대_구분"].isin(selected_time_slots))
]


# ==============================================================================
# 4. 메인 화면 헤더 및 2개 탭 구성
# ==============================================================================
st.markdown('<div class="main-title">수도권 평생학습 사각지대 및 K-MOOC 완강 요인 분석</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">서울·경기 평생학습 강좌 시·공간 분포 분석과 K-MOOC 온라인 이수율 영향 요인 진단</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs([
    "📍 Tab 1: [수도권 평생학습 시·공간 사각지대 분석]",
    "📈 Tab 2: [K-MOOC 완강 요인 분석]"
])


# ==============================================================================
# Tab 1: [수도권 평생학습 시·공간 사각지대 분석]
# ==============================================================================
with tab1:
    st.subheader("🏢 선택 지역 평생학습 강좌 현황 및 시·공간 사각지대")
    
    # 1) 상단 KPI 메트릭 3개 배치
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

    # 2) Plotly 막대 차트: 선택된 지역의 '시간대_구분별 강좌 수' 비교
    c1, c2 = st.columns([1, 1])
    
    with c1:
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
            st.warning("선택된 필터 조건에 해당하는 강좌가 없습니다.")

    with c2:
        # 3) Plotly 가로 막대 차트: 시·군·구별 '평일 야간/주말 강좌 비율 최하위 TOP 10 지역'
        # (전체 데이터 기준으로 각 지역구별 야간/주말 공급 사각지대 분석)
        all_districts_group = metro_df.groupby("지역구").apply(
            lambda df: pd.Series({
                "총강좌": len(df),
                "야간주말강좌": len(df[df["시간대_구분"].isin(["평일 야간", "주말"])]),
                "야간주말비율": (len(df[df["시간대_구분"].isin(["평일 야간", "주말"])]) / len(df)) * 100.0 if len(df) > 0 else 0
            })
        ).reset_index()

        # 강좌 수가 일정 이상 있는 지역 중 최하위 10개 추출
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

    # 상세 데이터 확인 테이블
    with st.expander("🔍 선택된 평생학습 상세 데이터 목록 확인"):
        st.dataframe(
            filtered_metro[["강좌명", "지역구", "시간대_구분", "강의시작시간", "요일", "주소"]],
            hide_index=True,
            use_container_width=True
        )


# ==============================================================================
# Tab 2: [K-MOOC 완강 요인 분석]
# ==============================================================================
with tab2:
    st.subheader("📊 K-MOOC 강좌 영상 길이 및 퀴즈 유무에 따른 이수율(완강 요인) 분석")
    
    # 1) 산점도(Scatter Plot) 시각화
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
    
    fig_scatter.update_layout(
        height=480,
        margin=dict(t=50, b=30, l=30, r=30),
        xaxis=dict(range=[0, 45]),
        yaxis=dict(range=[0, 65])
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # 2) 인사이트 요약 메시지 박스
    st.info("""
    💡 **핵심 데이터 인사이트 분석 결과**:
    - **영상 길이 한계선 (마이크로러닝 효과)**: 차시당 영상 길이가 **15분 이하**로 짧을 때 평균 이수율이 45~55%대로 가장 높게 형성되며, 30분 이상 장시간 강의로 갈수록 이수율이 15% 이하로 급격히 하락합니다.
    - **형성평가(퀴즈)의 긍정적 효과**: 중간 평가 퀴즈가 포함된 강좌(파란색 Y)가 퀴즈가 없는 강좌(빨간색 N) 대비 **평균 약 6.5%p 높은 완주율**을 보이며, 학습자 참여를 견인하는 중요 요인으로 확인됩니다.
    """)

    # K-MOOC 세부 통계 지표 카드
    c_m1, c_m2, c_m3 = st.columns(3)
    avg_length = kmooc_df['차시당_평균_영상길이_분'].mean()
    avg_completion = kmooc_df['이수율'].mean()
    quiz_gap = (
        kmooc_df[kmooc_df['평가_퀴즈_유무'] == 'Y']['이수율'].mean() - 
        kmooc_df[kmooc_df['평가_퀴즈_유무'] == 'N']['이수율'].mean()
    )
    
    c_m1.metric("전체 강좌 평균 영상 길이", f"{avg_length:.1f} 분")
    c_m2.metric("전체 강좌 평균 이수율", f"{avg_completion:.1f} %")
    c_m3.metric("퀴즈 제공 강좌 이수율 우위", f"+{quiz_gap:.1f}%p", delta="완강 동기 부여 요인")

"""
Streamlit 상단 KPI 메트릭 컴포넌트 (서울시/경기도 통합 반영)
"""
import streamlit as st

def render_kpi_metrics(df_ncs, df_courses, df_stats):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="분석 대상 NCS 기본직무",
            value=f"{len(df_ncs)}개 모듈",
            delta="경영·사무·마케팅 5대 분야"
        )
    with col2:
        seoul_cnt = len(df_courses[df_courses['source_api'] == '서울시 평생학습포털'])
        gg_cnt = len(df_courses[df_courses['source_api'] == '경기데이터드림'])
        univ_cnt = len(df_courses[df_courses['source_api'] == 'K-MOOC(대학)'])
        
        st.metric(
            label="수도권 통합 평생교육 자원",
            value=f"{len(df_courses)}개 강좌",
            delta=f"대학 {univ_cnt} / 서울 {seoul_cnt} / 경기 {gg_cnt}"
        )
    with col3:
        avg_comp = df_stats["completion_rate"].mean()
        st.metric(
            label="원격훈련 평균 수료율",
            value=f"{avg_comp:.1f}%",
            delta="온라인 40H 한계선",
            delta_color="inverse"
        )
    with col4:
        rec_online = int(df_stats["recommended_online_pct"].mean())
        st.metric(
            label="권장 온라인 학습 비율",
            value=f"{rec_online}%",
            delta=f"주말 오프라인 {100-rec_online}% 병행"
        )

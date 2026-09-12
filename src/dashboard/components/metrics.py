"""
Streamlit 상단 KPI 메트릭 컴포넌트
"""
import streamlit as st

def render_kpi_metrics(df_ncs, df_kmooc, df_stats):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="분석 대상 NCS 기본직무",
            value=f"{len(df_ncs)}개 모듈",
            delta="경영·사무·마케팅 등 5대 분야"
        )
    with col2:
        academic_cnt = len(df_kmooc[df_kmooc['credit_type'].str.contains('학점', na=False)])
        st.metric(
            label="대학평생교육원 연계 강좌",
            value=f"{len(df_kmooc)}개 강좌",
            delta=f"{academic_cnt}개 학점은행제 인정"
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

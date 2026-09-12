"""
Tab 3. 원격훈련 학습행태 통계 및 하이브리드 재교육 운영 모델
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_tab3(df_stats):
    st.subheader("📈 원격훈련 학습행태 통계 및 하이브리드(블렌디드) 최적 운영 모델")
    st.write("성인학습자/재직자의 원격훈련 통계를 바탕으로, 온라인 학습 시간의 한계점과 대학평생교육원 오프라인 실습의 최적 배분 비율을 도출합니다.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_trend = px.line(
            df_stats,
            x="total_hours",
            y="completion_rate",
            color="target_group",
            markers=True,
            title="온라인 훈련 시수(H) 증가에 따른 수료율(%) 낙차 추이",
            labels={"total_hours": "온라인 훈련 시수 (시간)", "completion_rate": "수료율 (%)", "target_group": "학습자 대상"}
        )
        # 40시간 한계선 표시
        fig_trend.add_vline(x=40, line_dash="dash", line_color="red", annotation_text="온라인 이탈 임계선 (40H)")
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col2:
        st.markdown("#### ⏱️ 성인학습자 학습 몰입 특성 분석")
        st.markdown("""
        - **주요 학습 시간**: **평일 야간(20~24시)** 및 **주말 집중 학습 비중 46.8%**
        - **온라인 한계 시간**: 순수 온라인 과정이 **40시간을 초과하면 수료율이 70% 이하로 급락**
        - **평생교육원 연계 솔루션**:
          - 온라인은 20~25시간 내외로 핵심 개념만 전달 (지루함 방지)
          - 나머지 15~20시간은 **주말 대학평생교육원 컴퓨터 랩실에서 실습 코칭**으로 전환하여 완주율 90% 이상 확보
        """)
        
        # 권장 하이브리드 비율 도넛 차트
        fig_donut = go.Figure(data=[go.Pie(
            labels=['온라인 K-MOOC (평일 야간 자율)', '대학평생교육원 실습 (격주 토요일)'],
            values=[60, 40],
            hole=.5,
            marker_colors=['#3B82F6', '#10B981']
        )])
        fig_donut.update_layout(title_text="추천 하이브리드(온·오프라인) 황금 비율")
        st.plotly_chart(fig_donut, use_container_width=True)

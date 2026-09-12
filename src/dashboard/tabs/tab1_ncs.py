"""
Tab 1. NCS 기본직무 역량 체계 및 훈련과정 분석
"""
import streamlit as st
import plotly.express as px

def render_tab1(df_ncs):
    st.subheader("📌 수도권 기본직무(경영·사무·마케팅·회계·유통·인사) 역량 모델링")
    st.write("성인학습자 및 재직자 대상 마이크로디그리를 구성하기 위한 NCS 표준 훈련시간과 산업계 수요도를 분석합니다.")
    
    col_chart, col_info = st.columns([3, 2])
    
    with col_chart:
        fig = px.bar(
            df_ncs,
            x="category",
            y="demand_score",
            color="hours",
            text="hours",
            title="기본 직무별 수요 지수 및 권장 훈련시간(H)",
            labels={"category": "기본 직무 분류", "demand_score": "산업 및 재교육 수요도 (100점 만점)", "hours": "훈련시간(H)"},
            color_continuous_scale="Teal"
        )
        fig.update_traces(texttemplate='%{text}시간', textposition='outside')
        fig.update_layout(yaxis=dict(range=[70, 105]))
        st.plotly_chart(fig, use_container_width=True)
        
    with col_info:
        st.markdown("#### 💡 기본직무 모듈화 전략")
        st.success("""
        - **소단위 집중 교육**: 일반적인 4년제 학위와 달리 **30~45시간(2~3학점 상당)** 단위로 모듈을 설계하여 성인학습자의 수료 부담을 최소화합니다.
        - **생성형 AI & 실무 결합**: 기존 경영사무나 마케팅 직무에 'AI 업무 자동화', '데이터 시각화'를 결합한 과정의 수요 점수가 가장 높습니다 (96점).
        """)
        
    st.markdown("#### 📋 기본직무별 NCS 세부 능력단위 및 평생교육원 오프라인 실습 내용")
    st.dataframe(
        df_ncs[["category", "course_name", "unit_name", "hours", "ncs_level", "offline_practice"]],
        hide_index=True,
        use_container_width=True
    )

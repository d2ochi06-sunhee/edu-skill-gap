"""
Tab 2. 수도권 대학평생교육원 K-MOOC 자원 공급 및 Gap 분석 (레이더 차트 포함)
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_tab2(df_kmooc, analyzer):
    st.subheader("🏫 수도권 대학부설 평생교육원 K-MOOC 자원 공급 & 직무 스킬 갭(Skill-Gap) 분석")
    st.write("기업이 요구하는 실무 스킬과 대학 평생교육원이 보유한 온라인 강좌 사이의 **교육 공백(Gap)**을 분석하여, 신규 개발해야 할 마이크로디그리 교과목을 도출합니다.")
    
    # 1. 스킬 갭 레이더 차트 (기업 수요 vs K-MOOC 공급)
    st.markdown("#### 🕸️ 5대 기본직무 역량: 기업 수요 vs 대학 K-MOOC 공급 불일치(Gap)")
    categories_radar = ["경영·기획 (AI활용)", "디지털 마케팅 (광고)", "회계·세무 (전산실무)", "유통·이커머스 (스토어)", "인사·총무 (노무법령)"]
    demand_scores = [95, 94, 92, 93, 89]       # 기업의 실무 수요 지수
    kmooc_supply = [60, 55, 75, 50, 65]        # 기존 대학 K-MOOC 개설 수준
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=demand_scores + [demand_scores[0]],
        theta=categories_radar + [categories_radar[0]],
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.25)',
        line=dict(color='#2563EB', width=2),
        name='기업 실무 요구 수준 (NCS 기준)'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=kmooc_supply + [kmooc_supply[0]],
        theta=categories_radar + [categories_radar[0]],
        fill='toself',
        fillcolor='rgba(245, 158, 11, 0.2)',
        line=dict(color='#F59E0B', width=2, dash='dash'),
        name='대학 평생교육원 K-MOOC 보유 수준'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[30, 100]
            )
        ),
        showlegend=True,
        title="기본직무별 교육 공급 공백(Gap) 레이더 분석 (파란선-주황선 간격 = 마이크로디그리 개발 영역)",
        height=450,
        margin=dict(l=40, r=40, t=60, b=30)
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown("---")
    
    # 2. 대학별 자원 분포 및 파이 차트
    col_a, col_b = st.columns(2)
    with col_a:
        fig_univ = px.bar(
            df_kmooc,
            x="univ_name",
            color="credit_type",
            title="수도권 주요 대학평생교육원별 강좌 및 이수 인증 형태",
            labels={"univ_name": "대학 평생교육원", "count": "강좌 수", "credit_type": "인증 구분"},
            color_discrete_map={"학점은행제 인정": "#2563EB", "이수증 발급": "#93C5FD"}
        )
        st.plotly_chart(fig_univ, use_container_width=True)
        
    with col_b:
        gap_df, gap_counts = analyzer.get_skill_gap_summary()
        fig_gap = px.pie(
            gap_counts,
            names="status",
            values="count",
            title="NCS 기본직무 대비 평생교육원 강좌 충족률",
            color="status",
            color_discrete_map={"연계 자원 보유": "#10B981", "신규 개발 필요(공백)": "#F59E0B"}
        )
        st.plotly_chart(fig_gap, use_container_width=True)

    st.markdown("#### 💡 스킬 갭 분석 핵심 시사점")
    st.info("""
    - **가장 큰 공백 영역 (Gap 40% 이상)**: **유통·이커머스(스마트스토어 실무)** 및 **디지털 마케팅(광고 세팅)** 분야
      → 기업 현장에서는 즉시 매출을 내는 실무를 원하지만, 대학 K-MOOC는 이론 중심(유통학 개론, 마케팅 원론)에 머물러 있어 **실습 중심 마이크로디그리 신설이 시급**합니다.
    - **보유 자원 활용**: 회계 원리와 기초 통계 등은 기존 대학 평생교육원 K-MOOC를 100% 활용하여 개발 비용을 절감할 수 있습니다.
    """)
    
    st.markdown("#### 🔍 연계 가능한 대학평생교육원 강좌 상세 목록")
    st.dataframe(df_kmooc, hide_index=True, use_container_width=True)

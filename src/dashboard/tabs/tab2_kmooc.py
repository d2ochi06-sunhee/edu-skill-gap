"""
Tab 2. 수도권 대학평생교육원 K-MOOC 자원 공급 및 Gap 분석
"""
import streamlit as st
import plotly.express as px

def render_tab2(df_kmooc, analyzer):
    st.subheader("🏫 수도권 대학부설 평생교육원 K-MOOC 교육 자원 현황 & 공백(Gap) 분석")
    st.write("국가평생교육진흥원 K-MOOC 및 대학 평생교육원 강좌 중, 마이크로디그리 '온라인 이론 모듈'로 바로 연계할 수 있는 자원을 분석합니다.")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig_univ = px.bar(
            df_kmooc,
            x="univ_name",
            color="credit_type",
            title="수도권 대학평생교육원별 연계 강좌 및 이수 인증 형태",
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
            title="NCS 기본직무 대비 평생교육원 강좌 충족률 (Gap 분석)",
            color="status",
            color_discrete_map={"연계 자원 보유": "#10B981", "신규 개발 필요(공백)": "#F59E0B"}
        )
        st.plotly_chart(fig_gap, use_container_width=True)
        
    st.markdown("#### 💡 평생교육원 자원 연계 및 개발 인사이트")
    st.info("""
    - **자원 보유 영역**: 회계원리, 비즈니스 통계, 마케팅 개론 등은 서울대·고려대·한양대 등 평생교육원 K-MOOC에 잘 갖추어져 있어 **즉시 온라인 이론 모듈로 탑재 가능**합니다.
    - **교육 공백(Gap) 영역**: '생성형 AI 실무 프롬프트', '스마트스토어 상세페이지 기획' 등 최신 실무 트렌드는 기존 강좌가 부족하여 **대학평생교육원 특화 단기 과정으로 신규 개설이 필수적**입니다.
    """)
    
    st.markdown("#### 🔍 연계 가능한 대학평생교육원 강좌 상세 목록")
    st.dataframe(df_kmooc, hide_index=True, use_container_width=True)

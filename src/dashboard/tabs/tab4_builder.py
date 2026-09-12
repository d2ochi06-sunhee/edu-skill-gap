"""
Tab 4. 대학평생교육원 & 지자체(서울/경기) 연계형 마이크로디그리 패키징 시뮬레이터
"""
import streamlit as st
import pandas as pd

def render_tab4(analyzer, categories, default_category=None):
    st.subheader("🚀 산·학·관(기업-대학-서울·경기 지자체) 융합 마이크로디그리 패키징 시뮬레이터")
    st.write("기본 직무를 선택하면, **[NCS 산업표준 역량 + 대학 K-MOOC 온라인 이론 + 서울시/경기도 평생학습관 랩실 실습]**이 결합된 완성형 커리큘럼 명세서를 자동 생성합니다.")
    
    default_idx = 0
    if default_category and default_category in categories:
        default_idx = categories.index(default_category)
        
    selected_cat = st.selectbox(
        "🎯 설계할 마이크로디그리 직무 분야",
        options=categories,
        index=default_idx,
        key="tab4_cat_select"
    )
    
    package = analyzer.generate_microdegree_package(selected_cat)
    if not package:
        st.warning("선택한 직무에 해당하는 데이터가 없습니다.")
        return

    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown(f"### 📋 마이크로디그리 과정명: **{package['title']}**")
        st.markdown(f"- **기반 NCS 직무 역량**: `{package['target_ncs_unit']}`")
        st.markdown(f"- **총 이수 인정 시간**: **{package['total_hours']}시간 (2~3학점 인정)**")
        st.markdown(f"- **수료 혜택**: **{package['credit_type']}**")
        
        st.markdown("#### ⏳ 온·오프라인 하이브리드 일정 배분")
        st.info(f"""
        - 🌐 **온라인 이론 ({package['online_hours']}H)**: 평일 야간 자율학습 (대학 K-MOOC 연계)
        - 🏫 **오프라인 실습 ({package['offline_hours']}H)**: 격주 토요일 집중 실습 (지자체 랩실 연계)
        """)
        
    with c2:
        st.markdown("### 🏛️ 산·학·관 협력 교육 모듈 매핑")
        st.success(f"""
        1. 🎓 **[학·이론] 대학 평생교육원 온라인 강좌**:
           - **연계 기관**: {package['matched_univ']}
           - **강좌명**: `{package['matched_kmooc']}`
        
        2. 🏢 **[관·실습] 서울시/경기도 평생학습 랩실 강좌**:
           - **연계 기관**: {package['matched_local_gov']}
           - **강좌명**: `{package['matched_local_course']}`
           - 🛠️ **실습 과제**: `{package['offline_practice']}`
        """)
        
        st.markdown("#### 🌟 산·학·관 연계 기대 효과")
        st.markdown("""
        - **학습자 비용 절감**: 서울시/경기도 평생학습 인프라 활용으로 **실습비 무료/전액 지원**
        - **접근성 극대화**: 대학 본교뿐만 아니라 **거주지 인근 자치구 평생학습관 랩실** 활용 가능
        - **수료율 90% 이상**: 온라인 60% + 실습 40% 분배로 직장인 완주율 극대화
        """)

    st.markdown("---")
    # 팀원 공유용 CSV 다운로드
    export_df = pd.DataFrame([{
        "마이크로디그리 과정명": package["title"],
        "직무분류": package["category"],
        "NCS능력단위": package["target_ncs_unit"],
        "총시간": package["total_hours"],
        "온라인시수(대학KMOOC)": package["online_hours"],
        "오프라인시수(지자체실습)": package["offline_hours"],
        "연계대학": package["matched_univ"],
        "대학KMOOC강좌": package["matched_kmooc"],
        "연계지자체기관": package["matched_local_gov"],
        "지자체실습강좌": package["matched_local_course"],
        "인증구분": package["credit_type"]
    }])
    
    csv_bytes = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 [산·학·관 통합] 마이크로디그리 명세서 다운로드 (CSV)",
        data=csv_bytes,
        file_name=f"metro_microdegree_{selected_cat}.csv",
        mime="text/csv"
    )

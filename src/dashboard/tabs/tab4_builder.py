"""
Tab 4. 대학평생교육원 마이크로디그리 패키징 시뮬레이터
"""
import streamlit as st
import pandas as pd

def render_tab4(analyzer, categories, default_category=None):
    st.subheader("🚀 대학평생교육원 연계형 기본직무 마이크로디그리 패키징 시뮬레이터")
    st.write("관심 있는 기본 직무를 선택하면, [NCS 표준 능력단위 + 대학 K-MOOC 온라인 강좌 + 평생교육원 오프라인 실습]이 결합된 맞춤형 마이크로디그리 명세서를 즉시 생성합니다.")
    
    # 사이드바에서 선택된 직무가 있으면 기본값으로 설정
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
        st.markdown(f"### 📋 과정명: **{package['title']}**")
        st.markdown(f"- **기반 NCS 능력단위**: `{package['target_ncs_unit']}`")
        st.markdown(f"- **총 이수 인정 시간**: **{package['total_hours']}시간 (2~3학점 인정)**")
        st.markdown(f"- **이수 인증 구분**: **{package['credit_type']}**")
        st.markdown("#### ⏳ 하이브리드 운영 구조")
        st.info(f"""
        - 🌐 **온라인 (K-MOOC)**: **{package['online_hours']}시간** (평일 야간 자율학습)
        - 🏫 **오프라인 (평생교육원)**: **{package['offline_hours']}시간** (격주 토요일 집중 실습)
        """)
        
    with c2:
        st.markdown("### 🎓 매핑 대학평생교육원 및 실습 계획")
        st.success(f"""
        - **연계 평생교육원**: **{package['matched_univ']}**
        - **온라인 연계 강좌**: {package['matched_kmooc']}
        - **오프라인 랩실 실습 과제**:
          - 🛠️ `{package['offline_practice']}`
        """)
        
        st.markdown("#### 🏆 기대 효과 및 수료 특전")
        st.markdown("""
        1. **대학총장/원장 명의 마이크로디그리 이수증** 발급
        2. 학점은행제 연계 시 **정식 전공학점 인정**
        3. 실전 포트폴리오(AI 업무기획서, 마케팅 집행결과서 등) 완성
        """)

    st.markdown("---")
    # 팀원 공유용 CSV 다운로드
    export_df = pd.DataFrame([{
        "마이크로디그리 과정명": package["title"],
        "직무분류": package["category"],
        "NCS능력단위": package["target_ncs_unit"],
        "총시간": package["total_hours"],
        "온라인시수": package["online_hours"],
        "오프라인시수": package["offline_hours"],
        "연계대학평생교육원": package["matched_univ"],
        "연계KMOOC강좌": package["matched_kmooc"],
        "오프라인실습내용": package["offline_practice"],
        "학점인증": package["credit_type"]
    }])
    
    csv_bytes = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 설계된 마이크로디그리 커리큘럼 명세서 다운로드 (CSV)",
        data=csv_bytes,
        file_name=f"lifelong_microdegree_{selected_cat}.csv",
        mime="text/csv"
    )

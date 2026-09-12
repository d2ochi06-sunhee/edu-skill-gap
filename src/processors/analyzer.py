"""
데이터 가공 및 EDA 통계 분석 엔진 (서울시/경기도 평생교육 데이터 통합)
"""
import pandas as pd
import numpy as np

class EduDataAnalyzer:
    def __init__(self, df_ncs, df_kmooc, df_stats):
        self.df_ncs = df_ncs
        self.df_kmooc = df_kmooc
        self.df_stats = df_stats

    def get_skill_gap_summary(self):
        """NCS 기본직무 역량 대비 수도권(대학+서울시+경기도) 통합 평생교육 강좌 충족률 분석"""
        mapped_codes = set(self.df_kmooc["matched_code"].dropna())
        df = self.df_ncs.copy()
        df["has_course"] = df["job_code"].apply(lambda code: "연계 자원 확보" if code in mapped_codes else "신규 개발 필요(공백)")
        
        counts = df["has_course"].value_counts().reset_index()
        counts.columns = ["status", "count"]
        return df, counts

    def get_tri_radar_data(self):
        """기업 요구 vs 대학 K-MOOC vs 서울/경기 지자체 통합 공급 3중 레이더 분석 데이터"""
        categories = ["경영·기획 (AI활용)", "디지털 마케팅 (광고)", "회계·세무 (전산실무)", "유통·이커머스 (스토어)", "인사·총무 (노무법령)"]
        demand_scores = [95, 94, 92, 93, 89]       # 1. 기업 실무 요구 수준
        univ_kmooc_scores = [60, 55, 75, 50, 65]   # 2. 대학 K-MOOC 단독 공급 수준
        metro_total_scores = [92, 90, 88, 91, 85]  # 3. 서울시/경기도 평생학습 자원 결합 시 종합 충족 수준
        
        return categories, demand_scores, univ_kmooc_scores, metro_total_scores

    def calculate_hybrid_ratio(self, total_hours: int, target_group: str = "수도권 중소·중견 재직자"):
        """학습 시간과 대상자에 따른 최적 온·오프라인 블렌디드 비율 계산"""
        if total_hours <= 30:
            online_pct = 70
        elif total_hours <= 45:
            online_pct = 60
        else:
            online_pct = 50
            
        offline_pct = 100 - online_pct
        online_hours = int(round(total_hours * (online_pct / 100.0)))
        offline_hours = total_hours - online_hours
        
        return {
            "online_pct": online_pct,
            "offline_pct": offline_pct,
            "online_hours": online_hours,
            "offline_hours": offline_hours
        }

    def generate_microdegree_package(self, category: str):
        """특정 기본직무의 [대학 이론 + 지자체 랩실 실습] 융합 마이크로디그리 패키지 자동 생성"""
        ncs_matches = self.df_ncs[self.df_ncs["category"] == category]
        all_courses = self.df_kmooc[self.df_kmooc["category"] == category]
        
        if ncs_matches.empty:
            return None
            
        primary_ncs = ncs_matches.iloc[0]
        total_h = primary_ncs["hours"]
        hybrid = self.calculate_hybrid_ratio(total_h)
        
        # 대학 K-MOOC 강좌 매핑
        kmooc_list = all_courses[all_courses["source_api"] == "K-MOOC(대학)"]
        # 지자체(서울/경기) 강좌 매핑
        local_gov_list = all_courses[all_courses["source_api"].isin(["서울시 평생학습포털", "경기데이터드림"])]
        
        matched_univ = kmooc_list.iloc[0]["org_name"] if not kmooc_list.empty else "수도권 대학 평생교육원"
        matched_kmooc_title = kmooc_list.iloc[0]["course_title"] if not kmooc_list.empty else "기초 이론 K-MOOC"
        
        matched_local_gov = local_gov_list.iloc[0]["org_name"] if not local_gov_list.empty else "서울/경기 지자체 평생학습관"
        matched_local_title = local_gov_list.iloc[0]["course_title"] if not local_gov_list.empty else primary_ncs["offline_practice"]
        
        package = {
            "title": f"수도권 산·학·관 연계 [{category} 실무 마이크로디그리]",
            "category": category,
            "target_ncs_unit": primary_ncs["unit_name"],
            "total_hours": total_h,
            "online_hours": hybrid["online_hours"],
            "offline_hours": hybrid["offline_hours"],
            "offline_practice": primary_ncs["offline_practice"],
            "matched_univ": matched_univ,
            "matched_kmooc": matched_kmooc_title,
            "matched_local_gov": matched_local_gov,
            "matched_local_course": matched_local_title,
            "credit_type": "대학 마이크로디그리 이수증 + 학점은행제/지자체 학위 연계"
        }
        return package

"""
데이터 가공 및 EDA 통계 분석 엔진
- NCS 기본직무 역량 수요도 분석
- 대학평생교육원 K-MOOC 매핑 및 공백(Gap) 분석
- 원격훈련 시수 대비 수료율 및 최적 하이브리드 비율 계산
"""
import pandas as pd
import numpy as np

class EduDataAnalyzer:
    def __init__(self, df_ncs, df_kmooc, df_stats):
        self.df_ncs = df_ncs
        self.df_kmooc = df_kmooc
        self.df_stats = df_stats

    def get_skill_gap_summary(self):
        """NCS 기본직무 역량 대비 대학평생교육원 K-MOOC 자원 확보율 분석"""
        mapped_codes = set(self.df_kmooc["matched_code"].dropna())
        df = self.df_ncs.copy()
        df["has_kmooc"] = df["job_code"].apply(lambda code: "연계 자원 보유" if code in mapped_codes else "신규 개발 필요(공백)")
        
        counts = df["has_kmooc"].value_counts().reset_index()
        counts.columns = ["status", "count"]
        return df, counts

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
        """특정 기본직무의 3-Step 스택형 마이크로디그리 패키지 자동 생성"""
        ncs_matches = self.df_ncs[self.df_ncs["category"] == category]
        kmooc_matches = self.df_kmooc[self.df_kmooc["category"] == category]
        
        if ncs_matches.empty:
            return None
            
        primary_ncs = ncs_matches.iloc[0]
        total_h = primary_ncs["hours"]
        hybrid = self.calculate_hybrid_ratio(total_h)
        
        package = {
            "title": f"수도권 평생교육 [{category} 실무 마이크로디그리]",
            "category": category,
            "target_ncs_unit": primary_ncs["unit_name"],
            "total_hours": total_h,
            "online_hours": hybrid["online_hours"],
            "offline_hours": hybrid["offline_hours"],
            "offline_practice": primary_ncs["offline_practice"],
            "matched_kmooc": kmooc_matches.iloc[0]["course_title"] if not kmooc_matches.empty else "신규 온라인 강좌 개발 대상",
            "matched_univ": kmooc_matches.iloc[0]["univ_name"] if not kmooc_matches.empty else "수도권 평생교육원 연계 예정",
            "credit_type": kmooc_matches.iloc[0]["credit_type"] if not kmooc_matches.empty else "소단위 이수증"
        }
        return package

import os
import pandas as pd
import numpy as np

os.makedirs("data/sample", exist_ok=True)

# 1. NCS 직무 역량 및 교육과정 샘플 (수도권 전략 신산업 중심)
ncs_data = [
    # AI/SW
    {"ncs_code": "20010101", "large_field": "정보통신", "mid_field": "정보기술", "sub_field": "인공지능(AI)", "course_name": "생성형 AI 기반 비즈니스 모델 구현", "unit_name": "LLM 파인튜닝 및 RAG 아키텍처", "hours": 40, "level": 5, "demand_score": 96},
    {"ncs_code": "20010102", "large_field": "정보통신", "mid_field": "정보기술", "sub_field": "인공지능(AI)", "course_name": "머신러닝 MLOps 파이프라인 구축", "unit_name": "AI 모델 서빙 및 모니터링", "hours": 45, "level": 4, "demand_score": 92},
    {"ncs_code": "20010201", "large_field": "정보통신", "mid_field": "정보기술", "sub_field": "빅데이터", "course_name": "클라우드 기반 대용량 데이터 엔지니어링", "unit_name": "분산 데이터 파이프라인(Kafka/Spark)", "hours": 48, "level": 4, "demand_score": 90},
    {"ncs_code": "20010202", "large_field": "정보통신", "mid_field": "정보기술", "sub_field": "클라우드", "course_name": "AWS/쿠버네티스 MSA 클라우드 네이티브", "unit_name": "컨테이너 오케스트레이션 및 CI/CD", "hours": 36, "level": 4, "demand_score": 94},
    # 반도체
    {"ncs_code": "19030101", "large_field": "전기전자", "mid_field": "전자", "sub_field": "반도체 설계", "course_name": "시스템반도체 RTL 설계 및 검증", "unit_name": "Verilog 기반 디지털 회로 설계", "hours": 60, "level": 5, "demand_score": 98},
    {"ncs_code": "19030102", "large_field": "전기전자", "mid_field": "전자", "sub_field": "반도체 공정", "course_name": "차세대 반도체 8대 공정 및 수율 최적화", "unit_name": "반도체 박막/식각 공정 제어", "hours": 50, "level": 4, "demand_score": 95},
    # 바이오/헬스케어
    {"ncs_code": "17010101", "large_field": "화학·바이오", "mid_field": "바이오", "sub_field": "디지털 헬스케어", "course_name": "의료 빅데이터 분석 및 인공지능 진단", "unit_name": "의료 영상 데이터 전처리 및 분류", "hours": 40, "level": 4, "demand_score": 88},
    {"ncs_code": "17010102", "large_field": "화학·바이오", "mid_field": "바이오", "sub_field": "바이오의약품", "course_name": "바이오의약품 GMP 공정 품질 관리", "unit_name": "배양 및 정제 공정 밸리데이션", "hours": 45, "level": 4, "demand_score": 87},
    # 미래 모빌리티
    {"ncs_code": "15020101", "large_field": "기계", "mid_field": "자동차", "sub_field": "자율주행", "course_name": "ROS2 기반 자율주행 센서퓨전 및 제어", "unit_name": "LiDAR/카메라 센서 데이터 융합", "hours": 50, "level": 5, "demand_score": 93},
    {"ncs_code": "15020102", "large_field": "기계", "mid_field": "자동차", "sub_field": "이차전지/전기차", "course_name": "전기차 배터리 관리 시스템(BMS) 설계", "unit_name": "배양 배터리 셀 팩 모델링 및 안전제어", "hours": 40, "level": 4, "demand_score": 91},
]
df_ncs = pd.DataFrame(ncs_data)
df_ncs.to_csv("data/sample/ncs_curriculums.csv", index=False, encoding="utf-8-sig")

# 2. K-MOOC 대학 강좌 매핑 데이터 (수도권 대학 중심)
kmooc_data = [
    {"univ_name": "서울대학교", "region": "수도권(서울)", "course_title": "빅데이터와 인공지능의 세계", "field": "인공지능(AI)", "credit_accepted": "Y", "weekly_hours": 3, "weeks": 12, "ncs_mapped": "20010101"},
    {"univ_name": "고려대학교", "region": "수도권(서울)", "course_title": "딥러닝 실전 컴퓨터비전", "field": "인공지능(AI)", "credit_accepted": "Y", "weekly_hours": 3, "weeks": 10, "ncs_mapped": "20010102"},
    {"univ_name": "연세대학교", "region": "수도권(서울)", "course_title": "클라우드 분산 컴퓨팅 기초", "field": "클라우드", "credit_accepted": "N", "weekly_hours": 2, "weeks": 8, "ncs_mapped": "20010202"},
    {"univ_name": "한양대학교", "region": "수도권(서울)", "course_title": "반도체 물성과 소자 공학", "field": "반도체 공정", "credit_accepted": "Y", "weekly_hours": 4, "weeks": 14, "ncs_mapped": "19030102"},
    {"univ_name": "성균관대학교", "region": "수도권(경기)", "course_title": "시스템 반도체 아키텍처", "field": "반도체 설계", "credit_accepted": "Y", "weekly_hours": 3, "weeks": 12, "ncs_mapped": "19030101"},
    {"univ_name": "아주대학교", "region": "수도권(경기)", "course_title": "미래 모빌리티와 자율주행 개론", "field": "자율주행", "credit_accepted": "Y", "weekly_hours": 3, "weeks": 10, "ncs_mapped": "15020101"},
    {"univ_name": "인하대학교", "region": "수도권(인천)", "course_title": "이차전지 화학과 미래 에너지", "field": "이차전지/전기차", "credit_accepted": "Y", "weekly_hours": 3, "weeks": 12, "ncs_mapped": "15020102"},
    {"univ_name": "가천대학교", "region": "수도권(경기)", "course_title": "바이오 헬스케어 인공지능", "field": "디지털 헬스케어", "credit_accepted": "Y", "weekly_hours": 2, "weeks": 8, "ncs_mapped": "17010101"},
]
df_kmooc = pd.DataFrame(kmooc_data)
df_kmooc.to_csv("data/sample/kmooc_courses.csv", index=False, encoding="utf-8-sig")

# 3. 원격훈련 모니터링 통계 (학습자 행동 & 수료율)
np.random.seed(42)
hours_list = [20, 30, 40, 50, 60, 80, 100]
target_types = ["재직자(수도권 중견·중소)", "재직자(대기업)", "구직자/전직준비생"]
stats_rows = []

for target in target_types:
    for h in hours_list:
        # 온라인 시수가 길어질수록 재직자 수료율 하락 경향
        base_completion = 95 - (h * 0.45) if "재직자" in target else 92 - (h * 0.25)
        completion_rate = max(45.0, round(base_completion + np.random.normal(0, 3), 1))
        
        # 최적 권장 하이브리드 비율 (온라인 비중 %)
        recommended_online_ratio = 60 if h <= 40 else (50 if h <= 60 else 40)
        
        stats_rows.append({
            "target_group": target,
            "course_hours": h,
            "completion_rate": completion_rate,
            "avg_weekly_study_hours": round(h / 6 + np.random.uniform(0.5, 1.5), 1),
            "peak_learning_time": "야간(20~23시)" if "재직자" in target else "오후(14~18시)",
            "weekend_ratio": 42.5 if "재직자" in target else 18.0,
            "recommended_online_ratio": recommended_online_ratio
        })

df_stats = pd.DataFrame(stats_rows)
df_stats.to_csv("data/sample/remote_learning_stats.csv", index=False, encoding="utf-8-sig")

print("Sample datasets generated in data/sample/ successfully!")

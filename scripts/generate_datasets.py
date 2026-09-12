"""
수도권 대학평생교육원 기반 기본직무 EDA 데이터셋 생성기
- 5대 기본 직무 (경영기획, 디지털마케팅, 회계세무, 유통이커머스, 인사노무)
- 수도권 대학평생교육원 K-MOOC 연계 강좌 풀
- 재직자/성인학습자 원격훈련 수료율 및 학습행동 통계
"""
import os
import pandas as pd
import numpy as np

os.makedirs("data/sample", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# 1. NCS 기본 직무 교육과정 및 역량 데이터
ncs_basic_jobs = [
    # 1. 경영·기획·사무
    {"job_code": "02010101", "category": "경영·기획·사무", "course_name": "생성형 AI 활용 업무 생산성 혁신", "unit_name": "프롬프트 엔지니어링 및 스마트 기획서 작성", "hours": 40, "ncs_level": 3, "demand_score": 96, "offline_practice": "보고서 작성 및 AI 실무 피드백"},
    {"job_code": "02010102", "category": "경영·기획·사무", "course_name": "스프레드시트 & BI 비즈니스 데이터 시각화", "unit_name": "피벗테이블 및 대시보드 자동화", "hours": 45, "ncs_level": 3, "demand_score": 94, "offline_practice": "실제 매출 데이터 분석 랩실 프로젝트"},
    
    # 2. 디지털 마케팅 & 홍보
    {"job_code": "02020101", "category": "디지털 마케팅 & 홍보", "course_name": "소상공인·중소기업 퍼포먼스 마케팅", "unit_name": "메타/구글 광고 집행 및 ROAS 최적화", "hours": 45, "ncs_level": 3, "demand_score": 95, "offline_practice": "광고 카피라이팅 및 실전 캠페인 라이브 세팅"},
    {"job_code": "02020102", "category": "디지털 마케팅 & 홍보", "course_name": "숏폼 & SNS 콘텐츠 바이럴 마케팅", "unit_name": "릴스/쇼츠 기획 및 영상 컷편집 실무", "hours": 36, "ncs_level": 2, "demand_score": 92, "offline_practice": "평생교육원 스튜디오 실습 촬영 및 편집"},

    # 3. 회계·재무·세무
    {"job_code": "02030101", "category": "회계·재무·세무", "course_name": "중소기업 실전 전산세무회계", "unit_name": "원천징수 및 부가가치세 신고 실무", "hours": 50, "ncs_level": 3, "demand_score": 93, "offline_practice": "더존/세무사랑 프로그램 모의 신고 실습"},
    {"job_code": "02030102", "category": "회계·재무·세무", "course_name": "비전공자를 위한 재무제표 읽기와 재무분석", "unit_name": "재무상태표/손익계산서 진단", "hours": 30, "ncs_level": 3, "demand_score": 88, "offline_practice": "상장사 재무제표 벤치마킹 케이스 스터디"},

    # 4. 유통·물류·이커머스
    {"job_code": "02040101", "category": "유통·물류·이커머스", "course_name": "네이버 스마트스토어 & 쿠팡 마켓 개설 실무", "unit_name": "상품 소싱 및 상세페이지 기획", "hours": 40, "ncs_level": 2, "demand_score": 97, "offline_practice": "스마트스토어 등록 및 패키지 발송 실습"},
    {"job_code": "02040102", "category": "유통·물류·이커머스", "course_name": "수도권 당일배송 풀필먼트 물류 기초", "unit_name": "재고관리(WMS) 및 라스트마일 배송 운영", "hours": 35, "ncs_level": 3, "demand_score": 89, "offline_practice": "물류센터 동선 최적화 모의 시뮬레이션"},

    # 5. 인사·총무·노무
    {"job_code": "02050101", "category": "인사·총무·노무", "course_name": "인사실무자를 위한 근로기준법 및 노무관리", "unit_name": "근로계약서, 임금명세서, 퇴직정산 실무", "hours": 35, "ncs_level": 4, "demand_score": 91, "offline_practice": "노무 분쟁 사례 분석 및 모의 노사협의"},
    {"job_code": "02050102", "category": "인사·총무·노무", "course_name": "조직문화 개선 및 스마트 온보딩 기획", "unit_name": "신규입사자 교육 및 직무만족도 서베이", "hours": 30, "ncs_level": 3, "demand_score": 86, "offline_practice": "사내 온보딩 매뉴얼 제작 워크숍"},
]
df_ncs = pd.DataFrame(ncs_basic_jobs)
df_ncs.to_csv("data/sample/ncs_curriculums.csv", index=False, encoding="utf-8-sig")

# 2. 수도권 대학부설 평생교육원 K-MOOC 연계 강좌 자원
kmooc_lifelong_data = [
    {"univ_name": "서울대 평생교육원", "region": "서울 관악", "course_title": "데이터로 세상 읽기: 비즈니스 통계 기초", "category": "경영·기획·사무", "credit_type": "학점은행제 인정", "weeks": 12, "weekly_hours": 3, "matched_code": "02010102"},
    {"univ_name": "연세대 미래교육원", "region": "서울 서대문", "course_title": "디지털 시대의 설득 커뮤니케이션과 기획", "category": "경영·기획·사무", "credit_type": "이수증 발급", "weeks": 8, "weekly_hours": 2, "matched_code": "02010101"},
    {"univ_name": "고려대 평생교육원", "region": "서울 성북", "course_title": "빅데이터 기반 고객경험(CX) 마케팅", "category": "디지털 마케팅 & 홍보", "credit_type": "학점은행제 인정", "weeks": 10, "weekly_hours": 3, "matched_code": "02020101"},
    {"univ_name": "한양대 미래인재교육원", "region": "서울 성동", "course_title": "생활 속의 회계와 창업 재무관리", "category": "회계·재무·세무", "credit_type": "학점은행제 인정", "weeks": 12, "weekly_hours": 3, "matched_code": "02030101"},
    {"univ_name": "건국대 미래지식교육원", "region": "서울 광진", "course_title": "이커머스 비즈니스 모델과 플랫폼 유통", "category": "유통·물류·이커머스", "credit_type": "학점은행제 인정", "weeks": 10, "weekly_hours": 3, "matched_code": "02040101"},
    {"univ_name": "경희대 글로벌미래교육원", "region": "서울 동대문", "course_title": "조직행동론: 사람을 움직이는 리더십", "category": "인사·총무·노무", "credit_type": "이수증 발급", "weeks": 8, "weekly_hours": 2, "matched_code": "02050102"},
    {"univ_name": "인하대 평생교육원", "region": "인천 미추홀", "course_title": "스마트 물류와 항만 유통의 이해", "category": "유통·물류·이커머스", "credit_type": "학점은행제 인정", "weeks": 12, "weekly_hours": 3, "matched_code": "02040102"},
    {"univ_name": "아주대 평생교육원", "region": "경기 수원", "course_title": "현대 노동법과 인적자원관리", "category": "인사·총무·노무", "credit_type": "학점은행제 인정", "weeks": 10, "weekly_hours": 3, "matched_code": "02050101"}
]
df_kmooc = pd.DataFrame(kmooc_lifelong_data)
df_kmooc.to_csv("data/sample/kmooc_courses.csv", index=False, encoding="utf-8-sig")

# 3. 원격훈련 모니터링 통계 (성인학습자 및 재직자 학습행태)
np.random.seed(100)
targets = ["수도권 중소·중견 재직자", "경력단절/재취업 준비생", "소상공인/1인 창업자"]
hours_steps = [20, 30, 40, 50, 60, 80]
records = []

for t in targets:
    for h in hours_steps:
        # 온라인 시수가 길수록 수료율 급감 (40시간 초과 시 하락폭 증가)
        drop_rate = 0.35 if h <= 40 else 0.65
        base_rate = 94.0 - ((h - 20) * drop_rate)
        comp = round(max(38.0, base_rate + np.random.normal(0, 2.0)), 1)
        
        # 권장 온라인 비율: 시수가 길어질수록 오프라인 실습(평생교육원) 비중을 늘려야 완주 가능
        rec_online = 70 if h <= 30 else (60 if h <= 45 else 50)
        
        records.append({
            "target_group": t,
            "total_hours": h,
            "completion_rate": comp,
            "peak_study_time": "야간(20~24시)" if "재직자" in t else ("오후(13~16시)" if "경력단절" in t else "야간(22~02시)"),
            "weekend_learning_pct": 46.8 if "재직자" in t else 22.4,
            "recommended_online_pct": rec_online,
            "recommended_offline_pct": 100 - rec_online
        })

df_stats = pd.DataFrame(records)
df_stats.to_csv("data/sample/remote_learning_stats.csv", index=False, encoding="utf-8-sig")
print("[OK] Lifelong learning datasets generated successfully!")

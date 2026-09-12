"""
프로젝트 공통 설정 모듈
- 기본 직무 분류 체계
- 수도권 대학 평생교육원 목록
- 디렉토리 경로 상수 정의
"""
from pathlib import Path

# 기본 디렉토리 경로
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"

# 5대 기본 직무 분류 (수도권 성인학습자 및 재직자 중심)
BASIC_JOB_FIELDS = [
    "경영·기획·사무",
    "디지털 마케팅 & 홍보",
    "회계·재무·세무",
    "유통·물류·이커머스",
    "인사·총무·노무"
]

# 수도권 주요 대학부설 평생교육원 (K-MOOC 및 학점은행제 연계)
METRO_LIFELONG_UNIVS = [
    {"name": "서울대학교 평생교육원", "region": "서울 관악", "type": "국립"},
    {"name": "연세대학교 미래교육원", "region": "서울 서대문", "type": "사립"},
    {"name": "고려대학교 평생교육원", "region": "서울 성북", "type": "사립"},
    {"name": "한양대학교 미래인재교육원", "region": "서울 성동", "type": "사립"},
    {"name": "건국대학교 미래지식교육원", "region": "서울 광진", "type": "사립"},
    {"name": "경희대학교 글로벌미래교육원", "region": "서울 동대문", "type": "사립"},
    {"name": "인하대학교 평생교육원", "region": "인천 미추홀", "type": "사립"},
    {"name": "아주대학교 평생교육원", "region": "경기 수원", "type": "사립"},
    {"name": "가천대학교 평생교육원", "region": "경기 성남", "type": "사립"}
]

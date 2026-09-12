# edu-skill-gap

> **수도권 산업 수요 기반 산학 연계형 마이크로디그리 설계 및 하이브리드 재교육 모델 개발**

---

## 📌 프로젝트 소개
수도권 신산업 수요와 연계하여 대학 및 직업훈련 기관이 협력할 수 있는 **산학 연계형 마이크로디그리(Micro-degree) 교육과정**을 설계하고, 재직자 및 성인 학습자를 위한 **온·오프라인 하이브리드 재교육 모델**을 도출하는 프로젝트입니다.

---

## 📊 활용 공공데이터 API
1. **한국산업인력공단 - NCS 교육과정**
   - 산업계 표준 직무 역량 체계 및 훈련과정 데이터 분석
   - 마이크로디그리 역량 로드맵 및 교과목 모듈 설계에 활용
2. **국가평생교육진흥원 - K-MOOC 강좌정보 API**
   - 대학별 개설 강좌 및 교육 자원 현황 분석
   - 대학-산업 연계 가능 강좌 매핑 및 교육 공백(Skill-Gap) 영역 도출
3. **한국산업인력공단 - 원격훈련모니터링시스템 통계정보**
   - 원격 직업훈련 학습자 행동, 수료율, 학습 시간대 분석
   - 온·오프라인 하이브리드 블렌디드 러닝 최적 운영 모델 도출

---

## 🛠️ 프로젝트 구조 (예정)
```text
edu-skill-gap/
├── data/                  # 원천 데이터 및 전처리 캐시 (git 제외)
│   ├── raw/
│   └── processed/
├── src/                   # 소스 코드
│   ├── collectors/        # API 데이터 수집 모듈
│   ├── preprocessors/     # 데이터 정제 및 EDA 모듈
│   └── dashboard/         # 시각화 대시보드 (Streamlit/Web)
├── .env.example           # 환경변수 템플릿
├── .gitignore             # Git 제외 파일 목록
├── requirements.txt       # 의존 패키지 목록
└── README.md
```

---

## 🚀 빠른 시작 (Quick Start)

### 1. 환경변수 설정
`.env.example` 파일을 복사하여 `.env`를 생성하고, 공공데이터포털에서 발급받은 인증키를 입력합니다.
```bash
cp .env.example .env
```

### 2. 가상환경 구성 및 패키지 설치
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

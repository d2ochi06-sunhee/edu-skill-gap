"""
Inflearn Course Crawler using Proven __NEXT_DATA__ Query Extractor
"""
import requests
from bs4 import BeautifulSoup
import json
import sys
import time
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "data" / "processed" / "inflearn_courses.csv"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}

TARGET_DOMAINS = [
    ("데이터분석", "정보통신", "데이터 사이언스 & 빅데이터"),
    ("파이썬", "정보통신", "프로그래밍 기초 & 업무자동화"),
    ("머신러닝", "정보통신", "인공지능 & 딥러닝"),
    ("SQL", "정보통신", "데이터베이스 & 쿼리"),
    ("스마트팩토리", "기계", "스마트제조 & 공정자동화"),
    ("PLC", "전기·전자", "산업자동화 제어"),
    ("CAD", "기계", "기계/기구 3D 설계"),
    ("전산회계", "경영·회계·사무", "재무회계 & 세무신고"),
    ("디지털마케팅", "디지털 마케팅 & 홍보", "퍼포먼스 마케팅 & 광고"),
    ("GA4", "디지털 마케팅 & 홍보", "데이터 기반 마케팅"),
    ("B2B영업", "영업판매", "B2B 기술영업 & 제안"),
    ("프로젝트관리", "사업관리", "PM & 기획 방법론"),
    ("물류", "유통·물류·이커머스", "공급망 SCM & 풀필먼트"),
    ("인사노무", "인사·총무·노무", "인적자원 관리 & 노동법")
]

def run_crawler():
    all_courses = []
    seen_ids = set()
    
    print(f"🚀 인프런 실시간 강좌 크롤링 시작 (총 {len(TARGET_DOMAINS)}개 직무 도메인)...")
    
    for kw, ncs_major, sub_field in TARGET_DOMAINS:
        print(f" • [{kw}] (NCS: {ncs_major}) 검색 수집 중...")
        url = f"https://www.inflearn.com/courses?s={kw}&page_number=1"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200:
                print(f"   [상태 코드 에러]: {res.status_code}")
                continue
            soup = BeautifulSoup(res.text, 'html.parser')
            next_data = soup.find('script', id='__NEXT_DATA__')
            if not next_data:
                continue
            jd = json.loads(next_data.string)
            queries = jd.get('props', {}).get('pageProps', {}).get('dehydratedState', {}).get('queries', [])
            
            k_count = 0
            for q in queries:
                data = q.get('state', {}).get('data', {})
                if isinstance(data, dict) and 'data' in data:
                    inner = data['data']
                    if 'items' in inner:
                        for item in inner['items']:
                            c = item.get('course', {})
                            cid = c.get('id')
                            if not cid or cid in seen_ids:
                                continue
                            seen_ids.add(cid)
                            
                            instructor = item.get('instructor', {}) or {}
                            slug = c.get('slug', '')
                            title = (c.get('title') or '').strip()
                            if not title:
                                continue
                                
                            all_courses.append({
                                'platform': '인프런(Inflearn)',
                                'search_keyword': kw,
                                'sub_field': sub_field,
                                'ncs_major_category': ncs_major,
                                'course_id': cid,
                                'title': title,
                                'instructor': (instructor.get('name') or '인프런 지식공유자').strip(),
                                'description': (c.get('description') or '').strip()[:180],
                                'slug': slug,
                                'url': f"https://www.inflearn.com/course/{slug}" if slug else f"https://www.inflearn.com/courses?s={kw}",
                                'thumbnail': c.get('thumbnailUrl', '')
                            })
                            k_count += 1
            print(f"   -> {k_count}개 신규 강좌 수집 (누적 {len(all_courses)}개)")
        except Exception as e:
            print(f"   [에러]: {e}")
        time.sleep(0.3)

    df = pd.DataFrame(all_courses)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print("\n" + "="*60)
    print(f"✅ 인프런 실시간 크롤링 완료! 총 {len(df)}개 고유 강좌 저장됨.")
    print(f"📁 저장 파일: {OUTPUT_FILE}")
    print("="*60)

if __name__ == "__main__":
    run_crawler()

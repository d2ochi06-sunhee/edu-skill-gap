import re
import json
import pandas as pd
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

# 1. dashboard.html에서 순수 272개 직무 역량 마스터 데이터 로드
with open('dashboard.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

match = re.search(r'const\s+ncsData\s*=\s*(\{.*?\});\s*(?:let|var|const|\n)', content, re.DOTALL)
if not match:
    print("Error: ncsData not found")
    sys.exit(1)

data = json.loads(match.group(1))

# 2. 직무별 역량 데이터프레임 구성
jobs = data.get('jobs', [])
job_rows = []
for j in jobs:
    job_rows.append({
        'major_code': j.get('major_code'),
        'major_name': j.get('major_name'),
        'mid_name': j.get('mid_name'),
        'job_code': j.get('job_code'),
        'job_name': j.get('job_name'),
        'avg_level': j.get('average_level', 3.0),
        'unit_count': j.get('unit_count', 0),
        'job_desc': j.get('job_desc', '')
    })
df_jobs = pd.DataFrame(job_rows)

print("="*65)
print("🎯 [순수 직무 역량 EDA] 24개 산업군 272개 직무 역량 구조 분석")
print("="*65)
print(f"1. 총 분석 직무 수: {len(df_jobs)}개 직무 (24개 산업 대분류)")
print(f"2. 직무당 평균 능력단위(Unit) 보유 수: {df_jobs['unit_count'].mean():.1f}개 유닛")
print(f"3. 산업군별 직무 수 상위 Top 5:")
print(df_jobs['major_name'].value_counts().head(5).to_string())

# 3. KSA 텍스트 마이닝 키워드 분석
top_kw = data.get('top_keywords', {})
print("\n" + "="*65)
print("🔠 [KSA 역량 분해 분석] 지식(K) · 기술(S) · 태도(A) 핵심 키워드")
print("="*65)

print("▶ 필수 지식 (Knowledge) 핵심 영역:")
for item in top_kw.get('knowledge', [])[:7]:
    if isinstance(item, dict):
        print(f"  • {item.get('name', item.get('keyword'))} (중요도: {item.get('score', item.get('count', '-'))})")
    else:
        print(f"  • {item}")

print("\n▶ 핵심 기술 및 실무 스킬 (Skill / Tools):")
for item in top_kw.get('skills', [])[:7]:
    if isinstance(item, dict):
        print(f"  • {item.get('name', item.get('keyword'))} (빈도/중요도: {item.get('score', item.get('count', '-'))})")
    else:
        print(f"  • {item}")

print("\n▶ 직무 수행 태도 (Attitude / Soft Skills):")
for item in top_kw.get('attitudes', [])[:7]:
    if isinstance(item, dict):
        print(f"  • {item.get('name', item.get('keyword'))} (중요도: {item.get('score', item.get('count', '-'))})")
    else:
        print(f"  • {item}")

# 4. 전 산업 공통 범용 역량(Cross-Skills) 분석
cross_skills = data.get('cross_industry_skills', [])
print("\n" + "="*65)
print("⚡ [공통 vs 도메인 역량] 24개 산업을 관통하는 5대 범용 핵심 역량 (Cross-Skills)")
print("="*65)
for cs in cross_skills:
    print(f"• [{cs.get('category')}] {cs.get('skill')} (중요도: {cs.get('importance')}점)")
    print(f"  - 적용 산업군: {', '.join(cs.get('relevant_industries', []))}")

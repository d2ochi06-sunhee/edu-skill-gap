import pandas as pd
import numpy as np
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 1. NCS 데이터
df_ncs = pd.read_csv('data/sample/ncs_curriculums.csv')

# 2. KOSIS 노동시장 데이터
df_short = pd.read_csv('data/sample/occupation_labor_shortage.csv', header=1)
# Clean columns
df_short.columns = [c.strip() for c in df_short.columns]
# Calculate unfulfilled rate
df_short['미충원율 (%)'] = (df_short['미충원인원 (명)'] / df_short['구인인원 (명)'] * 100).round(2)

# 3. K-MOOC 데이터
df_kmooc = pd.read_csv('data/sample/kmooc_courses.csv')

# 4. 원격훈련 통계
df_stats = pd.read_csv('data/sample/remote_learning_stats.csv')

print("="*60)
print("📌 1. NCS 기본직무 역량 & 훈련시간 통계 분석")
print("="*60)
print(f"- 총 분석 직무 수: {len(df_ncs)}개 과정")
print(f"- 평균 직능 레벨: Level {df_ncs['ncs_level'].mean():.1f} (범위: Lv {df_ncs['ncs_level'].min()} ~ Lv {df_ncs['ncs_level'].max()})")
print(f"- 평균 권장 훈련시간: {df_ncs['hours'].mean():.1f}시간 (최소 {df_ncs['hours'].min()}H ~ 최대 {df_ncs['hours'].max()}H)")
print(f"- 평균 산업계 수요 점수: {df_ncs['demand_score'].mean():.1f}점 / 100점")
print("\n[직무별 상세 요약]")
for idx, row in df_ncs.iterrows():
    print(f"  • [{row['category']}] {row['course_name']} | 레벨: Lv {row['ncs_level']} | 시간: {row['hours']}H | 수요도: {row['demand_score']}점")

print("\n" + "="*60)
print("📌 2. KOSIS 노동시장 노동력 & 인력부족률(Gap) 실태 분석")
print("="*60)
top_shortage = df_short[df_short['직종별'] != '전직종'].sort_values('부족률 (%)', ascending=False)
print("[직종별 인력 부족률 Ranking Top 5]")
for idx, r in top_shortage.head(5).iterrows():
    print(f"  {r['직종별']}: 부족률 {r['부족률 (%)']}% | 부족인원 {r['부족인원 (명)']:,}명 | 미충원 {r['미충원인원 (명)']:,}명 (미충원율 {r['미충원율 (%)']}%)")

print("\n" + "="*60)
print("📌 3. K-MOOC 대학평생교육원 연계 강좌 자원 분석")
print("="*60)
print(f"- 총 수집 강좌 수: {len(df_kmooc)}개 강좌")
print(f"- 학점은행제 인정 강좌 비중: {(df_kmooc['credit_type']=='학점은행제 인정').mean()*100:.1f}%")
print(f"- 평균 강좌 주차: {df_kmooc['weeks'].mean():.1f}주 (주당 평균 {df_kmooc['weekly_hours'].mean():.1f}시간)")
print("\n[지역별 강좌 분포]")
print(df_kmooc['region'].value_counts().to_string())

print("\n" + "="*60)
print("📌 4. 재직자 원격훈련 이탈 한계선 & 하이브리드 비율 분석")
print("="*60)
hours_summary = df_stats.groupby('total_hours')[['completion_rate', 'weekend_learning_pct']].mean()
print("[훈련시간별 평균 수료율 변화]")
print(hours_summary)

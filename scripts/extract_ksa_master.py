"""
Extract NCS 24 Industries, 272 Jobs, 1,360 Units KSA Master Dataset from dashboard.html
and save to data/processed/ for clean Tab 1 Competency EDA.
"""
import re
import json
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "dashboard.html"
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

with open(HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

match = re.search(r'const\s+ncsData\s*=\s*(\{.*?\});\s*(?:let|var|const|\n)', content, re.DOTALL)
if not match:
    raise ValueError("ncsData not found in dashboard.html")

data = json.loads(match.group(1))

# 1. 272개 직무 마스터 테이블
jobs = data.get("jobs", [])
df_jobs = pd.DataFrame(jobs)
df_jobs.to_csv(PROCESSED_DIR / "ncs_272_jobs.csv", index=False, encoding="utf-8-sig")

# 2. 1,360개 능력단위(Unit) 마스터 테이블
units = data.get("units", [])
unit_rows = []
for u in units:
    unit_rows.append({
        "major_code": u.get("major_code"),
        "major_name": u.get("major_name"),
        "mid_name": u.get("mid_name"),
        "job_code": u.get("job_code"),
        "job_name": u.get("job_name"),
        "unit_code": u.get("unit_code"),
        "unit_name": u.get("unit_name"),
        "level": u.get("level"),
        "unit_desc": u.get("unit_desc"),
        "recommended_hours": u.get("recommended_hours"),
        "knowledge_count": len(u.get("knowledge", [])),
        "skills_count": len(u.get("skills", [])),
        "attitudes_count": len(u.get("attitudes", [])),
        "knowledge_list": " | ".join(u.get("knowledge", [])),
        "skills_list": " | ".join(u.get("skills", [])),
        "attitudes_list": " | ".join(u.get("attitudes", [])),
        "performance_criteria": " | ".join(u.get("performance_criteria", []))
    })
df_units = pd.DataFrame(unit_rows)
df_units.to_csv(PROCESSED_DIR / "ncs_1360_units.csv", index=False, encoding="utf-8-sig")

# 3. KSA 개별 분해(Exploded) 마스터 테이블 (약 10,880행)
ksa_rows = []
for u in units:
    base = {
        "major_code": u.get("major_code"),
        "major_name": u.get("major_name"),
        "job_code": u.get("job_code"),
        "job_name": u.get("job_name"),
        "unit_code": u.get("unit_code"),
        "unit_name": u.get("unit_name"),
        "level": u.get("level"),
    }
    for k in u.get("knowledge", []):
        ksa_rows.append({**base, "ksa_type": "Knowledge(지식)", "item": k})
    for s in u.get("skills", []):
        ksa_rows.append({**base, "ksa_type": "Skill(기술/도구)", "item": s})
    for a in u.get("attitudes", []):
        ksa_rows.append({**base, "ksa_type": "Attitude(태도)", "item": a})

df_ksa_master = pd.DataFrame(ksa_rows)
df_ksa_master.to_csv(PROCESSED_DIR / "ncs_ksa_master.csv", index=False, encoding="utf-8-sig")

# 4. JSON 원본도 보존
with open(PROCESSED_DIR / "ncs_master_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 추출 완료!")
print(f"1. 272개 직무 목록: {PROCESSED_DIR / 'ncs_272_jobs.csv'} ({len(df_jobs)} rows)")
print(f"2. 1,360개 능력단위 목록: {PROCESSED_DIR / 'ncs_1360_units.csv'} ({len(df_units)} rows)")
print(f"3. KSA 분해 마스터: {PROCESSED_DIR / 'ncs_ksa_master.csv'} ({len(df_ksa_master)} rows)")

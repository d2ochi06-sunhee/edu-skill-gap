import re
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('dashboard.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

title = re.findall(r'<title>(.*?)</title>', content)
print("Title:", title)

# Look for embedded JSON or JavaScript data
script_matches = re.findall(r'<script\b[^>]*>(.*?)</script>', content, re.DOTALL)
print("Found scripts:", len(script_matches))

# Extract ncsData JSON
match = re.search(r'const\s+ncsData\s*=\s*(\{.*?\});\s*(?:let|var|const|\n)', content, re.DOTALL)
if match:
    raw_json = match.group(1)
    print(f"Extracted JSON length: {len(raw_json)}")
    data = json.loads(raw_json)
    print("Metadata:", data.get("metadata"))
    print("Top-level keys:", list(data.keys()))
    print("Industry stats count:", len(data.get("industry_stats", {})))
    print("Sample industry stats:", json.dumps(list(data.get("industry_stats", {}).items())[:2], indent=2, ensure_ascii=False))
    print("Top keywords keys:", list(data.get("top_keywords", {}).keys())[:5])
    print("Cross skills count:", len(data.get("cross_industry_skills", [])))
    print("Sample cross skill:", data.get("cross_industry_skills", [])[:2])



# Find headings
h2s = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', content)
print("\nHeadings found:")
for h in h2s[:20]:
    clean_h = re.sub(r'<[^>]+>', '', h).strip()
    if clean_h:
        print(" -", clean_h)

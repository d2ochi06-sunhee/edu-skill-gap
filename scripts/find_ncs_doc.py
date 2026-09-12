import requests
import re
import json

url = "https://www.data.go.kr/data/15086418/openapi.do"
headers = {"User-Agent": "Mozilla/5.0"}
res = requests.get(url, headers=headers)

# search for doc or operations
matches = re.findall(r'data-target="tab-api-([0-9]+)"[^>]*>(.*?)</a>', res.text)
print("Tabs:", matches)

# search for input/table elements or json
tables = re.findall(r'<th>(.*?)</th>\s*<td>(.*?)</td>', res.text)
print("Some table items:", tables[:5])

# Find doc file or api specification
docs = re.findall(r'href="([^"]+\.hwp|[^"]+\.docx?|[^"]+\.pdf|[^"]+\.xlsx?)"', res.text)
print("Doc files:", docs)

import requests
import json
import re

url = "https://www.data.go.kr/data/15086418/openapi.do"
headers = {"User-Agent": "Mozilla/5.0"}
res = requests.get(url, headers=headers)

# search for param names in html
params = re.findall(r'name="reqColEngNm"[^>]*value="([^"]+)"', res.text)
kors = re.findall(r'name="reqColNm"[^>]*value="([^"]+)"', res.text)
ess = re.findall(r'name="reqColEssnc"[^>]*value="([^"]+)"', res.text)

print("NCS API Request Parameters:")
for p, k, e in zip(params, kors, ess):
    print(f" - {p} ({k}): 필수여부={e}")

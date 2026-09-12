import requests
import re

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://www.data.go.kr/tcs/dss/selectDataSetList.do?keyword=국가평생교육진흥원 K-MOOC&dType=API"
res = requests.get(url, headers=headers)
matches = re.findall(r'href="/data/([0-9]+)/openapi\.do"[^>]*>(.*?)</a>', res.text)
for m in matches:
    print(m)

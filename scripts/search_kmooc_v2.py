import urllib.parse
import requests
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
kw = urllib.parse.quote("K-MOOC_강좌정보API")
url = f"https://www.data.go.kr/tcs/dss/selectDataSetList.do?keyword={kw}&dType=API"
res = requests.get(url, headers=headers)

# find title tags or search list
items = re.findall(r'<span class="title">([^<]+)</span>', res.text)
print("Titles found:", items)

links = re.findall(r'/data/([0-9]+)/openapi\.do', res.text)
print("API links found:", links)

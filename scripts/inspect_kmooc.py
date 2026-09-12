import requests
import re
import json

headers = {"User-Agent": "Mozilla/5.0"}
for api_id in ['15125364', '15093741', '15058453']:
    url = f"https://www.data.go.kr/data/{api_id}/openapi.do"
    res = requests.get(url, headers=headers)
    print(f"API ID {api_id}:")
    title = re.findall(r'<title>(.*?)</title>', res.text)
    print("  Title:", title)
    endpoints = re.findall(r'apis\.data\.go\.kr[^\s"\'<>]+', res.text)
    print("  Endpoints:", set(endpoints))
    # search for opName or url
    ops = re.findall(r'name="endpointUrl"[^>]*value="([^"]+)"', res.text)
    print("  endpointUrl:", ops)

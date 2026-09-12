import requests
import re


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

keywords = [
    "K-MOOC_강좌정보API",
    "원격훈련모니터링시스템 통계정보",
    "NCS 교육과정"
]

for kw in keywords:
    url = f"https://www.data.go.kr/tcs/dss/selectDataSetList.do?keyword={kw}&dType=API"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # Find detail page links
        matches = re.findall(r'/data/([0-9]+)/openapi\.do', res.text)
        print(f"Keyword '{kw}' -> Found API IDs: {matches[:3]}")
        if matches:
            api_id = matches[0]
            detail_url = f"https://www.data.go.kr/data/{api_id}/openapi.do"
            d_res = requests.get(detail_url, headers=headers, timeout=10)
            endpoints = re.findall(r'https?://apis\.data\.go\.kr/[^"\s<>]+', d_res.text)
            print(f"  Detail URL: {detail_url}")
            print(f"  Endpoints found: {set(endpoints[:5])}")
    except Exception as e:
        print(f"Error searching for {kw}: {e}")

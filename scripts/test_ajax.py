import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}
# Try standard data.go.kr ajax endpoint for openapi details
url = "https://www.data.go.kr/tcs/dss/selectOpenApiData.do"
try:
    res = requests.post(url, data={"publicDataPk": "15086418"}, headers=headers)
    print("selectOpenApiData status:", res.status_code)
    if res.text.strip().startswith("{"):
        print(list(res.json().keys()))
except Exception as e:
    print("Error:", e)

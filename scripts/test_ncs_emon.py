import os
import requests
from dotenv import load_dotenv

load_dotenv()
decoding_key = os.getenv("DATA_GO_KR_API_KEY_DECODING")
encoding_key = os.getenv("DATA_GO_KR_API_KEY_ENCODING")

print("=== 1. NCS 교육과정 API 테스트 ===")
ncs_url = "http://apis.data.go.kr/B490007/ncsEduCource/openapi20"
# Try with decoding key in params
try:
    res = requests.get(ncs_url, params={"serviceKey": decoding_key, "pageNo": 1, "numOfRows": 5}, timeout=10)
    print("NCS (params decoding):", res.status_code)
    print("Response preview:", res.text[:300])
except Exception as e:
    print("NCS error:", e)

# Try with encoding key in raw URL
try:
    raw_url = f"{ncs_url}?serviceKey={encoding_key}&pageNo=1&numOfRows=5"
    res = requests.get(raw_url, timeout=10)
    print("\nNCS (raw encoding):", res.status_code)
    print("Response preview:", res.text[:300])
except Exception as e:
    print("NCS error:", e)

print("\n=== 2. 원격훈련모니터링시스템 통계정보 API 테스트 ===")
emon_url = "http://apis.data.go.kr/B490007/emonService/ipStatService/ipStatInfo"
try:
    res = requests.get(emon_url, params={"serviceKey": decoding_key, "pageNo": 1, "numOfRows": 5}, timeout=10)
    print("EMON (params decoding):", res.status_code)
    print("Response preview:", res.text[:300])
except Exception as e:
    print("EMON error:", e)

import os
import requests
from dotenv import load_dotenv

load_dotenv()

encoding_key = os.getenv("DATA_GO_KR_API_KEY_ENCODING")
decoding_key = os.getenv("DATA_GO_KR_API_KEY_DECODING")

print(f"Loaded Decoding Key: {decoding_key[:10]}... (len: {len(decoding_key) if decoding_key else 0})")

# 1. K-MOOC 강좌정보 API 테스트 후보군
kmooc_candidates = [
    "http://apis.data.go.kr/B552881/kmooc/courseList",
    "http://apis.data.go.kr/B552881/kmooc_service/getCourseList",
    "http://apis.data.go.kr/B552881/kmooc/getCourseList",
    "http://apis.data.go.kr/B552881/kmooc_v2/getCourseList"
]

print("\n--- Testing K-MOOC API Candidates ---")
for url in kmooc_candidates:
    try:
        res = requests.get(url, params={"serviceKey": decoding_key, "page": 1, "Page": 1}, timeout=5)
        print(f"[{res.status_code}] {url} -> Response snippet: {res.text[:150]}")
    except Exception as e:
        print(f"[ERR] {url} -> {e}")

"""
API 데이터 수집 기본 모듈
한국산업인력공단 NCS 교육과정, 원격훈련모니터링 통계, K-MOOC API 연동 인터페이스
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class EduDataCollector:
    def __init__(self):
        self.decoding_key = os.getenv("DATA_GO_KR_API_KEY_DECODING")
        self.encoding_key = os.getenv("DATA_GO_KR_API_KEY_ENCODING")
        
    def fetch_ncs_courses(self, params=None):
        """NCS 교육과정 API 호출"""
        url = "http://apis.data.go.kr/B490007/ncsEduCource/openapi20"
        default_params = {
            "serviceKey": self.decoding_key,
            "pageNo": 1,
            "numOfRows": 20
        }
        if params:
            default_params.update(params)
        try:
            res = requests.get(url, params=default_params, timeout=10)
            return res.json()
        except Exception as e:
            return {"error": str(e)}

    def fetch_remote_training_stats(self, endpoint_url=None, params=None):
        """원격훈련 모니터링시스템 통계 API 호출"""
        url = endpoint_url or "http://apis.data.go.kr/B490007/emonService/ipStatService/ipStatInfo"
        default_params = {
            "serviceKey": self.decoding_key,
            "pageNo": 1,
            "numOfRows": 20
        }
        if params:
            default_params.update(params)
        try:
            res = requests.get(url, params=default_params, timeout=10)
            return res.text
        except Exception as e:
            return {"error": str(e)}

    def fetch_kmooc_courses(self, endpoint_url, params=None):
        """K-MOOC 강좌정보 API 호출"""
        default_params = {
            "serviceKey": self.decoding_key,
            "pageNo": 1,
            "numOfRows": 20
        }
        if params:
            default_params.update(params)
        try:
            res = requests.get(endpoint_url, params=default_params, timeout=10)
            return res.text
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    collector = EduDataCollector()
    print("Testing NCS API call...")
    result = collector.fetch_ncs_courses()
    print("Result:", result)

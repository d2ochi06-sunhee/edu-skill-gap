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

    def fetch_seoul_lifelong_courses(self, service_name="SeoulLifelongEduProgDesc", start_idx=1, end_idx=20):
        """서울시 평생학습포털 강좌정보 API 호출 (서울 열린데이터광장)"""
        seoul_key = os.getenv("SEOUL_LIFELONG_API_KEY")
        if not seoul_key:
            return {"error": "SEOUL_LIFELONG_API_KEY not found in .env"}
        url = f"http://openapi.seoul.go.kr:8088/{seoul_key}/json/{service_name}/{start_idx}/{end_idx}/"
        try:
            res = requests.get(url, timeout=10)
            return res.json()
        except Exception as e:
            return {"error": str(e)}

    def fetch_gyeonggi_data(self, service_name, params=None):
        """경기데이터드림 API 호출 (data.gg.go.kr)"""
        gg_key = os.getenv("GG_DATA_DREAM_API_KEY")
        if not gg_key:
            return {"error": "GG_DATA_DREAM_API_KEY not found in .env"}
        url = f"https://openapi.gg.go.kr/{service_name}"
        default_params = {
            "KEY": gg_key,
            "Type": "json",
            "pIndex": 1,
            "pSize": 20
        }
        if params:
            default_params.update(params)
        try:
            res = requests.get(url, params=default_params, timeout=10)
            return res.json()
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    collector = EduDataCollector()
    print("Testing NCS API call...")
    print(collector.fetch_ncs_courses())
    print("\nTesting Seoul Lifelong API call...")
    print(collector.fetch_seoul_lifelong_courses())


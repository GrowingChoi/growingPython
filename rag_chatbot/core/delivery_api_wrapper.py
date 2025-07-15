"""
배송 추적 API 래퍼
스마트택배 API를 사용한 실제 배송 추적 기능
API 실패 시 목 데이터로 자동 폴백
"""
import json
import requests
from typing import Dict, Any, Optional
from pathlib import Path


class DeliveryAPIWrapper:
    """배송 추적 API 래퍼 클래스"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.mock_data_path = self.project_root / "data" / "raw_docs" / "mock_delivery_data.json"
        
        # 스마트택배 API 설정
        self.api_base_url = "https://info.sweettracker.co.kr"
        self.api_key = self._get_api_key()
        
        # 택배사 코드 매핑
        self.carrier_codes = {
            "CJ대한통운": "04",
            "한진택배": "05", 
            "로젠택배": "06",
            "롯데택배": "08",
            "우체국택배": "01",
            "대신택배": "22",
            "경동택배": "23",
            "일양로지스": "32",
            "합동택배": "33",
            "CU편의점택배": "46"
        }
    
    def _get_api_key(self) -> Optional[str]:
        """환경변수에서 API 키 가져오기"""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("DELIVERY_API_KEY")
    
    def _get_carrier_code(self, carrier_name: str) -> Optional[str]:
        """택배사 이름으로 코드 조회"""
        return self.carrier_codes.get(carrier_name)
    
    def track_package(self, tracking_number: str, carrier: str = None) -> Optional[Dict[str, Any]]:
        """배송 추적"""
        try:
            # 실제 API 사용 가능한 경우
            if self.api_key and carrier:
                carrier_code = self._get_carrier_code(carrier)
                if carrier_code:
                    api_result = self._call_real_api(tracking_number, carrier_code)
                    if api_result:
                        return api_result
            
            # API 실패 시 목 데이터로 폴백
            print("📦 목 데이터를 사용하여 배송 정보를 조회합니다.")
            return self._get_mock_delivery_info(tracking_number)
            
        except Exception as e:
            print(f"❌ 배송 추적 중 오류: {e}")
            return self._get_mock_delivery_info(tracking_number)
    
    def _call_real_api(self, tracking_number: str, carrier_code: str) -> Optional[Dict[str, Any]]:
        """실제 스마트택배 API 호출"""
        try:
            url = f"{self.api_base_url}/api/v1/trackingInfo"
            params = {
                "t_key": self.api_key,
                "t_code": carrier_code,
                "t_invoice": tracking_number
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("result") == "Y":
                    return self._format_api_response(data)
                else:
                    print(f"❌ API 오류: {data.get('msg', '알 수 없는 오류')}")
                    return None
            else:
                print(f"❌ HTTP 오류: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ API 호출 중 오류: {e}")
            return None
    
    def _format_api_response(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """API 응답을 표준 형식으로 변환"""
        try:
            tracking_details = api_data.get("trackingDetails", [])
            
            # 최신 상태 정보
            latest_status = tracking_details[-1] if tracking_details else {}
            
            return {
                "tracking_number": api_data.get("invoiceNo", ""),
                "carrier": api_data.get("companyName", ""),
                "status": latest_status.get("kind", "배송중"),
                "current_location": latest_status.get("where", ""),
                "last_update": latest_status.get("timeString", ""),
                "recipient": api_data.get("receiverName", ""),
                "tracking_details": [
                    {
                        "time": detail.get("timeString", ""),
                        "location": detail.get("where", ""),
                        "status": detail.get("kind", ""),
                        "description": detail.get("telno", "")
                    }
                    for detail in tracking_details
                ]
            }
        except Exception as e:
            print(f"❌ API 응답 파싱 오류: {e}")
            return None
    
    def _get_mock_delivery_info(self, tracking_number: str) -> Dict[str, Any]:
        """목 배송 정보 반환"""
        mock_data = self._load_mock_data()
        
        # 운송장번호로 목 데이터 검색
        for delivery in mock_data:
            if delivery["tracking_number"] == tracking_number:
                return delivery
        
        # 기본 목 데이터 반환
        return {
            "tracking_number": tracking_number,
            "carrier": "CJ대한통운",
            "status": "배송중",
            "current_location": "대구 허브",
            "last_update": "2024-12-01 14:30",
            "recipient": "홍길동",
            "tracking_details": [
                {
                    "time": "2024-12-01 09:00",
                    "location": "서울 물류센터",
                    "status": "집화완료",
                    "description": "상품이 집화되었습니다"
                },
                {
                    "time": "2024-12-01 12:00", 
                    "location": "대구 허브",
                    "status": "간선상차",
                    "description": "간선 운송 중입니다"
                },
                {
                    "time": "2024-12-01 14:30",
                    "location": "대구 허브",
                    "status": "배송중",
                    "description": "배송 준비 중입니다"
                }
            ]
        }
    
    def _load_mock_data(self) -> list:
        """목 데이터 로드"""
        try:
            if self.mock_data_path.exists():
                with open(self.mock_data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ 목 데이터 로드 실패: {e}")
        
        # 기본 목 데이터
        return [
            {
                "tracking_number": "123456789012",
                "carrier": "CJ대한통운",
                "status": "배송완료",
                "current_location": "배송완료",
                "last_update": "2024-12-01 16:45",
                "recipient": "홍길동",
                "tracking_details": [
                    {
                        "time": "2024-12-01 09:00",
                        "location": "서울 물류센터",
                        "status": "집화완료",
                        "description": "상품이 집화되었습니다"
                    },
                    {
                        "time": "2024-12-01 16:45",
                        "location": "서울시 강남구",
                        "status": "배송완료",
                        "description": "배송이 완료되었습니다"
                    }
                ]
            }
        ]
    
    def format_delivery_info(self, delivery_info: Dict[str, Any]) -> str:
        """배송 정보를 사용자 친화적 형식으로 포맷팅 (매우 간결 버전)"""
        if not delivery_info:
            return "배송 정보를 찾을 수 없습니다."

        # 핵심 정보만 한 줄로 제공
        status = delivery_info['status']
        location = delivery_info['current_location']

        if status == '배송완료':
            return f"✅ 배송완료되었습니다."
        elif status == '배송중':
            return f"🚚 배송중입니다. (현재 위치: {location})"
        elif status == '주문확인':
            return f"📋 주문이 확인되었습니다. 곧 배송 준비가 시작됩니다."
        else:
            return f"📦 {status} 상태입니다."
    
    def get_delivery_status_by_order(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """주문 정보로 배송 상태 조회"""
        try:
            tracking_number = order.get('tracking_number')
            carrier = order.get('carrier', '한진택배')

            if tracking_number:
                # 운송장번호가 있으면 실제 추적
                return self.track_package(tracking_number, carrier)
            else:
                # 운송장번호가 없으면 주문 상태 기반 목 데이터 생성
                order_status = order.get('status', '주문확인')
                order_id = order.get('order_id', '')

                if order_status == '배송완료':
                    status = '배송완료'
                    location = '배송완료'
                    description = '배송이 완료되었습니다'
                elif order_status == '배송중':
                    status = '배송중'
                    location = '대구 허브'
                    description = '배송 중입니다'
                elif order_status == '배송준비중':
                    status = '배송준비중'
                    location = '물류센터'
                    description = '배송 준비 중입니다'
                else:
                    status = '주문확인'
                    location = '주문처리중'
                    description = '주문이 확인되었습니다'

                return {
                    "tracking_number": tracking_number or f"주문번호: {order_id}",
                    "carrier": carrier,
                    "status": status,
                    "current_location": location,
                    "last_update": order.get('order_date', '2024-12-01'),
                    "recipient": order.get('delivery_address', '').split()[0] if order.get('delivery_address') else '고객님',
                    "tracking_details": [
                        {
                            "time": order.get('order_date', '2024-12-01'),
                            "location": location,
                            "status": status,
                            "description": description
                        }
                    ]
                }
        except Exception as e:
            print(f"❌ 주문 기반 배송 조회 실패: {e}")
            return None

    def track_package_real_api(self, tracking_number: str, carrier: str = "한진택배") -> Optional[Dict[str, Any]]:
        """실제 API를 우선 사용하는 배송 추적 (기존 track_package와 동일하지만 명시적 이름)"""
        return self.track_package(tracking_number, carrier)

    def check_delivery_availability(self, address: str) -> Dict[str, Any]:
        """배송 가능 지역 확인"""
        # 간단한 배송 가능 지역 체크
        if "제주" in address:
            return {
                "available": True,
                "note": "제주도는 추가 배송비가 발생할 수 있습니다.",
                "extra_days": 1
            }
        elif any(keyword in address for keyword in ["울릉도", "독도", "백령도"]):
            return {
                "available": False,
                "note": "해당 지역은 배송이 불가능합니다.",
                "extra_days": 0
            }
        else:
            return {
                "available": True,
                "note": "일반 배송 가능 지역입니다.",
                "extra_days": 0
            }

    def get_delivery_estimate(self, origin: str, destination: str) -> Dict[str, Any]:
        """배송 예상 시간 조회"""
        # 간단한 배송 예상 시간 계산
        estimates = {
            ("서울", "서울"): {"days": 1, "description": "당일 또는 익일 배송"},
            ("서울", "부산"): {"days": 2, "description": "1-2일 소요"},
            ("서울", "제주"): {"days": 3, "description": "2-3일 소요 (항공 운송)"},
        }

        key = (origin, destination)
        if key in estimates:
            return estimates[key]

        # 기본 예상 시간
        return {"days": 2, "description": "2-3일 소요 예상"}


# 사용 예시
if __name__ == "__main__":
    delivery_api = DeliveryAPIWrapper()
    
    # 배송 추적 테스트
    tracking_info = delivery_api.track_package("123456789012", "CJ대한통운")
    if tracking_info:
        print(delivery_api.format_delivery_info(tracking_info))
    
    # 배송 예상 시간 테스트
    estimate = delivery_api.get_delivery_estimate("서울", "부산")
    print(f"\n배송 예상 시간: {estimate['description']}")

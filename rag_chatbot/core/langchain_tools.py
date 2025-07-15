"""
LangChain Tool 래퍼 모듈
기존 컴포넌트들을 LangChain Tool 형식으로 변환
"""
import json
from typing import Dict, Any, Optional, List
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

# 기존 컴포넌트 임포트
from .rag_processor import RAGProcessor
from .db_query_engine import DatabaseQueryEngine
from .delivery_api_wrapper import DeliveryAPIWrapper
from .response_styler import ResponseStyler, ResponseTone


class RAGSearchInput(BaseModel):
    """RAG 검색 도구 입력 스키마"""
    query: str = Field(description="검색할 질문이나 키워드")


class RAGSearchTool(BaseTool):
    """RAG 기반 문서 검색 및 응답 생성 도구"""
    name: str = "rag_search"
    description: str = """FAQ, 제품 정보, 정책 등에 대한 질문에 답변합니다.
    다음과 같은 질문에 사용하세요:
    - 배송비, 반품, 교환 등 FAQ 관련 질문
    - 제품 사양, 가격, 재고 등 제품 정보 질문
    - 회사 정책, 서비스 안내 등 일반적인 질문"""
    args_schema: type = RAGSearchInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rag_processor = None

    def _get_rag_processor(self):
        """RAG 프로세서 지연 로딩"""
        if self._rag_processor is None:
            self._rag_processor = RAGProcessor()
            self._rag_processor.initialize_vector_store()
        return self._rag_processor

    def _run(self, query: str) -> str:
        """RAG 검색 실행"""
        try:
            rag = self._get_rag_processor()
            result = rag.process_query(query)
            return result['response']
        except Exception as e:
            return f"죄송합니다. 검색 중 오류가 발생했습니다: {str(e)}"


class OrderLookupInput(BaseModel):
    """주문 조회 도구 입력 스키마"""
    order_id: Optional[str] = Field(default=None, description="주문번호 (예: ORD20241201001)")
    phone: Optional[str] = Field(default=None, description="전화번호 (예: 010-1234-5678)")
    user_id: Optional[int] = Field(default=None, description="사용자 ID (현재 로그인한 사용자의 주문 내역을 조회할 때는 생략 가능)")


class OrderLookupTool(BaseTool):
    """주문 정보 조회 도구"""
    name: str = "order_lookup"
    description: str = """주문 상태, 주문 내역을 조회합니다.
    다음과 같은 질문에 사용하세요:
    - 주문 내역 조회 (내 주문, 주문 내역, 구매 내역 등)
    - 주문 상태 확인 (특정 주문번호가 있는 경우)
    - 최근 주문 내역 조회 (전화번호가 있는 경우)
    - 사용자가 명시적으로 '내 정보', '회원 정보', '프로필', '내가 누구'를 요청할 때만 사용하세요."""
    args_schema: type = OrderLookupInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._db_engine = DatabaseQueryEngine()
        self._current_user_id = None  # 현재 사용자 ID 저장용
    
    def _run(self, order_id: Optional[str] = None, phone: Optional[str] = None,
             user_id: Optional[int] = None) -> str:
        """주문 정보 조회 실행"""
        try:
            if order_id:
                # 특정 주문 조회
                order = self._db_engine.get_order_by_id(order_id)
                if order:
                    return self._db_engine.format_order_info(order)
                else:
                    return f"주문번호 {order_id}에 해당하는 주문을 찾을 수 없습니다."

            elif phone:
                # 전화번호로 최근 주문 조회
                orders = self._db_engine.get_recent_orders_by_phone(phone)
                if orders:
                    return self._db_engine.format_user_orders(orders)
                else:
                    return f"전화번호 {phone}로 등록된 주문을 찾을 수 없습니다."

            elif user_id:
                # 사용자 ID로 정보 조회
                user = self._db_engine.get_user_by_id(user_id)
                if user:
                    return self._db_engine.format_user_info(user)
                else:
                    return f"사용자 ID {user_id}에 해당하는 사용자를 찾을 수 없습니다."

            else:
                # 매개변수가 없는 경우, 현재 사용자의 주문 내역 조회
                if self._current_user_id:
                    try:
                        user_id_int = int(self._current_user_id)

                        # 사용자 기본 정보 조회 (간단하게)
                        user = self._db_engine.get_user_by_id(user_id_int)
                        if user:
                            # 주문 내역 위주로 제공
                            orders = self._db_engine.get_user_orders(user_id_int, limit=5)
                            if orders:
                                result = f"📦 **{user['username']}님의 주문 내역**\n\n"
                                for i, order in enumerate(orders, 1):
                                    result += f"{i}. {order['order_id']} - {order['status']} ({order['order_date']})\n"
                                    if order.get('items'):
                                        item_names = [item['product_name'] for item in order['items'][:2]]
                                        if len(order['items']) > 2:
                                            item_names.append(f"외 {len(order['items'])-2}개")
                                        result += f"   상품: {', '.join(item_names)}\n"
                                    result += f"   금액: {order['total_amount']:,}원\n\n"
                                return result
                            else:
                                return f"📦 **{user['username']}님의 주문 내역**\n\n아직 주문이 없습니다."
                        else:
                            return "사용자 정보를 찾을 수 없습니다."
                    except (ValueError, TypeError):
                        pass

                return "주문 조회를 위해서는 주문번호나 전화번호가 필요합니다. 또는 로그인 후 이용해주세요."

        except Exception as e:
            return f"주문 조회 중 오류가 발생했습니다: {str(e)}"

    def set_current_user_id(self, user_id: str):
        """현재 사용자 ID 설정"""
        self._current_user_id = user_id


class DeliveryTrackingInput(BaseModel):
    """배송 추적 도구 입력 스키마"""
    tracking_number: Optional[str] = Field(default=None, description="운송장번호")
    order_id: Optional[str] = Field(default=None, description="주문번호")
    carrier: Optional[str] = Field(default=None, description="택배사명 (예: CJ대한통운)")
    product_name: Optional[str] = Field(default=None, description="상품명 (예: 옷, 니트, 스웨터 등 - 현재 사용자의 주문에서 해당 상품을 찾아 배송 추적)")


class DeliveryTrackingTool(BaseTool):
    """배송 추적 도구"""
    name: str = "delivery_tracking"
    description: str = """배송 상태를 추적하고 배송 정보를 제공합니다.
    다음과 같은 질문에 사용하세요:
    - 운송장번호로 배송 추적
    - 주문번호로 배송 상태 확인
    - "내 [상품명] 어디까지왔어?" 같은 상품별 배송 추적
    - 배송 예상 시간 문의"""
    args_schema: type = DeliveryTrackingInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._delivery_api = DeliveryAPIWrapper()
        self._db_engine = DatabaseQueryEngine()
        self._current_user_id = None  # 현재 사용자 ID 저장용
    
    def _run(self, tracking_number: Optional[str] = None, order_id: Optional[str] = None,
             carrier: Optional[str] = None, product_name: Optional[str] = None) -> str:
        """배송 추적 실행"""
        try:
            if tracking_number:
                # 운송장번호로 직접 추적 (실제 API 사용, 제한시 자동 폴백)
                delivery_info = self._delivery_api.track_package_real_api(tracking_number, carrier or "한진택배")
                if delivery_info:
                    return self._delivery_api.format_delivery_info(delivery_info)
                else:
                    return f"운송장번호 {tracking_number}에 대한 배송 정보를 찾을 수 없습니다."

            elif order_id:
                # 주문번호로 배송 정보 조회
                order = self._db_engine.get_order_by_id(order_id)
                if order:
                    delivery_info = self._delivery_api.get_delivery_status_by_order(order)
                    if delivery_info:
                        return self._delivery_api.format_delivery_info(delivery_info)
                    else:
                        return f"주문번호 {order_id}의 배송 정보를 조회할 수 없습니다."
                else:
                    return f"주문번호 {order_id}에 해당하는 주문을 찾을 수 없습니다."

            elif product_name and self._current_user_id:
                # 상품명으로 현재 사용자의 주문에서 해당 상품 찾기
                try:
                    user_id_int = int(self._current_user_id)
                    orders = self._db_engine.get_user_orders(user_id_int)

                    # 상품명이 포함된 주문 찾기
                    matching_order = None
                    for order in orders:
                        for item in order.get('items', []):
                            if product_name.lower() in item['product_name'].lower():
                                matching_order = order
                                break
                        if matching_order:
                            break

                    if matching_order:
                        # 해당 주문의 배송 정보 조회
                        delivery_info = self._delivery_api.get_delivery_status_by_order(matching_order)
                        if delivery_info:
                            return f"'{product_name}' 상품의 배송 현황입니다.\n\n" + self._delivery_api.format_delivery_info(delivery_info)
                        else:
                            return f"'{product_name}' 상품의 배송 정보를 조회할 수 없습니다."
                    else:
                        return f"'{product_name}' 상품을 포함한 주문을 찾을 수 없습니다."

                except (ValueError, TypeError):
                    return "사용자 정보를 확인할 수 없습니다."

            else:
                return "배송 추적을 위해서는 운송장번호, 주문번호, 또는 상품명이 필요합니다."

        except Exception as e:
            return f"배송 추적 중 오류가 발생했습니다: {str(e)}"

    def set_current_user_id(self, user_id: str):
        """현재 사용자 ID 설정"""
        self._current_user_id = user_id


class ProductSearchInput(BaseModel):
    """상품 검색 도구 입력 스키마"""
    keyword: str = Field(description="검색할 상품명이나 키워드")
    limit: int = Field(default=5, description="검색 결과 개수 (기본값: 5)")


class ProductSearchTool(BaseTool):
    """상품 검색 도구"""
    name: str = "product_search"
    description: str = """상품을 검색하고 상품 정보를 제공합니다.
    다음과 같은 질문에 사용하세요:
    - 특정 상품 검색
    - 상품 가격, 재고 확인
    - 상품 사양 문의"""
    args_schema: type = ProductSearchInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._db_engine = DatabaseQueryEngine()

    def _run(self, keyword: str, limit: int = 5) -> str:
        """상품 검색 실행"""
        try:
            products = self._db_engine.search_products(keyword, limit)
            if products:
                return self._db_engine.format_product_list(products)
            else:
                return f"'{keyword}'와 관련된 상품을 찾을 수 없습니다."
        except Exception as e:
            return f"상품 검색 중 오류가 발생했습니다: {str(e)}"


class GeneralResponseInput(BaseModel):
    """일반 응답 도구 입력 스키마"""
    message: str = Field(description="응답할 메시지")
    tone: str = Field(default="friendly", description="응답 톤 (friendly, helpful, informative, formal, apologetic)")


class GeneralResponseTool(BaseTool):
    """일반적인 응답 생성 도구"""
    name: str = "general_response"
    description: str = """일반적인 인사, 자기소개, 간단한 대화에 대한 응답을 생성합니다.
    다음과 같은 상황에 사용하세요:
    - 인사말 (안녕하세요, 감사합니다 등)
    - 자기소개 요청 (이름이 뭐야, 누구야, 뭐할 수 있어 등)
    - 기능 설명 요청 (어떤 도움을 줄 수 있어, 사용법 등)
    - 간단한 대화 및 일반적인 질문
    - 기타 특정 도구가 필요하지 않은 응답"""
    args_schema: type = GeneralResponseInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._response_styler = ResponseStyler()
    
    def _run(self, message: str, tone: str = "friendly") -> str:
        """일반 응답 생성"""
        try:
            # 톤 매핑
            tone_mapping = {
                "friendly": ResponseTone.FRIENDLY,
                "helpful": ResponseTone.HELPFUL,
                "informative": ResponseTone.INFORMATIVE,
                "formal": ResponseTone.FORMAL,
                "apologetic": ResponseTone.APOLOGETIC
            }
            
            response_tone = tone_mapping.get(tone, ResponseTone.FRIENDLY)
            
            # 기본 응답 생성
            if "안녕" in message or "hello" in message.lower():
                base_response = "안녕하세요! 쇼핑몰 고객센터 AI 어시스턴트입니다. 무엇을 도와드릴까요?"
            elif "감사" in message or "thank" in message.lower():
                base_response = "천만에요! 더 궁금한 것이 있으시면 언제든 말씀해주세요."
            elif "잘가" in message or "bye" in message.lower():
                base_response = "감사합니다. 좋은 하루 되세요!"
            elif any(keyword in message.lower() for keyword in ["이름", "누구", "뭐야", "name", "who"]):
                base_response = "안녕하세요! 저는 쇼핑몰 고객센터 AI 어시스턴트입니다. 주문, 배송, 상품 문의 등 다양한 도움을 드릴 수 있어요!"
            elif any(keyword in message.lower() for keyword in ["뭐할수있어", "뭐 할 수 있어", "할수있", "뭐할", "기능", "도움", "what can you do", "can you"]):
                base_response = "저는 쇼핑몰 고객센터 AI 어시스턴트로서 다음과 같은 도움을 드릴 수 있습니다:\n• 상품 검색 및 정보 제공\n• 주문 상태 확인\n• 배송 추적\n• FAQ 및 정책 안내\n• 일반적인 쇼핑몰 문의 응답\n\n무엇을 도와드릴까요?"
            elif any(keyword in message.lower() for keyword in ["어떻게", "사용법", "how to"]):
                base_response = "궁금한 것이 있으시면 자연스럽게 말씀해주세요! 예를 들어:\n• '무선 이어폰 찾고 있어요'\n• '주문번호 ORD123 상태 확인해주세요'\n• '배송비는 얼마인가요?'\n• '운송장번호 123456 추적해주세요'\n\n편하게 질문해주시면 됩니다!"
            else:
                base_response = "네, 무엇을 도와드릴까요? 주문, 배송, 상품 문의 등 언제든 말씀해주세요."
            
            # 스타일링 적용
            return self._response_styler.style_response(base_response, response_tone, include_greeting=False)
            
        except Exception as e:
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"


def get_all_tools(current_user_id: Optional[str] = None) -> List[BaseTool]:
    """모든 도구 인스턴스 반환"""
    order_tool = OrderLookupTool()
    delivery_tool = DeliveryTrackingTool()

    if current_user_id:
        order_tool.set_current_user_id(current_user_id)
        delivery_tool.set_current_user_id(current_user_id)

    return [
        RAGSearchTool(),
        order_tool,
        delivery_tool,
        ProductSearchTool(),
        GeneralResponseTool()
    ]


def get_tool_descriptions() -> Dict[str, str]:
    """도구별 설명 반환"""
    tools = get_all_tools()
    return {tool.name: tool.description for tool in tools}


if __name__ == "__main__":
    # 도구 테스트
    tools = get_all_tools()
    
    print("🔧 사용 가능한 도구들:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # 간단한 테스트
    print("\n🧪 도구 테스트:")
    
    # RAG 검색 테스트
    rag_tool = RAGSearchTool()
    result = rag_tool._run("배송비는 얼마인가요?")
    print(f"RAG 검색 결과: {result[:100]}...")
    
    # 일반 응답 테스트
    general_tool = GeneralResponseTool()
    result = general_tool._run("안녕하세요")
    print(f"일반 응답 결과: {result}")



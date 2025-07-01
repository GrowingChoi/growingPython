"""
시스템 통합 테스트 스크립트
전체 RAG 시스템과 Tool Calling Agent 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_rag_processor():
    """RAG 프로세서 테스트"""
    print("📚 RAG 프로세서 테스트")
    print("-" * 50)
    
    try:
        from core.rag_processor import RAGProcessor
        
        rag = RAGProcessor()
        rag.initialize_vector_store()
        
        test_queries = [
            "배송비는 얼마인가요?",
            "무선 이어폰 배터리는 얼마나 지속되나요?",
            "반품 절차를 알려주세요"
        ]
        
        for query in test_queries:
            result = rag.process_query(query)
            print(f"질문: {query}")
            print(f"답변: {result['response'][:150]}...")
            print(f"신뢰도: {result['confidence']:.2f}")
            print(f"응답 시간: {result['response_time']:.2f}초")
            print()
            
    except Exception as e:
        print(f"❌ RAG 프로세서 테스트 실패: {e}")

def test_db_query_engine():
    """DB 쿼리 엔진 테스트"""
    print("🗄️ DB 쿼리 엔진 테스트")
    print("-" * 50)
    
    try:
        from core.db_query_engine import DatabaseQueryEngine
        
        db_engine = DatabaseQueryEngine()
        
        # 주문 조회 테스트
        order = db_engine.get_order_by_id("ORD20241201001")
        if order:
            print("주문 조회 성공:")
            print(db_engine.format_order_info(order)[:200] + "...")
        else:
            print("❌ 주문 조회 실패 - 데이터베이스를 초기화해주세요")
        
        print()
        
        # 사용자 주문 목록 테스트
        orders = db_engine.get_recent_orders_by_phone("010-1234-5678")
        if orders:
            print("사용자 주문 목록 조회 성공:")
            print(db_engine.format_user_orders(orders)[:200] + "...")
        else:
            print("❌ 사용자 주문 목록 조회 실패")
            
    except Exception as e:
        print(f"❌ DB 쿼리 엔진 테스트 실패: {e}")

def test_delivery_api():
    """배송 API 테스트"""
    print("🚚 배송 API 테스트")
    print("-" * 50)
    
    try:
        from core.delivery_api_wrapper import DeliveryAPIWrapper
        
        delivery_api = DeliveryAPIWrapper()
        
        # 배송 추적 테스트
        tracking_info = delivery_api.track_package("123456789012")
        if tracking_info:
            print("배송 추적 성공:")
            print(delivery_api.format_delivery_info(tracking_info)[:200] + "...")
        else:
            print("❌ 배송 추적 실패")
        
        print()
        
        # 배송 예상 시간 테스트
        estimate = delivery_api.get_delivery_estimate("서울", "부산")
        print(f"배송 예상 시간: {estimate['description']}")
        
    except Exception as e:
        print(f"❌ 배송 API 테스트 실패: {e}")

def test_tool_calling_agent():
    """Tool Calling Agent 테스트"""
    print("🤖 Tool Calling Agent 테스트")
    print("-" * 50)
    
    try:
        from core.agent_processor import ToolCallingAgentProcessor
        
        agent = ToolCallingAgentProcessor()
        
        test_queries = [
            "배송비는 얼마인가요?",
            "주문번호 ORD20241201001 상태 확인해주세요",
            "운송장번호 123456789012 배송 현황 알려주세요",
            "내 이름과 주문 상태를 알려주세요"  # 복합 질문
        ]
        
        for query in test_queries:
            print(f"\n질문: {query}")
            result = agent.process_query(query, user_id=1, session_id="test_session")
            print(f"답변: {result['response'][:200]}...")
            print(f"방법: {result.get('method', 'unknown')}")
            if result.get('tools_used'):
                print(f"사용된 도구: {', '.join(result['tools_used'])}")
            print()
            
    except Exception as e:
        print(f"❌ Tool Calling Agent 테스트 실패: {e}")

def test_langchain_tools():
    """LangChain Tools 테스트"""
    print("🔧 LangChain Tools 테스트")
    print("-" * 50)
    
    try:
        from core.langchain_tools import (
            RAGSearchTool, OrderLookupTool, DeliveryTrackingTool,
            ProductSearchTool, GeneralResponseTool
        )
        
        # RAG 검색 도구 테스트
        rag_tool = RAGSearchTool()
        result = rag_tool._run("배송비는 얼마인가요?")
        print(f"RAG 검색 결과: {result[:100]}...")
        
        # 주문 조회 도구 테스트
        order_tool = OrderLookupTool()
        result = order_tool._run("ORD20241201001")
        print(f"주문 조회 결과: {result[:100]}...")
        
        # 배송 추적 도구 테스트
        delivery_tool = DeliveryTrackingTool()
        result = delivery_tool._run("123456789012")
        print(f"배송 추적 결과: {result[:100]}...")
        
        print("✅ 모든 도구 테스트 완료")
        
    except Exception as e:
        print(f"❌ LangChain Tools 테스트 실패: {e}")

def main():
    """메인 테스트 함수"""
    print("🧪 시스템 통합 테스트")
    print("=" * 60)
    
    try:
        test_rag_processor()
        test_db_query_engine()
        test_delivery_api()
        test_langchain_tools()
        test_tool_calling_agent()
        
        print("✅ 모든 테스트 완료!")
        return 0
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

"""
Tool Calling Agent 프로세서
LangChain의 create_tool_calling_agent를 사용한 에이전트 구현
"""
import time
from typing import Dict, Any, List, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from core.response_styler import ResponseStyler
from openai import OpenAI
from dotenv import load_dotenv

from .langchain_tools import get_all_tools

load_dotenv()


class ToolCallingAgentProcessor:
    """Tool Calling Agent 기반 쿼리 프로세서"""

    def __init__(self, model_name: str = "gpt-4.1", temperature: float = 0.1):
        self.response_styler = ResponseStyler()
        """
        Args:
            model_name: 사용할 LLM 모델명 (기본: gpt-4o-mini - 비용 효율적)
            temperature: 모델 온도 설정
        """
        self.model_name = model_name
        self.temperature = temperature

        # LLM 초기화 (비용 절약을 위해 GPT-4o-mini 사용)
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        
        # 도구들 로드 (초기에는 사용자 컨텍스트 없이)
        self.tools = get_all_tools()
        self.current_user_id = None

        # 에이전트 초기화
        self.agent = None
        self.agent_executor = None
        self._initialize_agent()
        
        # 대화 기록
        self.chat_history = []

        # Batch 처리용 별도 LLM (더 빠른 응답을 위해)
        self.batch_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1
        )
    
    def _initialize_agent(self):
        """에이전트 초기화"""
        # 시스템 프롬프트 생성
        system_prompt = self._create_system_prompt()
        
        # 프롬프트 템플릿 생성
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 에이전트 생성
        self.agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
        # 에이전트 실행기 생성
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
    
    def _create_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        return """당신은 친절하고 전문적인 쇼핑몰 고객센터 AI 어시스턴트입니다.

자기소개:
- 이름: 쇼핑몰 고객센터 AI 어시스턴트
- 역할: 온라인 쇼핑몰의 고객 서비스 담당
- 성격: 친절하고 도움이 되며, 정확한 정보 제공에 집중

주요 역할:
- 고객의 질문에 정확하고 친절하게 답변
- 적절한 도구를 선택하여 정보 검색 및 처리
- 고객 만족을 위한 최상의 서비스 제공
- 자연스러운 대화를 통한 문제 해결

사용 가능한 도구들:
1. rag_search: FAQ, 제품 정보, 정책 등에 대한 질문 답변
2. order_lookup: 주문 상태, 주문 내역, 사용자 정보 조회
3. delivery_tracking: 배송 추적 및 배송 정보 제공
4. product_search: 사용자의 상품 검색 및 상품 정보 제공
5. general_response: 일반적인 인사, 자기소개, 간단한 대화 응답

도구 선택 가이드라인:
- 자기소개, 이름, 기능 문의 → general_response
- 인사, 감사 인사, 일반 대화 → general_response
- 배송비, 반품, 교환 등 FAQ 관련 질문 -> rag_search
- "셔츠 추천", "유사한 하의", "더 저렴한 제품" 등 특정 제품 관련 문의 → rag_search
- 제품 사양, 특징 등 제품 정보 → rag_search 이후 product_search
- 주문 내역, 내 주문, 구매 내역, 주문 상태 → order_lookup
- 사용자 정보, "내가 누구", "내 정보", "회원 정보", "프로필" → order_lookup
- 배송 추적, 배송 상태, "내 [상품명] 어디까지왔어?" → delivery_tracking
- 사용자가 주문한 상품, 가격 확인 → product_search


응답 가이드라인:
1. 항상 친근하고 정중한 어조 사용
2. 구체적이고 실용적인 정보 제공
3. 정보가 부족한 경우 추가 정보 요청
4. 도구 사용 결과를 바탕으로 종합적인 답변 제공
5. 필요시 고객센터 연락처(1588-1234) 안내
6. 자연스러운 대화 흐름 유지

특별 지침:
- 고객이 이름이나 정체성을 물어보면 general_response 도구 사용
- "주문내역", "내 주문", "구매내역" 등의 요청은 order_lookup 도구 사용
- 주문번호, 운송장번호 등이 언급되면 해당 도구를 우선 사용
- 로그인한 사용자의 주문 내역 조회 시 order_lookup 도구가 자동으로 현재 사용자 정보 활용
- 여러 도구가 필요한 경우 순차적으로 사용
- 도구 사용 실패 시 다른 도구로 대체 시도
- 항상 고객의 입장에서 생각하여 응답
- 단순한 인사나 질문도 general_response 도구를 통해 처리"""
    
    def add_to_chat_history(self, human_message: str, ai_message: str):
        """대화 기록에 추가"""
        self.chat_history.append(HumanMessage(content=human_message))
        self.chat_history.append(AIMessage(content=ai_message))
        
        # 대화 기록이 너무 길어지면 오래된 것부터 제거 (최근 10개 대화만 유지)
        if len(self.chat_history) > 20:
            self.chat_history = self.chat_history[-20:]
    
    def clear_chat_history(self):
        """대화 기록 초기화"""
        self.chat_history = []
    
    def process_query(self, query: str, user_id: Optional[str] = None, 
                     session_id: Optional[str] = None) -> Dict[str, Any]:
        # 인사 감지
        if self._is_greeting(query):
            return {
                "response": "안녕하세요! 무엇을 도와드릴까요? 😊",
                "method": "greeting",
                "response_time": 0.1,
                "tools_used": ["general_response"],
                "success": True
            }

        # 의미 없는 질문 감지
        if not self._is_informative_query(query):
            return {
                "response": "앗, 아직 질문을 못 알아들었어요 😅 다시 한번 말씀해 주세요!",
                "method": "general",
                "response_time": 0.1,
                "tools_used": [],
                "success": True
            }
        """
        쿼리 처리 메인 함수
        
        Args:
            query: 사용자 질문
            user_id: 사용자 ID (선택사항)
            session_id: 세션 ID (선택사항)
            
        Returns:
            처리 결과 딕셔너리
        """
        start_time = time.time()

        try:
            # 사용자 컨텍스트가 변경된 경우 도구들 업데이트
            if user_id != self.current_user_id:
                self.current_user_id = user_id
                self.tools = get_all_tools(user_id)
                # 에이전트 재초기화
                self._initialize_agent()

            # 사용자 컨텍스트가 있는 경우 쿼리에 추가
            enhanced_query = query
            if user_id:
                enhanced_query = f"[현재 로그인한 사용자 ID: {user_id}] {query}"

            # 에이전트 실행
            result = self.agent_executor.invoke({
                "input": enhanced_query,
                "chat_history": self.chat_history
            })
            
            response = result.get("output", "죄송합니다. 응답을 생성할 수 없습니다.")
            
            # 대화 기록에 추가
            self.add_to_chat_history(query, response)
            
            # 응답 시간 계산
            response_time = time.time() - start_time
            
            return {
                "response": response,
                "method": "tool_calling_agent",
                "response_time": response_time,
                "tools_used": self._extract_tools_used(result),
                "success": True
            }
            
        except Exception as e:
            print(f"❌ 에이전트 처리 실패: {e}")
            
            # 폴백 응답
            fallback_response = self.response_styler.handle_error_response(
                "system_error",
                "일시적인 시스템 오류가 발생했습니다."
            )
            
            response_time = time.time() - start_time
            
            return {
                "response": fallback_response,
                "method": "fallback",
                "response_time": response_time,
                "tools_used": [],
                "success": False,
                "error": str(e)
            }
    
    def _extract_tools_used(self, agent_result: Dict[str, Any]) -> List[str]:
        """에이전트 결과에서 사용된 도구 목록 추출"""
        tools_used = []

        # intermediate_steps에서 도구 사용 정보 추출
        if "intermediate_steps" in agent_result:
            for step in agent_result["intermediate_steps"]:
                # step[0]은 AgentAction 객체
                if hasattr(step[0], 'tool'):
                    tools_used.append(step[0].tool)
                elif hasattr(step[0], 'tool_input') and hasattr(step[0], 'log'):
                    # 로그에서 도구명 추출 시도
                    log = step[0].log
                    if "Invoking:" in log:
                        # "Invoking: `tool_name`" 패턴에서 도구명 추출
                        import re
                        match = re.search(r'Invoking: `([^`]+)`', log)
                        if match:
                            tools_used.append(match.group(1))

        return tools_used

    def _analyze_complex_query(self, query: str) -> Dict[str, Any]:
        """복합 질문을 분석하여 개별 작업으로 분해"""
        analysis_prompt = ChatPromptTemplate.from_template("""
다음 사용자 질문을 분석하여 개별 작업으로 분해해주세요.

사용자 질문: {query}

분석 기준:
1. 사용자 정보 조회 (이름, 정보 등)
2. 주문/구매 내역 조회
3. 배송 추적/도착 예정일
4. 상품 정보 조회
5. FAQ/정책 문의

응답 형식 (JSON):
{{
    "is_complex": true/false,
    "tasks": [
        {{
            "type": "user_info|order_lookup|delivery_tracking|product_search|rag_search",
            "description": "작업 설명",
            "priority": 1-5
        }}
    ],
    "requires_user_context": true/false
}}

복합 질문이 아니면 is_complex를 false로 설정하세요.
""")

        try:
            messages = analysis_prompt.format_messages(query=query)
            response = self.batch_llm.invoke(messages)

            # JSON 파싱 시도
            import json
            import re

            # JSON 부분만 추출
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                return {"is_complex": False, "tasks": [], "requires_user_context": False}

        except Exception as e:
            print(f"❌ 복합 질문 분석 실패: {e}")
            return {"is_complex": False, "tasks": [], "requires_user_context": False}

    def get_available_tools(self) -> List[Dict[str, str]]:
        """사용 가능한 도구 목록 반환"""
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools
        ]

    def _execute_batch_tasks(self, tasks: List[Dict[str, Any]], user_id: Optional[str] = None) -> Dict[str, Any]:
        """여러 작업을 병렬로 실행"""
        results = {}

        # 우선순위에 따라 정렬
        sorted_tasks = sorted(tasks, key=lambda x: x.get('priority', 3))

        for task in sorted_tasks:
            task_type = task['type']
            description = task['description']

            try:
                if task_type == "user_info" or task_type == "order_lookup":
                    # 사용자 정보/주문 조회
                    tool = None
                    for t in self.tools:
                        if t.name == "order_lookup":
                            tool = t
                            break

                    if tool:
                        result = tool._run()
                        results[task_type] = {
                            "success": True,
                            "data": result,
                            "description": description
                        }

                elif task_type == "delivery_tracking":
                    # 배송 추적 - 사용자의 최근 주문에서 배송 정보 조회
                    tool = None
                    for t in self.tools:
                        if t.name == "delivery_tracking":
                            tool = t
                            break

                    if tool and user_id:
                        # 사용자의 최근 주문에서 배송 중인 상품 찾기
                        from .db_query_engine import DatabaseQueryEngine
                        db_engine = DatabaseQueryEngine()
                        orders = db_engine.get_user_orders(int(user_id), limit=3)

                        delivery_info = ""
                        for order in orders:
                            if order.get('status') in ['배송중', '배송준비중']:
                                # 첫 번째 상품명으로 배송 추적
                                if order.get('items'):
                                    product_name = order['items'][0]['product_name']
                                    result = tool._run(product_name=product_name)
                                    delivery_info += f"\n{result}"

                        results[task_type] = {
                            "success": True,
                            "data": delivery_info if delivery_info else "배송 중인 상품이 없습니다.",
                            "description": description
                        }

                elif task_type == "product_search":
                    # 상품 검색 - 사용자의 구매 내역에서 상품 정보
                    if user_id:
                        from .db_query_engine import DatabaseQueryEngine
                        db_engine = DatabaseQueryEngine()
                        orders = db_engine.get_user_orders(int(user_id), limit=5)

                        product_info = "구매하신 상품들:\n"
                        for order in orders:
                            for item in order.get('items', []):
                                product_info += f"• {item['product_name']} (수량: {item['quantity']})\n"

                        results[task_type] = {
                            "success": True,
                            "data": product_info,
                            "description": description
                        }

                elif task_type == "rag_search":
                    # FAQ/정책 검색
                    tool = None
                    for t in self.tools:
                        if t.name == "rag_search":
                            tool = t
                            break

                    if tool:
                        result = tool._run(description)
                        results[task_type] = {
                            "success": True,
                            "data": result,
                            "description": description
                        }

            except Exception as e:
                results[task_type] = {
                    "success": False,
                    "error": str(e),
                    "description": description
                }

        return results

    def get_chat_history_summary(self) -> str:
        """대화 기록 요약 반환"""
        if not self.chat_history:
            return "대화 기록이 없습니다."
        
        summary = f"총 {len(self.chat_history) // 2}개의 대화가 있습니다.\n"
        
        # 최근 3개 대화만 표시
        recent_messages = self.chat_history[-6:] if len(self.chat_history) >= 6 else self.chat_history
        
        for i in range(0, len(recent_messages), 2):
            if i + 1 < len(recent_messages):
                human_msg = recent_messages[i].content
                ai_msg = recent_messages[i + 1].content
                summary += f"\n사용자: {human_msg[:50]}{'...' if len(human_msg) > 50 else ''}"
                summary += f"\nAI: {ai_msg[:50]}{'...' if len(ai_msg) > 50 else ''}\n"
        
        return summary

    def _combine_batch_results(self, query: str, results: Dict[str, Any]) -> str:
        """배치 처리 결과를 종합하여 최종 응답 생성"""
        combine_prompt = ChatPromptTemplate.from_template("""
사용자의 질문에 대해 여러 시스템에서 조회한 결과를 종합하여 자연스럽고 완전한 답변을 생성해주세요.

사용자 질문: {query}

조회 결과:
{results}

답변 가이드라인:
1. 사용자가 요청한 모든 정보를 포함하세요
2. 자연스럽고 친근한 톤으로 작성하세요
3. 정보를 논리적 순서로 정리하세요
4. 필요시 추가 안내사항을 포함하세요

답변:
""")

        try:
            # 결과를 텍스트로 포맷팅
            results_text = ""
            for task_type, result in results.items():
                if result['success']:
                    results_text += f"\n[{result['description']}]\n{result['data']}\n"
                else:
                    results_text += f"\n[{result['description']}]\n오류: {result['error']}\n"

            messages = combine_prompt.format_messages(
                query=query,
                results=results_text
            )

            response = self.batch_llm.invoke(messages)
            return response.content.strip()

        except Exception as e:
            print(f"❌ 배치 결과 종합 실패: {e}")
            return "죄송합니다. 정보를 종합하는 중 오류가 발생했습니다."

    def process_batch_query(self, query: str, user_id: Optional[str] = None,
                           session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        복합 질문을 batch 처리로 효율적으로 처리

        Args:
            query: 사용자 질문
            user_id: 사용자 ID (선택사항)
            session_id: 세션 ID (선택사항)

        Returns:
            처리 결과 딕셔너리
        """
        start_time = time.time()

        try:
            # 1. 복합 질문 분석
            analysis = self._analyze_complex_query(query)

            if not analysis.get('is_complex', False):
                # 복합 질문이 아니면 일반 처리
                return self.process_query(query, user_id, session_id)

            # 2. 사용자 컨텍스트 업데이트
            if user_id != self.current_user_id:
                self.current_user_id = user_id
                self.tools = get_all_tools(user_id)
                self._initialize_agent()

            # 3. 배치 작업 실행
            tasks = analysis.get('tasks', [])
            batch_results = self._execute_batch_tasks(tasks, user_id)

            # 4. 결과 종합
            final_response = self._combine_batch_results(query, batch_results)

            # 5. 대화 기록에 추가
            self.add_to_chat_history(query, final_response)

            response_time = time.time() - start_time

            return {
                "response": final_response,
                "method": "batch_processing",
                "response_time": response_time,
                "tasks_executed": len(tasks),
                "batch_results": batch_results,
                "success": True
            }

        except Exception as e:
            print(f"❌ 배치 처리 실패: {e}")

            # 폴백으로 일반 처리 시도
            return self.process_query(query, user_id, session_id)

    def add_to_chat_history(self, user_message: str, bot_response: str):
        """대화 기록에 추가"""
        self.chat_history.append(HumanMessage(content=user_message))
        self.chat_history.append(AIMessage(content=bot_response))

        # 대화 기록이 너무 길어지면 오래된 것부터 제거 (최근 10개 대화만 유지)
        if len(self.chat_history) > 20:
            self.chat_history = self.chat_history[-20:]
    def _is_informative_query(self, text: str) -> bool:
        prompt = f"""
        아래 문장이 의미 있는 질문(정보 요청, 명령, 질문, 자기소개 요청, 개인정보 문의 등)인지 판단해줘.
        단순 인사, 감탄, 감정 표현만 NO로 답해.

        입력: "{text}"
        의미 있는 질문입니까? (YES 또는 NO)

        """
        try:
            response = self.batch_llm.invoke([HumanMessage(content=prompt)])
            answer = response.content.strip().upper()
            return answer.startswith("YES")
        except Exception as e:
            print(f"❌ 의미 필터링 실패: {e}")
            return True  # 예외 발생 시에는 의미 있다고 간주
    def _is_greeting(self, text: str) -> bool:
        prompt = f"""
        다음 문장이 '인사'(greeting)인지 판단해줘. 인사는 처음 대화를 시작할 때 쓰는 표현이야.
        단순한 감탄사나 감정 표현(ㅋㅋ, 헐, ㅇㅈ 등)은 인사로 보지 마.

        문장: "{text}"
        인사입니까? (YES 또는 NO)
        """
        try:
            response = self.batch_llm.invoke([HumanMessage(content=prompt)])
            answer = response.content.strip().upper()
            return answer.startswith("YES")
        except Exception as e:
            print(f"❌ 인사 필터링 실패: {e}")
            return False

# 사용 예시
if __name__ == "__main__":
    # 에이전트 프로세서 초기화
    agent_processor = ToolCallingAgentProcessor()
    
    # 테스트 질문들
    test_queries = [
        "안녕하세요!",
        "배송비는 얼마인가요?",
        "무선 이어폰 찾고 있어요",
        "주문번호 ORD20241201001 상태 확인해주세요",
        "운송장번호 123456789012 배송 추적해주세요"
    ]
    
    print("🤖 Tool Calling Agent 테스트 시작\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 테스트 {i}: {query}")
        result = agent_processor.process_query(query)
        
        print(f"✅ 응답: {result['response'][:100]}{'...' if len(result['response']) > 100 else ''}")
        print(f"⏱️ 응답 시간: {result['response_time']:.2f}초")
        print(f"🔧 사용된 도구: {result.get('tools_used', [])}")
        print(f"✨ 성공 여부: {result['success']}")
        print("-" * 80)
    
    # 대화 기록 요약
    print("\n📝 대화 기록 요약:")
    print(agent_processor.get_chat_history_summary())

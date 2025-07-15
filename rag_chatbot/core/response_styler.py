"""
응답 스타일러 모듈
AI 응답의 톤앤매너를 조정하고 이모지를 추가하여 사용자 친화적으로 만드는 모듈
"""
import random
from enum import Enum
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


class ResponseTone(Enum):
    """응답 톤 종류"""
    FRIENDLY = "friendly"          # 친근한
    PROFESSIONAL = "professional"  # 전문적인
    INFORMATIVE = "informative"    # 정보 제공형
    APOLOGETIC = "apologetic"      # 사과하는
    ENTHUSIASTIC = "enthusiastic"  # 열정적인
    HELPFUL = "helpful"
    FORMAL = "formal"  


class ResponseStyler:
    """응답 스타일링 클래스"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        
        # 톤별 이모지 매핑
        self.tone_emojis = {
            ResponseTone.FRIENDLY: ["😊", "🙂", "😄", "🤗", "💝"],
            ResponseTone.PROFESSIONAL: ["📋", "💼", "📊", "✅", "📝"],
            ResponseTone.INFORMATIVE: ["ℹ️", "📚", "💡", "🔍", "📖"],
            ResponseTone.APOLOGETIC: ["😔", "🙏", "💔", "😞", "🤲"],
            ResponseTone.ENTHUSIASTIC: ["🎉", "🚀", "⭐", "🔥", "💪"],
            ResponseTone.HELPFUL: ["🤝", "💪", "👍", "✨", "🌟"],
            ResponseTone.FORMAL: ["📋", "💼", "📊", "✅", "📝"]
        }
        
        # 인사말 패턴
        self.greetings = [
            "안녕하세요!",
            "반갑습니다!",
            "안녕하세요! 😊",
            "좋은 하루입니다!",
            "환영합니다!"
        ]
        
        # 마무리 문구
        self.closings = [
            "더 궁금한 점이 있으시면 언제든지 문의해 주세요!",
            "추가로 도움이 필요하시면 말씀해 주세요!",
            "다른 질문이 있으시면 언제든 말씀해 주세요!",
            "더 도움이 필요하시면 고객센터(1588-1234)로 연락해 주세요!",
            "감사합니다! 좋은 하루 되세요!"
        ]
        
        # 스타일링 프롬프트 템플릿
        self.style_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 쇼핑몰 고객 서비스 응답 스타일러입니다.
            
주어진 응답을 다음 톤으로 다시 작성해주세요:
- {tone}: {tone_description}

스타일링 가이드라인:
1. 원본 정보는 그대로 유지
2. 지정된 톤에 맞게 문체 조정
3. 적절한 이모지 1-2개 추가
4. 자연스럽고 친근한 표현 사용
5. 너무 과하지 않게 적당히 조정

원본 응답: {original_response}"""),
            ("human", "위 응답을 {tone} 톤으로 스타일링해주세요.")
        ])
    
    def get_tone_description(self, tone: ResponseTone) -> str:
        """톤 설명 반환"""
        descriptions = {
            ResponseTone.FRIENDLY: "친근하고 따뜻한 톤",
            ResponseTone.PROFESSIONAL: "전문적이고 정중한 톤",
            ResponseTone.INFORMATIVE: "정보 전달에 집중한 명확한 톤",
            ResponseTone.APOLOGETIC: "사과하고 공감하는 톤",
            ResponseTone.ENTHUSIASTIC: "열정적이고 긍정적인 톤",
            ResponseTone.HELPFUL: "도움이 되고 지원하는 톤",
            ResponseTone.FORMAL: "격식있고 공식적인 톤"
        }
        return descriptions.get(tone, "친근한 톤")
    
    def add_emoji(self, text: str, tone: ResponseTone, count: int = 1) -> str:
        """텍스트에 톤에 맞는 이모지 추가"""
        emojis = self.tone_emojis.get(tone, ["😊"])
        selected_emojis = random.sample(emojis, min(count, len(emojis)))
        
        # 이모지를 자연스럽게 배치
        if random.choice([True, False]):
            # 앞에 추가
            return f"{' '.join(selected_emojis)} {text}"
        else:
            # 뒤에 추가
            return f"{text} {' '.join(selected_emojis)}"
    
    def add_greeting(self, text: str) -> str:
        """인사말 추가"""
        greeting = random.choice(self.greetings)
        return f"{greeting} {text}"
    
    def add_closing(self, text: str) -> str:
        """마무리 문구 추가"""
        closing = random.choice(self.closings)
        return f"{text}\n\n{closing}"
    
    def style_response(
        self, 
        response: str, 
        tone: ResponseTone = ResponseTone.FRIENDLY,
        include_greeting: bool = False,
        include_closing: bool = True,
        include_emoji: bool = True
    ) -> str:
        """응답 스타일링"""
        try:
            # LLM을 사용한 톤 조정
            styled_response = self.llm.invoke(
                self.style_prompt.format_messages(
                    tone=tone.value,
                    tone_description=self.get_tone_description(tone),
                    original_response=response
                )
            ).content
            
            # 인사말 추가
            if include_greeting:
                styled_response = self.add_greeting(styled_response)
            
            # 마무리 문구 추가
            if include_closing:
                styled_response = self.add_closing(styled_response)
            
            # 이모지 추가 (LLM이 이미 추가했을 수 있으므로 조건부)
            if include_emoji and not any(emoji in styled_response for emoji_list in self.tone_emojis.values() for emoji in emoji_list):
                styled_response = self.add_emoji(styled_response, tone)
            
            return styled_response
            
        except Exception as e:
            print(f"❌ 응답 스타일링 실패: {e}")
            # 실패 시 기본 스타일링
            return self._basic_styling(response, tone, include_greeting, include_closing, include_emoji)
    
    def _basic_styling(
        self, 
        response: str, 
        tone: ResponseTone,
        include_greeting: bool,
        include_closing: bool,
        include_emoji: bool
    ) -> str:
        """기본 스타일링 (LLM 실패 시 폴백)"""
        styled = response
        
        if include_greeting:
            styled = self.add_greeting(styled)
        
        if include_closing:
            styled = self.add_closing(styled)
        
        if include_emoji:
            styled = self.add_emoji(styled, tone)
        
        return styled
    
    def detect_tone_from_content(self, content: str) -> ResponseTone:
        """내용에서 적절한 톤 자동 감지"""
        content_lower = content.lower()
        
        # 사과 관련 키워드
        if any(word in content_lower for word in ["죄송", "미안", "실패", "오류", "문제"]):
            return ResponseTone.APOLOGETIC
        
        # 정보 제공 관련 키워드
        elif any(word in content_lower for word in ["사양", "정보", "가격", "배송", "주문"]):
            return ResponseTone.INFORMATIVE
        
        # 긍정적 키워드
        elif any(word in content_lower for word in ["완료", "성공", "좋은", "훌륭", "만족"]):
            return ResponseTone.ENTHUSIASTIC
        
        # 기본은 친근한 톤
        else:
            return ResponseTone.FRIENDLY
    
    def auto_style(self, response: str, **kwargs) -> str:
        """자동 톤 감지 후 스타일링"""
        detected_tone = self.detect_tone_from_content(response)
        return self.style_response(response, tone=detected_tone, **kwargs)


# 사용 예시
if __name__ == "__main__":
    styler = ResponseStyler()
    
    # 테스트 응답들
    test_responses = [
        ("배송비는 5만원 이상 주문시 무료입니다.", ResponseTone.INFORMATIVE),
        ("주문번호 ORD20241201001의 상태는 배송중입니다.", ResponseTone.PROFESSIONAL),
        ("죄송합니다. 해당 정보를 찾을 수 없습니다.", ResponseTone.APOLOGETIC),
        ("주문이 성공적으로 완료되었습니다!", ResponseTone.ENTHUSIASTIC)
    ]
    
    for response, tone in test_responses:
        print(f"원본: {response}")
        styled = styler.style_response(response, tone, include_greeting=True)
        print(f"스타일링: {styled}")
        print("-" * 50)
    
    # 자동 톤 감지 테스트
    print("\n자동 톤 감지 테스트:")
    auto_response = "시스템에 오류가 발생했습니다."
    auto_styled = styler.auto_style(auto_response)
    print(f"원본: {auto_response}")
    print(f"자동 스타일링: {auto_styled}")

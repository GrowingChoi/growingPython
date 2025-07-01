# 📚 사용법 및 데이터 관리 가이드

## 📋 목차

1. [설치 및 설정](#-설치-및-설정)
2. [데이터 관리](#-데이터-관리)
3. [챗봇 사용법](#-챗봇-사용법)
4. [API 설정](#-api-설정)
5. [트러블슈팅](#-트러블슈팅)

---

## 🚀 설치 및 설정

### 시스템 요구사항
- Python 3.8 이상
- OpenAI API 키
- 최소 4GB RAM

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd SKN13-3rd-4Team
```

### 2. 가상환경 설정 (권장)
```bash
# conda 사용
conda create -n chatbot python=3.8
conda activate chatbot

# 또는 venv 사용
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
`.env` 파일을 프로젝트 루트에 생성:
```env
# 필수
OPENAI_API_KEY=your_openai_api_key_here

# 선택사항 (배송 추적)
DELIVERY_API_KEY=your_delivery_api_key_here
DELIVERY_API_BASE_URL=https://info.sweettracker.co.kr

# 선택사항 (모니터링)
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=ecommerce-chatbot
```

### 5. 초기 데이터 설정
```bash
# 데이터베이스 초기화
python scripts/simple_db_init.py

# 문서 임베딩
python scripts/simple_embed.py

# 시스템 테스트 (선택사항)
python scripts/test_system.py
```

### 6. 웹 애플리케이션 실행
```bash
streamlit run app/unified_chatbot.py
```

---

## 📊 데이터 관리

### FAQ 데이터 추가

#### 파일 위치
```
data/raw_docs/faq_data.json
```

#### JSON 형식
```json
[
  {
    "faq_id": "FAQ001",
    "category": "배송",
    "question": "배송비는 얼마인가요?",
    "answer": "5만원 이상 주문시 무료배송이며, 5만원 미만 주문시 배송비 3,000원이 부과됩니다.",
    "keywords": "배송비 무료배송 제주도 도서산간"
  }
]
```

#### 필수 필드
- `faq_id`: 고유 식별자 (예: FAQ001, FAQ002...)
- `category`: 카테고리 (배송, 반품/교환, 결제, 회원 등)
- `question`: 질문 내용
- `answer`: 답변 내용
- `keywords`: 검색 키워드 (공백으로 구분)

### 상품 정보 추가

#### 파일 위치
```
data/raw_docs/product_info.json
```

#### JSON 형식
```json
[
  {
    "product_id": "PROD001",
    "name": "무선 이어폰 Pro",
    "category": "오디오",
    "price": 89000,
    "description": "고품질 무선 이어폰으로 노이즈 캔슬링 기능과 긴 배터리 수명을 자랑합니다.",
    "specifications": {
      "배터리": "최대 24시간",
      "연결": "블루투스 5.0",
      "방수": "IPX4"
    },
    "features": ["노이즈 캔슬링", "터치 컨트롤", "고속 충전"],
    "stock": 50,
    "keywords": ["무선", "이어폰", "블루투스", "노이즈캔슬링"]
  }
]
```

#### 필수 필드
- `product_id`: 고유 상품 ID
- `name`: 상품명
- `category`: 카테고리
- `price`: 가격 (숫자)
- `description`: 상품 설명
- `specifications`: 사양 정보 (객체)
- `features`: 주요 기능 (배열)
- `keywords`: 검색 키워드 (배열)

#### 선택 필드
- `stock`: 재고 수량 (없으면 "재고 확인 필요"로 표시)

### 데이터 업데이트 프로세스

#### 1. JSON 파일 편집
- FAQ: `data/raw_docs/faq_data.json`
- 상품: `data/raw_docs/product_info.json`

#### 2. 벡터 임베딩 실행
```bash
python scripts/simple_embed.py
```

#### 3. 챗봇 재시작
```bash
streamlit run app/unified_chatbot.py
```

---

## 🤖 챗봇 사용법

### 실행
```bash
streamlit run app/unified_chatbot.py
```

### 주요 기능

#### 1. 사용자 선택
- 사이드바에서 테스트용 사용자 선택
- 개인화된 주문 내역 및 배송 정보 제공

#### 2. 질문 유형

**FAQ 질문**:
- "배송비는 얼마인가요?"
- "반품은 어떻게 하나요?"
- "쿠폰 사용 방법을 알려주세요"

**상품 정보 질문**:
- "무선 이어폰 추천해주세요"
- "스마트워치 가격이 얼마예요?"
- "키보드 사양을 알려주세요"

**주문 관련 질문**:
- "내 주문 내역을 보여주세요"
- "최근 주문 상태는 어떻게 되나요?"

**배송 추적 질문**:
- "내 주문 배송 현황을 알려주세요"
- "운송장번호 123456789012 추적해주세요"

**복합 질문**:
- "내 주문 상태와 배송 현황을 모두 알려주세요"
- "스마트워치 가격과 배송비를 알려주세요"

#### 3. 응답 정보
- **응답 시간**: 처리 소요 시간
- **사용된 도구**: 어떤 도구가 사용되었는지 표시
- **처리 방식**: Tool Calling Agent 또는 Batch Processing

---

## 🔧 API 설정

### OpenAI API
```env
OPENAI_API_KEY=sk-...
```
- [OpenAI 플랫폼](https://platform.openai.com/)에서 API 키 발급
- 사용량에 따른 과금 (GPT-4o-mini 사용으로 비용 최적화)

### 배송 추적 API (선택사항)
```env
DELIVERY_API_KEY=your_key
DELIVERY_API_BASE_URL=https://info.sweettracker.co.kr
```
- 스마트택배 API 사용
- API 키가 없으면 Mock 데이터로 자동 폴백

### LangSmith 모니터링 (선택사항)
```env
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=ecommerce-chatbot
```
- AI 에이전트 성능 모니터링
- 대화 기록 및 성능 분석

---

## 🛠️ 트러블슈팅

### 일반적인 문제

#### 1. 모듈 import 오류
```bash
ModuleNotFoundError: No module named 'langchain'
```
**해결**: 의존성 재설치
```bash
pip install -r requirements.txt
```

#### 2. OpenAI API 오류
```bash
openai.error.AuthenticationError
```
**해결**: API 키 확인
- `.env` 파일의 `OPENAI_API_KEY` 확인
- API 키 유효성 및 잔액 확인

#### 3. 벡터 DB 오류
```bash
chromadb.errors.InvalidCollectionException
```
**해결**: 벡터 DB 재생성
```bash
rm -rf data/vectordb_chroma
python scripts/simple_embed.py
```

#### 4. 데이터베이스 오류
```bash
sqlite3.OperationalError: no such table
```
**해결**: 데이터베이스 재초기화
```bash
python scripts/simple_db_init.py
```

#### 5. JSON 파싱 오류
```bash
json.decoder.JSONDecodeError
```
**해결**: JSON 문법 확인
- 온라인 JSON 검증 도구 사용
- 쉼표, 따옴표 등 문법 오류 수정

### 성능 최적화

#### 1. 응답 속도 개선
- 벡터 DB 인덱스 최적화
- 캐시 활용
- 배치 크기 조정

#### 2. 메모리 사용량 최적화
- 불필요한 모델 로딩 방지
- 대화 기록 제한

#### 3. 비용 최적화
- GPT-4o-mini 사용 (기본 설정)
- 토큰 사용량 모니터링
- 불필요한 API 호출 방지

### 로그 확인

#### 1. Streamlit 로그
```bash
streamlit run app/unified_chatbot.py --logger.level=debug
```

#### 2. Python 로그
- 콘솔 출력 확인
- 오류 메시지 분석

---

## 📈 고급 사용법

### 새로운 도구 추가
1. `core/langchain_tools.py`에 새 도구 클래스 추가
2. `get_all_tools()` 함수에 도구 등록
3. 에이전트 프롬프트 업데이트

### 커스텀 데이터 소스 연동
1. 새로운 래퍼 클래스 생성
2. LangChain Tool로 변환
3. 데이터 전처리 스크립트 작성

### 모니터링 및 분석
- LangSmith 대시보드 활용
- 성능 메트릭 수집
- 사용자 피드백 분석

## 🧪 시스템 테스트

### 통합 테스트 실행
전체 시스템이 정상 작동하는지 확인:
```bash
python scripts/test_system.py
```

### 테스트 항목
- **RAG 프로세서**: 문서 검색 및 응답 생성
- **데이터베이스**: 주문/사용자 정보 조회
- **배송 API**: 실제 배송 추적 기능
- **LangChain Tools**: 개별 도구 기능
- **Tool Calling Agent**: 전체 에이전트 시스템

### 테스트 결과 해석
- ✅ 성공: 해당 기능 정상 작동
- ❌ 실패: 오류 메시지 확인 후 해당 섹션 트러블슈팅 참조

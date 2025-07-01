# Scripts 폴더

이 폴더에는 프로젝트 초기화, 테스트, 유지보수를 위한 스크립트들이 포함되어 있습니다.

## 📁 파일 목록

### 🔧 초기화 스크립트

#### `simple_db_init.py`
- **용도**: 데이터베이스 초기화 및 샘플 데이터 삽입
- **기능**:
  - SQLite 데이터베이스 생성
  - 스키마 적용 (users, orders, products 테이블)
  - 샘플 데이터 삽입 (사용자, 주문, 상품 정보)
- **실행**: `python scripts/simple_db_init.py`

#### `simple_embed.py`
- **용도**: 문서 임베딩 및 벡터 데이터베이스 생성
- **기능**:
  - FAQ 및 상품 정보 문서 로드
  - OpenAI 임베딩을 사용한 벡터화
  - Chroma 벡터 데이터베이스 생성
  - RAG 시스템 테스트
- **실행**: `python scripts/simple_embed.py`

### 🧪 테스트 스크립트

#### `test_system.py`
- **용도**: 전체 시스템 통합 테스트
- **기능**:
  - RAG 프로세서 테스트
  - 데이터베이스 쿼리 엔진 테스트
  - 배송 API 래퍼 테스트
  - LangChain Tools 테스트
  - Tool Calling Agent 테스트
- **실행**: `python scripts/test_system.py`

## 🚀 사용 순서

### 1. 프로젝트 초기 설정
```bash
# 1. 데이터베이스 초기화
python scripts/simple_db_init.py

# 2. 문서 임베딩
python scripts/simple_embed.py
```

### 2. 시스템 테스트
```bash
# 전체 시스템 테스트
python scripts/test_system.py
```

### 3. 웹 애플리케이션 실행
```bash
# Streamlit 앱 실행
streamlit run app/unified_chatbot.py
```

## 📋 스크립트 상세 설명

### simple_db_init.py
```python
# 주요 기능
- create_database(): 데이터베이스 및 스키마 생성
- insert_sample_data(): 샘플 데이터 삽입
- 사용자 3명, 주문 6건, 상품 9개 데이터 생성
```

### simple_embed.py
```python
# 주요 기능
- load_documents(): JSON 파일에서 문서 로드
- create_vector_store(): Chroma 벡터 스토어 생성
- RAGProcessor 클래스를 사용한 통합 임베딩
- 테스트 쿼리 실행 및 결과 확인
```

### test_system.py
```python
# 테스트 항목
- test_rag_processor(): RAG 검색 및 응답 생성
- test_db_query_engine(): 데이터베이스 조회 기능
- test_delivery_api(): 배송 추적 API
- test_langchain_tools(): 개별 도구 테스트
- test_tool_calling_agent(): Agent 통합 테스트
```

## ⚠️ 주의사항

1. **환경변수 설정**: `.env` 파일에 필요한 API 키 설정 필요
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DELIVERY_API_KEY=your_delivery_api_key_here (선택사항)
   ```

2. **실행 순서**: 반드시 `simple_db_init.py` → `simple_embed.py` 순서로 실행

3. **의존성**: 모든 스크립트는 프로젝트 루트에서 실행해야 함

4. **오류 처리**: 각 스크립트는 오류 발생 시 상세한 로그 출력

## 🔄 업데이트 방법

### 새로운 FAQ나 상품 정보 추가 시
1. `data/raw_docs/` 폴더의 JSON 파일 수정
2. `python scripts/simple_embed.py` 재실행

### 데이터베이스 스키마 변경 시
1. `db/schema.sql` 파일 수정
2. `python scripts/simple_db_init.py` 재실행

### 새로운 테스트 추가 시
1. `scripts/test_system.py`에 테스트 함수 추가
2. `main()` 함수에서 새 테스트 호출

## 📊 성능 모니터링

각 스크립트는 실행 시간과 성공/실패 상태를 출력합니다:
- ✅ 성공: 정상 완료
- ❌ 실패: 오류 발생 및 상세 로그
- ⏱️ 시간: 각 작업별 소요 시간 표시

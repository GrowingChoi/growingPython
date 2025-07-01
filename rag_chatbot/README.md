# Tool Calling Agent 기반 쇼핑몰 챗봇 시스템

## 팀원 소개 

| 항목 | 최성장 | 박현아 | 구재회 | 전진혁 |
|----|----|----|----|----|
| 이미지 | <img src="images/키퍼.png" width="100" height="100"> | <img src="images/베써니.png" width="120" height="100"> | <img src="images/이든.png" width="100" height="100"> | <img src="images/아자젤.png" width="100" height="100"> |
| 이메일 | [GrowingChocolate](https://github.com/GrowingChoi) | <p align='center'>[hyuna](https://github.com/hyun-ah-0)</p> | <p align='center'>[jaehoi-koo](https://github.com/jaehoi-koo)</p> | <p align='center'>[rag-master](https://github.com/Jinhyeok33)</p> |

## 1.프로젝트 개요

기존 챗봇이 **의도(Intent)** 만 분류하고 정해진 응답만 제공했다면,  
이 시스템은 **LLM이 직접 판단하고, 필요한 툴을 호출하여 최적의 답변을 생성**합니다.

 **상품 추천, 배송 조회, FAQ 검색까지** –  
고객 질문 하나에 AI가 **자동 검색 + 문서 분석 + 자연어 응답**을 연결하는,  
**Tool Calling 기반의 지능형 RAG 챗봇**입니다.

## 주제 선정 배경  

국내 전자상거래 시장은 2023년 기준 약 **227조 원 규모**로, 최근 몇 년간 연평균 10% 이상의 성장률을 기록하고 있습니다.  
➡️ **출처**: [통계청, 온라인쇼핑동향(2023년 연간)](https://kostat.go.kr/board/view.do?bSeq=&aSeq=436945&page=1&rowPerPage=10&boardSeq=580&searchType=null&searchWord=null)


  <img src="https://tse4.mm.bing.net/th?id=OIP.W5qixHESoh6x8VxsG5sr4QHaJn&pid=Api" width="500"/>  

▲ 대한민국 이커머스 시장 성장 추이 (출처: ECDB)

고객의 **69%는 문제 발생 시 먼저 셀프서비스 채널(예: FAQ)을 이용**하고,  
FAQ에서 원하는 답변을 찾지 못하면 **40% 이상의 고객이 구매를 포기하거나 브랜드 충성도가 하락**하는 것으로 나타났습니다.  
➡️ **출처**: Forrester Research 2021, Zendesk CX Report 2022  
[출처 링크](https://www.zendesk.kr/blog/customer-experience-trends-2022/)


 <img src="https://tse2.mm.bing.net/th?id=OIP._M8Vrc-0JfYLUaE3MA9cYwHaEr&pid=Api" width="500"/>

▲ 셀프서비스 실패 시 이탈 가능성 (출처: Forrester, Zendesk)
---

## 2. 프로젝트 목표  
1️⃣ **고객 중심의 대화 경험 설계**  
- 사용자의 질문 흐름을 끊지 않는 응답 구조 설계  
- FAQ, 상품설명, 정책 안내 등 다양한 정보를 통합 응대  
- 사람과 대화하듯 매끄러운 인터랙션 제공

2️⃣ **RAG 기반 LLM 챗봇 구축**  

<img src="https://raw.githubusercontent.com/SKNETWORKS-FAMILY-AICAMP/SKN13-3rd-4Team/main/images/rag_llm.png" width="500"/>


---

## 3. 핵심 특징

###  지능형 Tool Calling Agent
- **자동 도구 선택**: LLM이 질문을 분석하여 적절한 도구를 자동 선택
- **단일 처리 방식**: 하나의 Agent로 모든 유형의 질문 처리
- **복합 질문 처리**: Batch 처리를 통한 다중 작업 병렬 실행

###  시스템 장점
- **비용 효율성**: GPT-4o-mini 사용으로 GPT-4 대비 60% 비용 절약
- **실시간 연동**: 실제 배송 추적 API와 연동된 정확한 정보 제공
- **고속 검색**: Chroma Vector DB를 통한 밀리초 단위 FAQ/상품 검색

## 4. 기술 스택

| 분야 | 기술 | 용도 |
|------|------|------|
| **LLM** | OpenAI GPT-4o-mini | 자연어 이해 및 응답 생성 |
| **Vector DB** | Chroma | FAQ, 상품 정보 벡터 검색 |
| **Embedding** | OpenAI text-embedding-3-large | 텍스트 벡터화 |
| **Database** | SQLite | 사용자, 주문, 상품 데이터 관리 |
| **Framework** | Streamlit, LangChain | 웹 UI 및 AI 에이전트 |
| **API** | 스마트택배 배송 추적 API | 실시간 배송 정보 |

---

## 5. 프로젝트 구조

```bash
📁 SKN13-3rd-4Team/
├── app/
│   └── unified_chatbot.py           # ✅ Streamlit 기반 챗봇 프론트엔드
├── core/
│   ├── agent_processor.py           # ✅ Tool Calling Agent (도구 선택 + 실행 중심)
│   ├── rag_processor.py             # RAG 기반 문서 응답 생성기
│   ├── db_query_engine.py           # 사용자/주문/상품 DB 쿼리
│   ├── delivery_api_wrapper.py      # 배송 추적 API 래퍼
│   └── response_styler.py           # 응답 톤/이모지 스타일러
├── langchain_tools.py              # LangChain Tool 정의 모듈 (agent가 사용할 tool 리스트)
├── db/
│   └── schema.sql                   # 데이터베이스 스키마
├── scripts/
│   ├── README.md                    # 스크립트 사용 가이드
│   ├── simple_db_init.py            # 데이터베이스 초기화
│   ├── simple_embed.py              # 문서 임베딩 (RAG 프로세서 사용)
│   └── test_system.py               # 통합 시스템 테스트
└── docs/                            # 📚 문서
```

---
## 6. 시스템 아키텍처

### 전체 구조도
<img src="https://raw.githubusercontent.com/SKNETWORKS-FAMILY-AICAMP/SKN13-3rd-4Team/main/images/system_architecture.png" width="700"/>

###  챗봇 처리 플로우  

<img src="https://raw.githubusercontent.com/SKNETWORKS-FAMILY-AICAMP/SKN13-3rd-4Team/main/images/chatbot.png" width="700"/>


※ 사용자의 질문이 실제 응답으로 이어지는 전 과정을 시각화한 흐름도입니다.

## 7. 데이터 수집 및 전처리 
### 1. 수집 대상
- **FAQ 데이터**
  - 수집후 가공하여 JSON 파일로 저장
  - 파일 위치: `data/raw_docs/faq_data.json`
- **상품 정보 데이터**
  - 수집후 가공하여 JSON 파일로 저장
  - 파일 위치: `data/raw_docs/product_info.json`
---

### 크롤링 데이터 예시 
```html
<div class="godsInfo-area">
  ...
  <h2 class="brand-name">
      <a href="/brand-link">8 seconds</a>
  </h2>
  <div class="gods-name" id="goodDtlTitle">
      코튼 경량 세미와이드 팬츠 - 아이보리
  </div>
  <div class="price-info">
      <span class="gods-price">
          <span class="cost">
              <del>49,900</del>
          </span>
      </span>
  </div>
  <div class="gods-about">
      <p class="about-desc">
          구멍으로 패턴을 연출한 사랑스러운 스카시 짜임이 돋보이는 카디건입니다.
      </p>
      ...
      <dt>소재정보</dt>
      <dd>
          겉감 : 아크릴 77%, 나일론 23%.
      </dd>
      ...
      <th>착용시기</th>
      <td>봄</td>
      <td class="on">여름</td>
      <td>가을</td>
      <td>겨울</td>
      ...
```
### 2.전처리 과정
- **JSON 파일 로드**
    ```python
    with open(faq_path, 'r', encoding='utf-8') as f:
        faq_data = json.load(f)
    ```

- 각 FAQ 문서의 내용을 아래와 같이 문자열로 만듭니다:
    ```
    질문: {질문 텍스트}
    답변: {답변 텍스트}
    키워드: {키워드 텍스트}
    ```

- 코드 예시:
    ```python
        for faq in faq_data:
            # 특징 정보 포맷팅
            feats = faq.get('features', [])
            feature_text = "\n".join(feats) if isinstance(feats, list) else str(feats)

            # 키워드 정보 포맷팅
            keywords = faq.get('keywords', [])
            keywords_text = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
            
            doc = Document(
                page_content=f"질문: {faq['question']}\n답변: {faq['answer']}\n키워드: {keywords_text}",
                metadata={
                    "source": "faq",
                    "features": feature_text,
                    "keywords": keywords_text
                }
            )
    ```
- 텍스트 정제:
    - 개행문자 제거
    - 양 끝 공백 제거
    ```python
    body = content.replace("\n", " ").strip()
    ```

### **상품 정보 전처리**
상품 정보 문서는 아래와 같이 처리됩니다:

- **JSON 파일 로드**
    ```python
    with open(product_path, 'r', encoding='utf-8') as f:
        product_data = json.load(f)
    ```

- 각 상품 정보를 하나의 문자열로 변환
    - 포함 항목:
        - 상품명
        - 카테고리
        - 키워드
        - 설명 (descriptions)
        - 사양 (specifications)
        - 특징 (features)
        - 가격

- 사양, 특징은 문자열로 이어붙임:
    ```python
    specs = product.get('specifications', {})
    specs_text = ",".join(specs) if isinstance(specs, list) else str(specs)
    features = product.get('features', [])
    features_text = ",".join(features) if isinstance(features, list) else str(features)
    ```

- 최종적으로 아래와 같이 page_content를 생성:
    ```
    상품명: 퍼프 소매 오픈워크 카디건 - 네이비,
    카테고리: 여성 의류 가디건,
    키워드: 가디건, 여성 가디건, 퍼프 소매, 오픈워크, 네이비, 8 seconds
    설명: 8 seconds 브랜드의 퍼프 소매 오픈워크 카디건 - 네이비는 세련된 퍼프 소매와 오픈워크 디테일이 돋보이는 여성용 가디건입니다. 네이비 컬러로 다양한 스타일링이 가능하며,
      S, M, L 세 가지 사이즈로 제공되어 체형에 맞게 선택할 수 있습니다. 봄, 여름 시즌에 가볍게 걸치기 좋은 아이템으로, 깔끔한 디자인과 편안한 착용감이 특징입니다.
    사양: 브랜드: 8 seconds, 색상: 네이비, 사이즈: S, M, L, 상품할인: -10,000원, 쿠폰할인: -0원, 총 할인금액: -10,000원
    특징: 퍼프 소매 디자인, 오픈워크 디테일, 깔끔한 네이비 컬러, 봄부터 여름까지 착용 가능, 여성스러운 실루엣
    가격: 정가 39,900원 / 할인가 29,900원 (25% 할인)
    ```

- 코드 예시:
    ```python
        doc = Document(
            page_content=f"""
                상품명: {product['name']}
                카테고리: {product['category']}
                키워드: {product['keywords']}
                설명: {product['description']}
                사양: {specs_text},
                특징: {features_text}
                가격: {product['price']}원""",
            metadata={
                "source": "product",
                "product_id": product.get('product_id', ''),
                "price": product.get('price', 0),
                "category": product.get('category', '기타'),
                "keywords": str(product.get('keywords', ''))
            }
        )
    ```

### ✅ Keyword 전처리

- keywords 필드는 metadata에만 들어가 있었음
- 따라서 검색 hit율이 낮았음
- 개선 방안 (제안):
    - keywords를 page_content에 포함해야 한다

### ✅ 저장 방식

- FAQ와 Product 모두 Chroma Vector Store에 저장됩니다:
  ```python
      # 벡터 스토어 생성
      self.vector_db_path.mkdir(parents=True, exist_ok=True)
      self.vectorstore = Chroma(
          embedding_function=self.embeddings,
          persist_directory=str(self.vector_db_path)
      )

      # 문서 추가
      BATCH_SIZE = 500
      for i in range(0, len(split_docs), BATCH_SIZE):
          try:
              self.vectorstore.add_documents(split_docs[i:i+BATCH_SIZE])
          except Exception as e:
              print(f"{i}번 째 Document Batch 추가 실패: {e}")
              continue
                  
      print(f"벡터 스토어 생성 완료: {self.vector_db_path}")
    ```
- `metadata`는 검색용이 아닌, 결과 출력용으로 활용됨

### ✅ 전처리 결과

- FAQ와 상품 정보를 벡터화하여 Vector DB에 저장
- 검색 효율 향상
---
## 8. 워크플로우

### 1. 단순 질문 처리 플로우
```
사용자 질문 → Agent 분석 → 도구 선택 → 실행 → 응답 생성
     ↓           ↓           ↓         ↓         ↓
"배송비는?"  → FAQ 검색   → RAG Tool → 검색 결과 → "5만원 이상 무료배송"
```

### 2. 복합 질문 처리 플로우 (Batch)
```
복합 질문 → Agent 분석 → 작업 분해 → 병렬 실행 → 결과 통합 → 응답 생성
    ↓          ↓          ↓          ↓          ↓          ↓
"내 주문과   → 2개 작업   → [주문조회] → [Task1]   → 결과 병합  → 통합 응답
배송현황"     식별        [배송추적]   [Task2]
```

### 3. 도구 선택 로직
```
질문 분석
    ├─ FAQ 키워드 감지 → RAG Search Tool
    ├─ 주문 관련 감지 → Order Lookup Tool
    ├─ 배송 관련 감지 → Delivery Tracking Tool
    ├─ 상품 관련 감지 → Product Search Tool
    └─ 일반 대화 → General Response Tool
```

### 4. 챗봇 응답 예시

<img src="https://raw.githubusercontent.com/SKNETWORKS-FAMILY-AICAMP/SKN13-3rd-4Team/main/images/chatbot_example.png" width="500"/>

#### 예시 1: FAQ 질문
```
Input: "반품은 어떻게 하나요?"
Process: Agent → RAG Tool → Vector Search → FAQ 검색
Output: "상품 수령 후 7일 이내 고객센터 연락..."
```

#### 예시 2: 주문 내역과 배송 상태 질문 (복합 질문)
```
Input: "주문한 내역과 지금 배송 상태는 어떻게 되나요?"
Process: Agent → Order Lookup Tool, Product Search Tool → SQLite 기반 RDB, 스마트택배 API → 주문내역, 배송 상태 조회 
Output: "주문한 상품은 ..., 현재 택배는... "
```
---


## 9. 시연 및 성능 지표

### 평균 응답 시간
- **단순 질문**: 2-5초
- **복합 질문 (Batch)**: 8-15초
- **벡터 검색**: 1-2초
- **DB 조회**: 0.1-0.5초
- **API 호출**: 3-8초

### 정확도
- **도구 선택**: 95% 이상 적절한 도구 선택
- **RAG 검색**: 약 80~90% 정확도
- **배송 추적**: 실제 API 연동으로 100% 정확

### 비용 효율성
- **GPT-4o-mini**: GPT-4 대비 60% 절약(RAG 활용으로 API 호출 최소화)
- **토큰 사용량**: 평균 500-1500 토큰/질문
- **API 호출**: 질문당 1-3회

## 10. 주요 장점

1. **단순성**: 하나의 Agent로 모든 질문 처리
2. **효율성**: Batch 처리로 복합 질문 최적화
3. **확장성**: 새로운 도구 쉽게 추가 가능
4. **비용 효율성**: GPT-4o-mini 사용으로 비용 절약
5. **실용성**: 실제 API 연동으로 현실적인 서비스 제공
6. **검색 품질 개선 가능성**: keywords를 page_content에 포함하여 RAG 검색 정확도를 높일 수 있음

---

## 11. 빠른 시작

### 1. 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 생성)
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. 데이터 초기화
```bash
# 데이터베이스 초기화
python scripts/simple_db_init.py

# 문서 임베딩
python scripts/simple_embed.py
```

### 3. 애플리케이션 실행
```bash
# 웹 애플리케이션 시작
streamlit run app/unified_chatbot.py
```

### 4. 접속
- **URL**: http://localhost:8501
- **기본 모드**: Tool Calling Agent
- **특별 기능**: Batch 처리 (복합 질문 자동 감지)

## 문서

- **[GUIDE.md](GUIDE.md)**: 상세한 설치, 사용법, 데이터 관리 및 트러블슈팅 가이드
- **[docs/](docs/)**: 추가 기술 문서 및 아키텍처 정보

## 개발팀
SKN13-3rd-4Team

## 한 줄 회고

| 이름 | 회고 |
|----|----|
|최성장 | 4차 프로젝트도 화이팅 >.< |
|박현아 | 좋은 팀원들 만나서 무사히 끝낼 수 있었습니다! 다들 너무 감사했고, 다음에 있을 4차 프로젝트도 잘 부탁드려요~ |
|구재회 | 딸깍 |
|전진혁 | **"RAG master"** |




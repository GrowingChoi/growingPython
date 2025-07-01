"""
문서 임베딩 스크립트
FAQ와 상품 정보를 벡터 데이터베이스에 임베딩
"""
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# 환경변수 로드
load_dotenv()

# 프로젝트 루트 경로 설정
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

data_dir = project_root / "data"
vector_db_path = data_dir / "vectordb_chroma"

def load_documents():
    """문서 로드"""
    documents = []
    
    # FAQ 문서 로드
    faq_path = data_dir / "raw_docs" / "faq_data.json"
    if faq_path.exists():
        with open(faq_path, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
            
        for faq in faq_data:
            doc = Document(
                page_content=f"질문: {faq['question']}\n답변: {faq['answer']}",
                metadata={
                    "source": "faq",
                    "category": faq['category'],
                    "faq_id": faq.get('faq_id', faq.get('id', 'unknown')),
                    "keywords": faq.get('keywords', '')
                }
            )
            documents.append(doc)
    
    # 제품 정보 문서 로드
    product_path = data_dir / "raw_docs" / "product_info.json"
    if product_path.exists():
        with open(product_path, 'r', encoding='utf-8') as f:
            product_data = json.load(f)
            
        for product in product_data:
            # 사양 정보를 문자열로 변환
            specs = product.get('specifications', {})
            specs_text = ", ".join([f"{k}: {v}" for k, v in specs.items()]) if isinstance(specs, dict) else str(specs)
            
            # 특징 정보를 문자열로 변환
            features = product.get('features', [])
            features_text = ", ".join(features) if isinstance(features, list) else str(features)
            
            doc = Document(
                page_content=f"상품명: {product['name']}\n설명: {product['description']}\n사양: {specs_text}\n특징: {features_text}\n가격: {product['price']:,}원",
                metadata={
                    "source": "product",
                    "product_id": product['product_id'],
                    "category": product['category'],
                    "price": product['price'],
                    "keywords": str(product.get('keywords', ''))
                }
            )
            documents.append(doc)
    
    return documents

def create_vector_store():
    """벡터 스토어 생성"""
    print("📄 문서 로드 중...")
    documents = load_documents()
    
    if not documents:
        print("⚠️ 로드할 문서가 없습니다.")
        return None
    
    print(f"📄 {len(documents)}개 문서 로드 완료")
    
    # 임베딩 모델 초기화
    print("🔧 임베딩 모델 초기화 중...")
    embeddings = OpenAIEmbeddings()
    
    # 벡터 스토어 생성
    print("💾 벡터 스토어 생성 중...")
    vector_db_path.mkdir(parents=True, exist_ok=True)
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(vector_db_path)
    )
    
    # 저장
    vectorstore.persist()
    print(f"✅ 벡터 스토어 생성 완료: {vector_db_path}")
    
    return vectorstore

def test_search():
    """검색 테스트"""
    print("\n🔍 검색 테스트 시작...")
    
    # 임베딩 모델 초기화
    embeddings = OpenAIEmbeddings()
    
    # 벡터 스토어 로드
    vectorstore = Chroma(
        persist_directory=str(vector_db_path),
        embedding_function=embeddings
    )
    
    # 테스트 쿼리
    test_queries = [
        "배송비는 얼마인가요?",
        "무선 이어폰 가격",
        "반품 방법"
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        results = vectorstore.similarity_search(query, k=2)
        
        for i, doc in enumerate(results, 1):
            print(f"  결과 {i}: {doc.page_content[:100]}...")
            print(f"  소스: {doc.metadata.get('source', 'unknown')}")

def main():
    """메인 실행 함수"""
    print("🚀 문서 임베딩 시작...")

    try:
        # RAG 프로세서를 사용한 임베딩
        from core.rag_processor import RAGProcessor

        rag_processor = RAGProcessor()
        rag_processor.initialize_vector_store()

        print("✅ 문서 임베딩 완료!")

        # 테스트 쿼리 실행
        test_queries = [
            "배송비는 얼마인가요?",
            "무선 이어폰 사양이 어떻게 되나요?",
            "반품은 어떻게 하나요?"
        ]

        print("\n🔍 테스트 쿼리 실행:")
        for query in test_queries:
            print(f"\n질문: {query}")
            result = rag_processor.process_query(query)
            print(f"답변: {result['response'][:100]}...")
            print(f"신뢰도: {result['confidence']:.2f}")
            print(f"소스 수: {len(result['sources'])}")

        return 0

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

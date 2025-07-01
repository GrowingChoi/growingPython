"""
RAG (Retrieval-Augmented Generation) 프로세서
벡터 DB를 사용한 문서 검색 및 응답 생성
"""
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()


class RAGProcessor:
    """RAG 기반 문서 검색 및 응답 생성 클래스"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name, temperature=0.1)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None
        
        # 프로젝트 루트 경로 설정
        self.project_root = Path(__file__).parent.parent
        self.vector_db_path = self.project_root / "data" / "vectordb_chroma"
        self.raw_docs_path = self.project_root / "data" / "raw_docs"
        
        # 텍스트 분할기 설정
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # RAG 프롬프트 템플릿 설정
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 쇼핑몰 고객 서비스 전문가입니다.
            
주요 역할:
- 고객의 질문에 대해 정확하고 친절한 답변 제공
- 제공된 문서 정보를 바탕으로 답변 생성
- 정보가 부족한 경우 정중하게 안내

답변 가이드라인:
1. 친근하고 정중한 어조 사용
2. 구체적이고 실용적인 정보 제공
3. 문서에 없는 정보는 추측하지 말고 안내
4. 필요시 추가 문의 방법 안내

검색된 문서 정보:
{context}"""),
            ("human", "{question}")
        ])
    
    def initialize_vector_store(self):
        """벡터 스토어 초기화 및 RAG Chain 구성"""
        try:
            if self.vector_db_path.exists():
                # 기존 벡터 스토어 로드
                self.vectorstore = Chroma(
                    persist_directory=str(self.vector_db_path),
                    embedding_function=self.embeddings
                )
                print(f"벡터 스토어 로드 완료: {self.vector_db_path}")
            else:
                # 새로운 벡터 스토어 생성
                print("벡터 스토어가 없습니다. 새로 생성합니다...")
                self._create_vector_store()
            
            # 리트리버 설정
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            
            # RAG Chain 구성
            self._setup_rag_chain()
            
        except Exception as e:
            print(f"벡터 스토어 초기화 실패: {e}")
            raise
    
    def _setup_rag_chain(self):
        """RAG Chain 구성"""
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # RAG Chain 구성: 검색 → 포맷팅 → 프롬프트 → LLM → 파싱
        self.rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.rag_prompt
            | self.llm
            | StrOutputParser()
        )
        print("RAG Chain 구성 완료")
    
    def _create_vector_store(self):
        """벡터 스토어 생성"""
        documents = self._load_documents()
        
        if not documents:
            raise ValueError("로드할 문서가 없습니다.")
        
        # 문서 분할
        split_docs = self.text_splitter.split_documents(documents)
        print(f"{len(split_docs)}개 문서 청크 생성")
        
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
    
    def _load_documents(self) -> List[Document]:
        """문서 로드 및 Document 객체 변환"""
        documents = []
        
        # FAQ 문서 처리
        faq_documents = self._process_faq_documents()
        documents.extend(faq_documents)
        
        # 제품 정보 문서 처리
        product_documents = self._process_product_documents()
        documents.extend(product_documents)
        
        print(f"총 {len(documents)}개 문서 로드")
        return documents
    
    def _process_faq_documents(self) -> List[Document]:
        """FAQ 문서 처리"""
        documents = []
        faq_file = self.raw_docs_path / "faq_data.json"
        
        if not faq_file.exists():
            print(f"FAQ 파일이 없습니다: {faq_file}")
            return documents
        
        try:
            with open(faq_file, 'r', encoding='utf-8') as f:
                faq_data = json.load(f)
            
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
                documents.append(doc)
            
            print(f"FAQ 문서 {len(documents)}개 처리 완료")
            
        except Exception as e:
            print(f"FAQ 문서 처리 실패: {e}")
        
        return documents
    
    def _process_product_documents(self) -> List[Document]:
        """제품 정보 문서 처리"""
        documents = []
        product_file = self.raw_docs_path / "product_info.json"
        
        if not product_file.exists():
            print(f"제품 정보 파일이 없습니다: {product_file}")
            return documents
        
        try:
            with open(product_file, 'r', encoding='utf-8') as f:
                product_data = json.load(f)
            
            for product in product_data:
                # 사양 정보 포맷팅
                specs = product.get('specifications', {})
                # specs_text = ", ".join([f"{k}: {v}" for k, v in specs.items()]) if isinstance(specs, dict) else str(specs)
                specs_text = "\n".join(specs) if isinstance(specs, list) else str(specs)
                
                # 특징 정보 포맷팅
                features = product.get('features', [])
                # features_text = ", ".join(features) if isinstance(features, list) else str(features)
                features_text = "\n".join(features) if isinstance(features, list) else str(features)
                
                doc = Document(
                    page_content=f"상품명: {product['name']}\n카테고리: {product['category']}\n키워드: {product['keywords']}\n설명: {product['description']}\n특징: {features_text}\n가격: {product['price']}원",
                    metadata={
                        "source": "product",
                        "product_id": product.get('product_id', ''),
                        "price": product.get('price', 0),
                        "category": product.get('category', '기타'),
                        "keywords": str(product.get('keywords', ''))
                    }
                )
                documents.append(doc)
            
            print(f"제품 문서 {len(documents)}개 처리 완료")
            
        except Exception as e:
            print(f"제품 문서 처리 실패: {e}")
        
        return documents
    
    def search_documents(self, query: str, k: int = 3) -> List[Document]:
        """문서 검색"""
        if not self.retriever:
            print("리트리버가 초기화되지 않았습니다.")
            return []
        
        try:
            results = self.retriever.invoke(query)
            return results[:k]
        except Exception as e:
            print(f"문서 검색 실패: {e}")
            return []
    
    def generate_response(self, query: str) -> str:
        """RAG Chain을 사용한 응답 생성"""
        if not self.rag_chain:
            return "죄송합니다. 시스템이 초기화되지 않았습니다."
        
        try:
            response = self.rag_chain.invoke(query)
            return response
        except Exception as e:
            print(f"응답 생성 실패: {e}")
            return "죄송합니다. 현재 시스템에 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """쿼리 처리 (검색 + 응답 생성)"""
        start_time = time.time()
        
        # 문서 검색
        relevant_docs = self.search_documents(query)
        
        if not relevant_docs:
            return {
                "response": "죄송합니다. 관련된 정보를 찾을 수 없습니다. 고객센터(1588-1234)로 문의해주시면 더 자세한 도움을 받으실 수 있습니다.",
                "sources": [],
                "confidence": 0.0,
                "response_time": time.time() - start_time
            }
        
        # RAG Chain을 사용한 응답 생성
        response = self.generate_response(query)
        
        # 소스 정보 추출
        sources = []
        for doc in relevant_docs:
            source_info = {
                "source": doc.metadata.get("source", "unknown"),
                "content_preview": doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            }
            if doc.metadata.get("source") == "product":
                source_info["product_id"] = doc.metadata.get("product_id")
            elif doc.metadata.get("source") == "faq":
                source_info["faq_id"] = doc.metadata.get("faq_id")
                source_info["category"] = doc.metadata.get("category")
            
            sources.append(source_info)
        
        return {
            "response": response,
            "sources": sources,
            "confidence": len(relevant_docs) / 3.0,
            "response_time": time.time() - start_time
        }


if __name__ == "__main__":
    rag = RAGProcessor()
    rag.initialize_vector_store()
    
    test_queries = [
        "배송비는 얼마인가요?",
        "무선 이어폰 사양이 어떻게 되나요?",
        "반품은 어떻게 하나요?"
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        result = rag.process_query(query)
        print(f"답변: {result['response']}")
        print(f"신뢰도: {result['confidence']:.2f}")
        print(f"소스 수: {len(result['sources'])}")
        print(f"응답 시간: {result['response_time']:.2f}초")

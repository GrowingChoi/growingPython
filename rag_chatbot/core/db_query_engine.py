"""
데이터베이스 쿼리 엔진
사용자 정보, 주문 정보 등을 데이터베이스에서 조회
"""
import sqlite3
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

class DatabaseQueryEngine:
    """데이터베이스 쿼리 처리 클래스"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            project_root = Path(__file__).parent.parent
            self.db_path = project_root / "data" / "sample_db" / "ecommerce.db"
        else:
            self.db_path = Path(db_path)
        
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """데이터베이스 파일 존재 확인"""
        if not self.db_path.exists():
            print(f"⚠️ 데이터베이스 파일이 없습니다: {self.db_path}")
            print("💡 'python db/init_db.py' 명령어로 데이터베이스를 초기화해주세요.")
    
    def _get_connection(self) -> sqlite3.Connection:
        """데이터베이스 연결 반환"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
        return conn
    
    def get_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """전화번호로 사용자 정보 조회"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM users WHERE phone = ?
                """, (phone,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            print(f"❌ 사용자 조회 실패: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """이메일로 사용자 정보 조회"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM users WHERE email = ?
                """, (email,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            print(f"❌ 사용자 조회 실패: {e}")
            return None
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """주문 ID로 주문 정보 조회"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 주문 기본 정보 조회
                cursor.execute("""
                    SELECT o.*, u.username, u.phone 
                    FROM orders o
                    JOIN users u ON o.user_id = u.user_id
                    WHERE o.order_id = ?
                """, (order_id,))
                
                order_row = cursor.fetchone()
                if not order_row:
                    return None
                
                order_info = dict(order_row)
                
                # 주문 상품 정보 조회
                cursor.execute("""
                    SELECT * FROM order_items WHERE order_id = ?
                """, (order_id,))
                
                items = [dict(row) for row in cursor.fetchall()]
                order_info['items'] = items
                
                return order_info
                
        except Exception as e:
            print(f"❌ 주문 조회 실패: {e}")
            return None
    
    def get_user_orders(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자의 주문 목록 조회"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM orders 
                    WHERE user_id = ? 
                    ORDER BY order_date DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                orders = []
                for row in cursor.fetchall():
                    order = dict(row)
                    
                    # 각 주문의 상품 정보 조회
                    cursor.execute("""
                        SELECT * FROM order_items WHERE order_id = ?
                    """, (order['order_id'],))
                    
                    order['items'] = [dict(item_row) for item_row in cursor.fetchall()]
                    orders.append(order)
                
                return orders
                
        except Exception as e:
            print(f"❌ 사용자 주문 목록 조회 실패: {e}")
            return []
    
    def get_recent_orders_by_phone(self, phone: str, limit: int = 5) -> List[Dict[str, Any]]:
        """전화번호로 최근 주문 조회"""
        try:
            user = self.get_user_by_phone(phone)
            if not user:
                return []
            
            return self.get_user_orders(user['user_id'], limit)
            
        except Exception as e:
            print(f"❌ 전화번호로 주문 조회 실패: {e}")
            return []
    
    def get_product_info(self, product_id: str) -> Optional[Dict[str, Any]]:
        """상품 정보 조회"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM products WHERE product_id = ?
                """, (product_id,))
                
                row = cursor.fetchone()
                if row:
                    product = dict(row)
                    
                    # JSON 필드 파싱
                    if product.get('specifications'):
                        try:
                            product['specifications'] = json.loads(product['specifications'])
                        except:
                            pass
                    
                    if product.get('features'):
                        try:
                            product['features'] = json.loads(product['features'])
                        except:
                            pass
                    
                    if product.get('keywords'):
                        try:
                            product['keywords'] = json.loads(product['keywords'])
                        except:
                            pass
                    
                    return product
                return None
                
        except Exception as e:
            print(f"❌ 상품 정보 조회 실패: {e}")
            return None
    
    def search_products(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """키워드로 상품 검색"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM products 
                    WHERE name LIKE ? OR description LIKE ? OR keywords LIKE ?
                    LIMIT ?
                """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))
                
                products = []
                for row in cursor.fetchall():
                    product = dict(row)
                    
                    # JSON 필드 파싱
                    if product.get('specifications'):
                        try:
                            product['specifications'] = json.loads(product['specifications'])
                        except:
                            pass
                    
                    products.append(product)
                
                return products
                
        except Exception as e:
            print(f"❌ 상품 검색 실패: {e}")
            return []
    
    def get_order_status_summary(self) -> Dict[str, int]:
        """주문 상태별 통계"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM orders 
                    GROUP BY status
                """)
                
                return {row['status']: row['count'] for row in cursor.fetchall()}
                
        except Exception as e:
            print(f"❌ 주문 상태 통계 조회 실패: {e}")
            return {}
    
    def log_chat_interaction(self, session_id: str, user_id: Optional[int], 
                           user_message: str, bot_response: str, 
                           intent: str, confidence: float, response_time_ms: int):
        """챗봇 대화 로그 저장"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chat_logs 
                    (session_id, user_id, user_message, bot_response, intent, confidence_score, response_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (session_id, user_id, user_message, bot_response, intent, confidence, response_time_ms))
                
                conn.commit()
                
        except Exception as e:
            print(f"❌ 채팅 로그 저장 실패: {e}")
    
    def format_order_info(self, order: Dict[str, Any]) -> str:
        """주문 정보를 사용자 친화적 형태로 포맷팅"""
        if not order:
            return "주문 정보를 찾을 수 없습니다."
        
        # 주문 기본 정보
        result = f"📦 **주문 정보**\n"
        result += f"• 주문번호: {order['order_id']}\n"
        result += f"• 주문일: {order['order_date']}\n"
        result += f"• 상태: {order['status']}\n"
        result += f"• 총 금액: {order['total_amount']:,}원\n"
        
        # 배송 정보
        if order.get('tracking_number'):
            result += f"• 운송장번호: {order['tracking_number']}\n"
            result += f"• 택배사: {order['delivery_company']}\n"
        
        result += f"• 배송지: {order['shipping_address']}\n"
        
        # 주문 상품 정보
        if order.get('items'):
            result += f"\n🛍️ **주문 상품**\n"
            for item in order['items']:
                result += f"• {item['product_name']} x {item['quantity']}개 - {item['price']:,}원\n"
        
        return result
    
    def format_user_orders(self, orders: List[Dict[str, Any]]) -> str:
        """사용자 주문 목록을 포맷팅"""
        if not orders:
            return "주문 내역이 없습니다."
        
        result = f"📋 **최근 주문 내역** (총 {len(orders)}건)\n\n"
        
        for i, order in enumerate(orders, 1):
            result += f"{i}. {order['order_id']} ({order['order_date']})\n"
            result += f"   상태: {order['status']} | 금액: {order['total_amount']:,}원\n"
            
            if order.get('items'):
                item_names = [item['product_name'] for item in order['items'][:2]]
                if len(order['items']) > 2:
                    item_names.append(f"외 {len(order['items'])-2}개")
                result += f"   상품: {', '.join(item_names)}\n"
            
            result += "\n"
        
        return result

    def format_product_list(self, products: List[Dict[str, Any]]) -> str:
        """상품 목록을 포맷팅"""
        if not products:
            return "검색된 상품이 없습니다."

        result = f"🛍️ **상품 검색 결과** (총 {len(products)}개)\n\n"

        for i, product in enumerate(products, 1):
            result += f"{i}. **{product['name']}**\n"
            result += f"   💰 가격: {product['price']:,}원\n"
            result += f"   📝 설명: {product['description']}\n"

            # 사양 정보
            if product.get('specifications'):
                specs = product['specifications']
                if isinstance(specs, dict):
                    spec_text = ", ".join([f"{k}: {v}" for k, v in specs.items()])
                    result += f"   🔧 사양: {spec_text}\n"
                elif isinstance(specs, str):
                    result += f"   🔧 사양: {specs}\n"

            # 특징 정보
            if product.get('features'):
                features = product['features']
                if isinstance(features, list):
                    result += f"   ✨ 특징: {', '.join(features)}\n"
                elif isinstance(features, str):
                    result += f"   ✨ 특징: {features}\n"

            # 재고 정보 (선택 필드)
            stock = product.get('stock') or product.get('stock_quantity')
            if stock is not None:
                result += f"   📦 재고: {stock}개\n"
            else:
                result += f"   📦 재고: 재고 확인 필요\n"
            result += "\n"

        return result

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """사용자 ID로 사용자 정보 조회"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM users WHERE user_id = ?
                """, (user_id,))

                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None

        except Exception as e:
            print(f"❌ 사용자 조회 실패: {e}")
            return None

    def format_user_info(self, user: Dict[str, Any]) -> str:
        """사용자 정보를 포맷팅"""
        if not user:
            return "사용자 정보를 찾을 수 없습니다."

        result = f"👤 **사용자 정보**\n"
        result += f"• 이름: {user['username']}\n"
        result += f"• 이메일: {user['email']}\n"
        result += f"• 전화번호: {user['phone']}\n"
        result += f"• 주소: {user['address']}\n"
        result += f"• 회원등급: {user['member_grade']}\n"
        result += f"• 가입일: {user['join_date']}\n"
        result += f"• 총 주문수: {user['total_orders']}건\n"
        result += f"• 총 구매금액: {user['total_amount']:,}원\n"

        return result

    def get_all_users(self) -> List[Dict[str, Any]]:
        """모든 사용자 목록 조회"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, username, email, phone, address, member_grade,
                           join_date, total_orders, total_amount
                    FROM users
                    ORDER BY username
                """)

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            print(f"❌ 사용자 목록 조회 실패: {e}")
            return []


# 사용 예시
if __name__ == "__main__":
    db_engine = DatabaseQueryEngine()

    # 테스트 쿼리들
    print("🔍 주문 조회 테스트:")
    order = db_engine.get_order_by_id("ORD20241201001")
    if order:
        print(db_engine.format_order_info(order))

    print("\n🔍 사용자 주문 목록 테스트:")
    orders = db_engine.get_recent_orders_by_phone("010-1234-5678")
    print(db_engine.format_user_orders(orders))

    print("\n🔍 상품 검색 테스트:")
    products = db_engine.search_products("이어폰")
    for product in products:
        print(f"- {product['name']} ({product['price']:,}원)")

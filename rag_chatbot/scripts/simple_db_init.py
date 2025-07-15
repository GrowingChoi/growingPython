"""
간단한 데이터베이스 초기화 스크립트 (테스트용)
"""
import sqlite3
import json
from pathlib import Path

# 프로젝트 루트 경로
project_root = Path(__file__).parent.parent
db_path = project_root / "data" / "sample_db" / "ecommerce.db"

def create_tables():
    """테이블 생성"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 사용자 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            member_grade TEXT DEFAULT 'BRONZE',
            join_date DATE,
            total_orders INTEGER DEFAULT 0,
            total_amount INTEGER DEFAULT 0
        )
    """)
    
    # 상품 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            specifications TEXT,
            features TEXT,
            price INTEGER,
            keywords TEXT
        )
    """)
    
    # 주문 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER,
            order_date DATE,
            status TEXT,
            tracking_number TEXT,
            delivery_company TEXT,
            total_amount INTEGER,
            shipping_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # 주문 상품 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            product_id TEXT,
            product_name TEXT,
            quantity INTEGER,
            price INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders (order_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ 테이블 생성 완료")

def insert_sample_data():
    """샘플 데이터 삽입"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 사용자 데이터
    users = [
        (1, "김철수", "kim@example.com", "010-1234-5678", "서울시 강남구 테헤란로 123", "VIP", "2024-01-15", 5, 450000),
        (2, "이영희", "lee@example.com", "010-2345-6789", "서울시 서초구 서초대로 456", "GOLD", "2024-02-20", 3, 280000),
        (3, "박민수", "park@example.com", "010-3456-7890", "부산시 해운대구 해운대로 789", "SILVER", "2024-03-10", 1, 45000)
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO users 
        (user_id, username, email, phone, address, member_grade, join_date, total_orders, total_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, users)
    
    # 상품 데이터
    products = [
        ("PROD001", "무선 이어폰 Pro", "오디오", "고품질 무선 이어폰", '{"배터리": "24시간", "연결": "블루투스 5.0"}', '["노이즈 캔슬링", "터치 컨트롤"]', 89000, '["무선", "이어폰", "블루투스"]'),
        ("PROD002", "스마트워치 Ultra", "웨어러블", "건강 모니터링 스마트워치", '{"디스플레이": "1.9인치", "배터리": "7일"}', '["건강 모니터링", "GPS"]', 159000, '["스마트워치", "건강", "GPS"]'),
        ("PROD003", "무선 키보드", "컴퓨터 액세서리", "저소음 무선 키보드", '{"연결": "2.4GHz", "키": "저소음"}', '["저소음", "무선"]', 45000, '["키보드", "무선", "저소음"]'),
        ("PROD004", "프리미엄 니트 스웨터", "의류", "부드럽고 따뜻한 프리미엄 울 소재의 니트 스웨터", '{"소재": "울 70%, 캐시미어 30%", "사이즈": "M (95-100cm)"}', '["프리미엄 울 소재", "캐시미어 혼방"]', 89000, '["니트", "스웨터", "울", "캐시미어", "옷", "의류"]'),
        ("PROD005", "무선 충전기", "충전기", "Qi 무선 충전기", '{"출력": "15W", "호환성": "Qi"}', '["고속충전", "안전보호"]', 25000, '["무선충전", "Qi", "고속"]')
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO products 
        (product_id, name, category, description, specifications, features, price, keywords)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, products)
    
    # 주문 데이터
    orders = [
        ("ORD20241201001", 1, "2024-12-01", "배송중", "123456789012", "CJ대한통운", 89000, "서울시 강남구 테헤란로 123"),
        ("ORD20241201002", 2, "2024-12-01", "배송완료", "123456789013", "한진택배", 159000, "서울시 서초구 서초대로 456"),
        ("ORD20241201003", 3, "2024-12-02", "주문확인", None, None, 45000, "부산시 해운대구 해운대로 789"),
        ("ORD20241226001", 1, "2024-12-24", "배송중", "535148425350", "한진택배", 89000, "서울시 강남구 테헤란로 123")
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO orders 
        (order_id, user_id, order_date, status, tracking_number, delivery_company, total_amount, shipping_address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, orders)
    
    # 주문 상품 데이터
    order_items = [
        ("ORD20241201001", "PROD001", "무선 이어폰 Pro", 1, 89000),
        ("ORD20241201002", "PROD002", "스마트워치 Ultra", 1, 159000),
        ("ORD20241201003", "PROD003", "무선 키보드", 1, 45000),
        ("ORD20241226001", "PROD004", "프리미엄 니트 스웨터", 1, 89000)
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO order_items 
        (order_id, product_id, product_name, quantity, price)
        VALUES (?, ?, ?, ?, ?)
    """, order_items)
    
    conn.commit()
    conn.close()
    print("✅ 샘플 데이터 삽입 완료")

def main():
    """메인 함수"""
    print("🚀 간단한 데이터베이스 초기화 시작...")
    
    # 디렉토리 생성
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 테이블 생성
    create_tables()
    
    # 샘플 데이터 삽입
    insert_sample_data()
    
    print(f"✅ 데이터베이스 초기화 완료: {db_path}")

if __name__ == "__main__":
    main()

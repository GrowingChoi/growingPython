"""
데이터베이스 스키마 초기화 스크립트
"""
import sqlite3
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv가 설치되지 않았습니다. 환경변수를 직접 설정해주세요.")

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "sample_db" / "ecommerce.db"

def create_database():
    """데이터베이스 생성 및 스키마 적용"""
    # 디렉토리 생성
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # 스키마 파일 읽기
    schema_path = PROJECT_ROOT / "db" / "schema.sql"
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # 데이터베이스 연결 및 스키마 실행
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 스키마 실행
    cursor.executescript(schema_sql)
    conn.commit()
    
    print(f"✅ 데이터베이스 스키마 생성 완료: {DB_PATH}")
    return conn

def main():
    """메인 실행 함수"""
    print("🚀 데이터베이스 초기화 시작...")
    
    try:
        # 데이터베이스 생성
        conn = create_database()
        conn.close()
        
        print("✅ 데이터베이스 초기화 완료!")
        print("💡 데이터를 로드하려면 다음 명령어를 실행하세요:")
        print("   python scripts/load_db_data.py")
        return 0
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
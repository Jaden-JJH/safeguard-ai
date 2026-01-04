import sqlite3
import os

# 상대 경로 사용 (프로젝트 루트 기준)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FOLDER = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_FOLDER, 'safeguard_patterns.db')

def create_database():
    """
    SQLite 데이터베이스 파일과 patterns 테이블을 생성합니다.
    """
    # database 폴더가 없으면 생성
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 이미 테이블이 존재하면 삭제 (초기화를 위해)
        cursor.execute('DROP TABLE IF EXISTS patterns')
        
        # patterns 테이블 생성 (데이터 스키마 정의)
        cursor.execute('''
        CREATE TABLE patterns (
            pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
            crime_type TEXT NOT NULL,
            scenario_name TEXT NOT NULL,
            simulation_mode TEXT NOT NULL,
            pattern_data TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"'{DB_PATH}'에 데이터베이스와 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        print(f"[Error] 데이터베이스 생성 실패: {e}")

if __name__ == '__main__':
    create_database()
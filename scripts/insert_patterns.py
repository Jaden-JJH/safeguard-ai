import sqlite3
import json
import os

# 상대 경로 사용 (프로젝트 루트 기준)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'safeguard_patterns.db')
JSON_PATH = os.path.join(BASE_DIR, 'data', 'patterns_final.json')

def insert_patterns_from_json():
    """
    JSON 파일에서 패턴 데이터를 읽어와 SQLite DB에 삽입합니다.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            patterns = json.load(f)
            
        for pattern in patterns:
            cursor.execute('''
            INSERT INTO patterns (crime_type, scenario_name, simulation_mode, pattern_data, is_active)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                pattern['crime_type'],
                pattern['scenario_name'],
                pattern['simulation_mode'],
                pattern['pattern_data'], # 이미 JSON 문자열이므로 그대로 저장
                pattern['is_active']
            ))
            
        conn.commit()
        conn.close()
        
        print(f"{len(patterns)}개의 패턴이 '{DB_PATH}'에 성공적으로 삽입되었습니다.")
        
    except FileNotFoundError:
        print(f"[Error] '{JSON_PATH}' 파일을 찾을 수 없습니다. 3_pattern_generation.ipynb를 먼저 실행하세요.")
    except Exception as e:
        print(f"[Error] DB 삽입 실패: {e}")

if __name__ == '__main__':
    insert_patterns_from_json()
# db.py
# PostgreSQL 연결 및 SQL 파일 읽기

'''
[Windows 시스템 환경변수 설정]
- 시작 > 시스템환경변수 편집 > 환경변수 > 시스템변수 > 새로만들기
- PGHOST : localhost
- PGPORT : 5432
- PGDATABASE : 데이터베이스명 (day29)
- PGUSER : 사용자명 (day29)
- PGPASSWORD : 비밀번호 (day29)
- 설정 후 파이참 재기동
'''

import os
from pathlib import Path
import psycopg

# SQL 파일들 저장 디렉토리
SQL_DIR = Path(__file__).resolve().parent / 'sql'
if not SQL_DIR.exists(): # 디렉토리 없다면
    SQL_DIR.mkdir(parents=True, exist_ok=True) # 새로 생성

# 커넥션 생성 함수
def get_connection():
    # 시스템환경변수에 설정한 키들
    keys = ('PGHOST', 'PGPORT', 'PGDATABASE', 'PGUSER', 'PGPASSWORD')
    missing = [key for key in keys if not os.environ.get(key)]
    if missing: # 없는 키들에 대해서
        raise ValueError('환경변수를 설정하세요: ' + ','.join(missing))
    return psycopg.connect(
        host=os.environ['PGHOST'],
        port=int(os.environ['PGPORT']),
        dbname=os.environ['PGDATABASE'],
        user=os.environ['PGUSER'],
        password=os.environ['PGPASSWORD'],
        connect_timeout=5 # 5초간 연결 대기
    )

# 파일명에 해당하는 SQL 문자열을 리턴하는 함수
def load_sql(filename):
    path = (SQL_DIR / filename).resolve() # SQL파일의 서버상의 실제경로
    # 생성된 sql디렉토리에 SQL파일이 없거나 SQL파일의 확장자가 sql이 아니라면
    if path.parent != SQL_DIR.resolve() or path.suffix != '.sql':
        raise ValueError('sql폴더의 .sql파일명만 지정하세요.')
    return path.read_text(encoding='utf-8') # SQL파일내의 문자열을 리턴


























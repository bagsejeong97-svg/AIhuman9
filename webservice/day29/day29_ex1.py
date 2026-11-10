# day29_ex1.py
# PostgreSQL + pstcopg CRUD 실습

# pip install "psycopg[binary]"

import psycopg
from db import get_connection, load_sql
from util.print_util import pp,up

# 테이블 생성 함수
def create_table(conn):
    sql = load_sql('speaker_create_table.sql')
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit() # 커밋을 해야 데이터베이스에 반영됨
# create_table(get_connection())


# insert
def add_speaker(conn,name,language,sample_count):
    sql = load_sql('speaker_add_speaker.sql')
    with conn.cursor() as cur:
        cur.execute(sql,(name,language,sample_count))
        row = cur.fetchone()
        conn.commit()
        return row[0] # ID 반환

# result = add_speaker(get_connection(),'홍길동','한국어',300)
# result = add_speaker(get_connection(),'강감찬','영어',500)
# result = add_speaker(get_connection(),'윤종신','불어',700)
# pp(result)

# select all
def get_speakers(conn):
    sql = load_sql('speaker_get_speakers.sql')
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall() # 전체 조회 결과 행 튜플들의 리스트 반환

# pp(get_speakers(get_connection()))

# 조건 SELECT ONE
def get_speakers_by_language(conn,language):
    sql = load_sql('speaker_get_speakers_by_language.sql')
    with conn.cursor() as cur:
        cur.execute(sql,(language,))
        return cur.fetchall() # 조회된 행 반환

# pp(get_speakers_by_language(get_connection(),'한국어'))

# UPDATE
def update_sample_count(conn,speaker_id,sample_count):
    sql = load_sql('speaker_update_sample_count.sql')
    with conn.cursor() as cur:
        cur.execute(sql,(sample_count,speaker_id))
        conn.commit()
        return cur.rowcount # 쿼리 영향 받은 행의 수를 리턴

# rcount = update_sample_count(get_connection(),1,150)
# pp(rcount)

# DELETE
def delete_speaker(conn,speaker_id):
    sql = load_sql('speaker_delete_speakers.sql')
    with conn.cursor() as cur:
        cur.execute(sql,(speaker_id,))
        conn.commit()
        return cur.rowcount

# rcount = delete_speaker(get_connection(),1)
# pp(rcount)































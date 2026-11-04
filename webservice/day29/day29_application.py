# day29_application.py
# 주제:
import psycopg
from db import get_connection, load_sql
from util.print_util import pp, up

def create_table(conn):
    sql = """CREATE TABLE IF NOT EXISTS jobs (
        id SERIAL PRIMARY KEY ,
        company VARCHAR(100) NOT NULL,
        position VARCHAR(100) NOT NULL,
        location VARCHAR(50) NOT NULL,
        salary INTEGER NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT '모집중');
    
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
    pp('테이블 생성')


def insert_job(conn,company,  position, location, salary, status='모집중'):
    sql = """INSERT INTO jobs (company, position, location, salary, status)
    values (%s, %s, %s, %s, %s);
    """
    with conn.cursor() as cur:
        cur.execute(sql, (company, position, location, salary, status))
        conn.commit()
    pp('insert success')

def all_jobs(conn):
    sql = """SELECT * FROM jobs ORDER BY ID DESC;"""
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    pp('전체 조회',rows)
    return rows

def location_job(conn, location):
    sql = """SELECT * FROM jobs WHERE location = %s;"""
    with conn.cursor() as cur:
        cur.execute(sql, (location,))
        locations = cur.fetchall()
        pp('지역별 공고 조회',locations)
        return locations

def update_job(conn, id,salary):
    sql = """UPDATE jobs SET salary = %s WHERE id = %s;"""
    with conn.cursor() as cur:
        cur.execute(sql, (salary, id))
        conn.commit()
        pp('수정 성공',cur.rowcount)
        return cur.rowcount


def delete_jobs(conn, id):
    sql = """DELETE FROM jobs 
     WHERE id = %s;"""
    with conn.cursor() as cur:
        cur.execute(sql, (id,))
        conn.commit()
        pp('삭제성공',cur.rowcount)
        return cur.rowcount

# TRUNCATE TABLE JOBS RESTART IDENTITY;
def main():
    with get_connection() as gc:
        create_table(gc)

        sql = """
        TRUNCATE TABLE jobs RESTART IDENTITY;
        """

        truncate_sql = """TRUNCATE TABLE jobs RESTART IDENTITY;"""
        with gc.cursor() as cur:
            cur.execute(truncate_sql)
        gc.commit()  #

        # 샘플 등록
        insert_job(gc, "네이버", "백엔드 개발자", "판교", 6000)
        insert_job(gc, "카카오", "프론트엔드 개발자", "판교", 5500,'마감')
        insert_job(gc, "라인", "AI 엔지니어", "서울", 6500)

        # 조회
        all_jobs(gc)
        location_job(gc, "판교")

        # 수정 및 삭제 (rowcount 확인)
        update_job(gc, 1, 6500)
        delete_jobs(gc, 2)

        # 최종 결과 확인
        all_jobs(gc)


if __name__ == "__main__":
    main()







































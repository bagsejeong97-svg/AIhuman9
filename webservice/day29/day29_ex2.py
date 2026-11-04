# day29_ex2.py
# GROUP BY + HAVING 조회, JOIN 조회
# GROUP BY : 컬럼의 값이 같은 행들을 그룹핑
# HAVING : 그룹핑 한 후에 각 그룹에 조건을 부여
# JOIN : 두 개 이상의 테이블을 논리적으로 하나로 연결해서 조회

import psycopg
from db import get_connection, load_sql
from util.print_util import pp, up

# 두개의 테이블 생성 함수
def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute(load_sql('employee_create_tables.sql'))
        cur.execute(load_sql('employee_create_tables_2.sql'))
        conn.commit()

# create_tables(get_connection())

# 샘플 데이터를 등록하는 함수
def insert_data(conn):
    with conn.cursor() as cur:

        # 테이블 데이터 초기화
        cur.execute(load_sql('employee_insert_data.sql'))

        # 부서테이블 데이터 등록
        departments = [('개발팀',), ('데이터팀',), ('기획팀',)]
        cur.executemany( # departments리스트의 요소들을 반복해서 쿼리 수행
            load_sql('department_insert_data2.sql'),
            departments
        )
        pp(cur.rowcount, '개의 부서 등록됨!')

        # 직원테이블 데이터 등록
        employees = [
            ('김개발', 1, 4500), ('이개발', 1, 5200), ('박개발', 1, 4800),
            ('최데이터', 2, 5000), ('정데이터', 2, 5500), ('한기획', 3, 4000)
        ]
        cur.executemany(
            load_sql('employee_insert_data3.sql'),
            employees
        )
        pp(cur.rowcount, '명의 직원 등록됨!')

    conn.commit()

# insert_data(get_connection())

# 그룹핑 조회
def group_by_having(conn):
    sql = load_sql('employee_groupby.sql')
    with conn.cursor() as cur:
        cur.execute(sql,(4800,))
        rows = cur.fetchall()
    pp('부서별 평균 연봉이 4,800만원 이상인 부서')
    for row in rows:
        pp(
            f'부서ID={row[0]},인원={row[1]}명,'
            f'평균연봉={row[2]}만원'
        )
group_by_having(get_connection())

# join
def join_query(conn):
    sql = load_sql('departments_employees_join.sql')
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    pp('조인 결과')
    for row in rows:
        pp(
            f'직원ID={row[0]}, 직원명={row[1]}'
            f', 부서명={row[2]}, 연봉={row[3]}명'
        )
join_query(get_connection())






































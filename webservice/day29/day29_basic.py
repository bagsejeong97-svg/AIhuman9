# day29_basic.py
# 주제:

import os
import psycopg
from db import get_connection, load_sql
from util.print_util import pp, up


def create_table(conn):
    sql = load_sql('basic_book_create_table.sql')
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
# create_table(get_connection())


def add_book_information(conn,title,author,stock):
    sql = load_sql('basic_book_information.sql')
    with conn.cursor() as cur:
        cur.execute(sql,(title,author,stock))
        row = cur.fetchone()
        conn.commit()
        return row[0]

# result = add_book_information(get_connection(),'책1','저자1',1)
# result = add_book_information(get_connection(),'책2','저자2',2)
# result = add_book_information(get_connection(),'책3','저자3',3)

def all_books(conn):
    sql = load_sql('basic_book_all.sql')
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()
# pp(all_books(get_connection()))

def one_book(conn,stock):
    sql = load_sql('basic_book_one_book.sql')
    with conn.cursor() as cur:
        cur.execute(sql,(stock,))
        return cur.fetchall()

def update_books(conn,id,stock):
    sql = load_sql('basic_book_update_books.sql')
    with conn.cursor() as cur:
        cur.execute(sql,(stock,id))
        conn.commit()

# pp(update_books(get_connection(),1,500))
# pp(one_book(get_connection(),2))

def delete_book(conn,id):
    sql = load_sql('basic_book_delete_book.sql')
    with conn.cursor() as cur:
        cur.execute(sql,(id,))
        conn.commit()

if __name__ == '__main__':
    with get_connection() as conn:
        print("=== 1. 테이블 생성 ===")
        create_table(conn)
        pp('책 생성')
        book1 = add_book_information(get_connection(),'홍길동','박세정',10)
        pp('전체 책 조회')
        pp(len(all_books(get_connection())))






















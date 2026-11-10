# day29_challenge.py
# 주제:
import psycopg
from db import get_connection, load_sql
from util.print_util import pp, up

def create_table(conn):
    with conn.cursor() as cur:
        sql = """CREATE TABLE IF NOT EXISTS model_runs (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(80) NOT NULL,
    dataset_name VARCHAR(80) NOT NULL,
    accuracy NUMERIC(5, 4) NOT NULL, -- 전체 5자리, 소수이하 4자리
    epochs INTEGER NOT NULL,
    memo TEXT
)"""
        cur.execute(sql)

def add_run(conn,model_name,dataset_name,accuracy,epochs,memo):
    with conn.cursor() as cur:
        sql = """INSERT INTO model_runs(model_name,dataset_name,accuracy,epochs,memo) values (%s,%s,%s,%s,%s) returning id"""
        cur.execute(sql,(model_name,dataset_name,accuracy,epochs,memo))
        return cur.fetchone()[0] # 등록 후 등록된 자동증가번호(id) 리턴 출력

def get_runs(conn):
    with conn.cursor() as cur:
        sql = """SELECT model_name,dataset_name,accuracy,epochs,memo from model_runs order by id"""
        cur.execute(sql)
        return cur.fetchall()

def get_runs_by_accuracy(conn,min_accuracy):
    with conn.cursor() as cur:
        sql = """SELECT id, model_name, accuracy
                    FROM model_runs
                    WHERE accuracy >= %s
                    ORDER BY accuracy DESC"""
        cur.execute(sql,(min_accuracy,))
        return cur.fetchall()

def update_memo(conn,run_id,memo):
    with conn.cursor() as cur:
        sql = """UPDATE model_runs SET memo=%s WHERE id=%s"""
        cur.execute(sql,(memo,run_id))
        return cur.rowcount
def delete_run(conn,run_id):
    with conn.cursor() as cur:
        sql = """DELETE FROM model_runs WHERE id=%s"""
        cur.execute(sql,(run_id,))
        return cur.rowcount

def main():
    try:
        with get_connection() as conn:

            create_table(conn)

            with conn.cursor() as cur:
                sql = """truncate table model_runs restart IDENTITY """
                cur.execute(sql)
                conn.commit()

                pp('정상 Transaction')

                try:

                    id1 = add_run(
                        conn,'CNN','FashionMNIST',
                        0.9125,15,'기본모델'
                    )
                    id2 = add_run(
                        conn, 'MLP', 'FashionMNIST',
                        0.8870, 20, 'Dense모델'
                    )

                    pp(f'생성 id: {id1},{id2}')

                    updated = update_memo(conn,id1,'튜닝 예정')
                    pp(f'수정 ROW수 : {updated}')

                    conn.commit() # Transaction 완료




                except Exception as e:
                    conn.rollback() #Transaction 취소
                    pp(f'Transaction 취소:{e}')

                pp(get_runs(conn))

                pp('정확도 0.90 이상')
                pp(get_runs_by_accuracy(conn,0.90))

                pp('의도적인 오류와 ROLLBACK')
                try:
                    # model_name이 None이므로 예외발생되어 commit되지 않고 rollback됨
                    # 테이블 최초 설정시 not null 설정
                    add_run(conn,None,'Iris',0.95,10,'오류 실험')
                    conn.commit() # 예외 발생 없으면 commit 실행
                except Exception as e:
                    conn.rollback() # 예외 발생시 rollback 진행
                    pp(f'ROLLBACK 실행: {e}')

                pp('ROLLBACK 이후 데이터')
                pp(get_runs(conn))

                pp('삭제')
                pp(f'삭제된 ROW의 수 : {delete_run(conn,id2)}')
                conn.commit()

                pp(get_runs(conn))

    except psycopg.Error as e:
        pp(f'PostgreSQL 에러: {e}')


if __name__ == '__main__':
    main()























































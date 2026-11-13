# day56_basic.py
# 주제:
import os
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime, timezone
import httpx
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from util.print_util import pp, up

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', '')

Library_router = APIRouter(
    prefix="/library",
    tags=["library"]
)

class ReservationCreate(BaseModel):
    book_title: str = Field(min_length=2,max_length=80)
    reservation_name: str = Field(min_length=2,max_length=30)

class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : int
    book_title : str
    reservation_name : str


def db_connection():
    if not DATABASE_URL:
        raise HTTPException(503, 'DATABASE_URL을 설정해야 합니다.')
    try:
        # 조회한 행을 딕셔너리로 가져오는 데이터베이스 커넥션
        # with가 끝나면 데이터베이스 커넥션도 종료
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
            yield conn # 라우터로 연결 객체 전달
    except psycopg.OperationalError:
        raise HTTPException(503, '데이터베이스 연결 실패')


app = FastAPI(
    title='도서 대출 예약 API',
    version='0.0.1'
)

def initialize_schema():
    if not DATABASE_URL:
        return
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
        ID BIGSERIAL PRIMARY KEY,
            BOOK_TITLE VARCHAR(80) NOT NULL,
            RESERVATION_NAME VARCHAR(30) NOT NULL
        )
        ''')



initialize_schema()


@Library_router.post(
    "",
    response_model=ReservationOut,
    status_code=201
)

def create_reservation(
    data: ReservationCreate,
    conn=Depends(db_connection)
):
    row = conn.execute(
        """
        INSERT INTO reservations (BOOK_TITLE, RESERVATION_NAME)
        VALUES (%s, %s)
        RETURNING *
        """,
        (data.book_title, data.reservation_name)
    ).fetchone()

    return row


def list_reservation_service(conn, limit, offset):
    return conn.execute('''
        SELECT * 
        FROM reservations 
        ORDER BY ID DESC
        LIMIT %s
        OFFSET %s
    ''', (limit, offset)).fetchall()



def get_reservation_service(conn, reservation_id):
    return conn.execute('''
        SELECT *
        FROM reservations 
        WHERE ID=%s
    ''', (reservation_id,)).fetchone()


def delete_reservation_service(conn, reservation_id):
    row = conn.execute('''
        DELETE FROM reservations 
        WHERE ID=%s
        RETURNING ID
    ''', (reservation_id,)).fetchone()

    return row is not None

@Library_router.get("", response_model=list[ReservationOut])
def list_reservations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    conn=Depends(db_connection)
):
    return list_reservation_service(conn, limit, offset)



@Library_router.get('/{reservation_id}', response_model=ReservationOut)
def get_reservation(reservation_id: int, conn=Depends(db_connection)):
    reservation = get_reservation_service(conn, reservation_id)
    if not reservation:
        raise HTTPException(404,'해당데이터가 없습니다.')
    return reservation


@Library_router.delete("/{reservation_id}")
def delete_reservation(reservation_id: int, conn=Depends(db_connection)):
    if not delete_reservation_service(conn, reservation_id):
        raise HTTPException(404,'해당데이터가 없습니다.')
    return {'deleted': True, 'reservation_id': reservation_id}









app.include_router(Library_router)




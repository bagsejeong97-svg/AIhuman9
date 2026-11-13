# day56_application.py
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

seminar_router = APIRouter(
    prefix="/seminar",
    tags=["seminar"],
)


class SeminarCreate(BaseModel):
    seminar_name: str = Field(min_length=2,max_length=80)
    attendee: str = Field(min_length=1,max_length=30)
    status: str = Field(
        default="requested",
        pattern="^(requested|confirmed|cancelled)$"



    )
class SeminarUpdate(BaseModel):
    seminar_name: str | None = Field(default=None, min_length=2, max_length=80)
    attendee: str | None = Field(default=None, min_length=1, max_length=30)
    status: str | None = Field(
        default=None,
        pattern="^(requested|confirmed|cancelled)$"
    )



class SeminarOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : int
    seminar_name : str
    attendee : str
    status : str
    created_at : datetime

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
    title = '학과 세미나 신청 API',
    version='0.0.1'
)

def initialize_schema():
    if not DATABASE_URL:
        return
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS seminar_signups_history (
        ID BIGSERIAL PRIMARY KEY,
            SEMINAR_NAME VARCHAR(80) NOT NULL,
            ATTENDEE VARCHAR(30) NOT NULL,
            STATUS VARCHAR NOT NULL,
            CREATED_AT TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        ''')


initialize_schema()

@seminar_router.post(
    "",
    response_model=SeminarOut,
    status_code=201
)



def create_seminar(
    payload: SeminarCreate,
    conn = Depends(db_connection)
):
    row = conn.execute(
        """
        INSERT INTO seminar_signups_history
        (seminar_name, attendee, status)
        VALUES (%s, %s, %s)
        RETURNING *
        """,
        (payload.seminar_name, payload.attendee, payload.status)
    ).fetchone()

    return {
        "id": row["id"],
        "seminar_name": row["seminar_name"],
        "attendee": row["attendee"],
        "status": row["status"],
        "created_at": row["created_at"]
    }


def list_seminars_service(conn, limit, offset):
    return conn.execute('''
    select * from seminar_signups_history
                        order by id desc
                        limit %s
                        offset %s''', (limit, offset)).fetchall()

def get_seminar_service(conn, seminar_id):
    return conn.execute('''
    select * from seminar_signups_history
        where id=%s
    ''', (seminar_id,)).fetchone()

def update_seminar_service(conn, seminar_id, data):
    before = get_seminar_service(conn, seminar_id)

    if before is None:
        return None

    changes = data.model_dump(exclude_unset=True)

    if not changes:
        return before

    seminar_name = changes.get('seminar_name', before['seminar_name'])
    attendee = changes.get('attendee', before['attendee'])
    status = changes.get('status', before['status'])

    row = conn.execute('''
    UPDATE seminar_signups_history
    SET seminar_name=%s, attendee=%s, status=%s
    WHERE id=%s
    RETURNING *
    ''', (seminar_name, attendee, status, seminar_id)).fetchone()

    return row

def delete_seminar_service(conn, seminar_id):
    row= conn.execute('''
    delete from seminar_signups_history
                        where id=%s
                        returning id''',(seminar_id,)).fetchone()

    return row is not None

@seminar_router.get("")
def get_seminars(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    conn = Depends(db_connection)
):
    return list_seminars_service(conn, limit, offset)


@seminar_router.get('/{seminar_id}', response_model=SeminarOut)
def get_seminar(seminar_id: int, conn = Depends(db_connection)):
    seminar = get_seminar_service(conn, seminar_id)
    if not seminar:
        raise HTTPException(404,'해당데이터가 없습니다')
    return seminar


@seminar_router.patch("/{seminar_id}", response_model=SeminarOut)
def update_seminar(seminar_id: int, data: SeminarUpdate, conn = Depends(db_connection)):
    seminar = update_seminar_service(conn, seminar_id, data)
    if not seminar:
        raise HTTPException(404,'해당데이터가 없습니다.')
    return seminar

@seminar_router.delete("/{seminar_id}")
def delete_seminar(seminar_id: int, conn = Depends(db_connection)):
    if not delete_seminar_service(conn, seminar_id):
        raise HTTPException(404,'해당데이터가 없습니다.')
    return {'deleted': True,'id': seminar_id}






app.include_router(seminar_router)























































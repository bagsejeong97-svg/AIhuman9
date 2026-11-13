# day56_ex.py
# FastAPI APIRouter를 통한 라우터 분리
# PostgreSQL 연동한 데이터베이스 작업
# PERSO 언어 목록 / Space 목록

'''
[데이터베이스 사용자 및 DB 생성]
CMD > psql -U postgres
CREATE USER day56 WITH PASSWORD 'day56';
CREATE DATABASE day56 OWNER day56;
* 주의 : PostgreSQL은 큰따옴표로 감싸지 않은 식별자를 자동으로 소문자로 변환함
        데이터베이스 삭제 : DROP DATABASE 데이터베이스명
        사용자계정 삭제 : DROP USER 사용자계정명

[.env 파일 생성]
DATABASE_URL=postgresql://day56:day56@localhost:5432/day56
PERSO_API_KEY=
'''

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
PERSO_API_KEY = os.getenv('PERSO_API_KEY', '')
PERSO_BASE = 'https://api.perso.ai'

job_router = APIRouter(
    prefix='/api/v1/jobs', # 라우터 앞에 붙는 경로
    tags=['jobs'] # 문서내에서 라우터 검색용 태그
)

perso_router = APIRouter(
    prefix='/api/v1/perso',
    tags=['perso']
)

class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    source_lang: str = Field(default='ko', min_length=2, max_length=10)
    target_lang: str = Field(default='en', min_length=2, max_length=10)

class JobPatch(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=100)
    status: str | None = Field(default=None, pattern='^(draft|ready|done)$')

class JobOut(BaseModel):
    # 모델 설정 : from_attributes=True 객체 속성에서도 값을 읽도록 허용
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    source_lang: str
    target_lang: str
    status: str
    created_at: datetime

def db_connection():
    if not DATABASE_URL:
        raise HTTPException(503, 'DATABASE_URL을 설정해야 합니다.')
    try:
        # 조회한 행을 딕셔너리로 가져오는 데이터베이스 커넥션
        # with가 끝나면 데이터베이스 커넥션도 종료
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
            yield conn # 라우터로 연결 객체 전달
    except psycopg.OperationalError as e:
        raise HTTPException(503, '데이터베이스 연결 실패')

# 테이블 생성 함수
def initialize_schema():
    if not DATABASE_URL:
        return
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS MEDIA_JOBS (
                ID BIGSERIAL PRIMARY KEY,
                TITLE VARCHAR(100) NOT NULL,
                SOURCE_LANG VARCHAR(100) NOT NULL,
                TARGET_LANG VARCHAR(100) NOT NULL,
                STATUS VARCHAR(10) NOT NULL DEFAULT 'draft',
                CREATED_AT TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        ''')

# FastAPI 앱의 생명주기를 관리하는 함수
@asynccontextmanager
async def lifespan(app: FastAPI):
    pp('FastAPI 서버 시작')
    initialize_schema()
    yield # 서버가 요청을 처리하는 구간
    pp('FastAPI 서버 종료')

app = FastAPI(
    lifespan=lifespan, # 앱의 생명주기 관리하는 함수 등록
    title='미디어 작업 관리 및 Perso 연계 API',
    version='0.0.1'
)


### Job Service (Business Logic)

# 데이터 한건 입력 후 입력한 데이터를 리턴해서 한 건 조회하는 함수
def create_job_service(conn, data):
    row = conn.execute('''
        INSERT INTO MEDIA_JOBS (TITLE, SOURCE_LANG, TARGET_LANG)
        VALUES (%s, %s, %s)
        RETURNING *
    ''', (data.title, data.source_lang, data.target_lang)).fetchone()
    conn.commit()
    return row

# 페이징 목록 조회
def list_jobs_service(conn, limit, offset):
    return conn.execute('''
        SELECT * 
        FROM MEDIA_JOBS 
        ORDER BY ID DESC
        LIMIT %s
        OFFSET %s
    ''', (limit, offset)).fetchall()

# 단건 조회
def get_job_service(conn, job_id):
    return conn.execute('''
        SELECT *
        FROM MEDIA_JOBS
        WHERE ID=%s
    ''', (job_id,)).fetchone()

# 부분 수정
def update_job_service(conn, job_id, data):
    before = get_job_service(conn, job_id) # 수정 전
    if before is None:
        return None
    # exclude_unset=True : 요청에서 전달하지 않은 필드는 제외
    changes = data.model_dump(exclude_unset=True)
    if not changes: # 수정할 것이 없다면 이전 것을 리턴
        return before
    title = changes.get('title', before['title'])
    status = changes.get('status', before['status'])
    if title is None or status is None:
        raise HTTPException(422, 'null로 변경할 수 없습니다.')
    row = conn.execute('''
        UPDATE MEDIA_JOBS 
        SET TITLE = %s, STATUS = %s
        WHERE ID = %s
        RETURNING *
    ''', (title, status, job_id)).fetchone()
    conn.commit()
    return row

# 삭제
def delete_job_service(conn, job_id):
    row = conn.execute('''
        DELETE FROM MEDIA_JOBS
        WHERE ID=%s
        RETURNING ID
    ''', (job_id,)).fetchone()
    conn.commit()
    return row is not None

### Job Router

@job_router.post('', response_model=JobOut, status_code=201)
def create_job(data: JobCreate, conn=Depends(db_connection)):
    return create_job_service(conn, data)

@job_router.get('', response_model=list[JobOut])
def list_jobs(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    conn=Depends(db_connection)
):
    return list_jobs_service(conn, limit, offset)

@job_router.get('/{job_id}', response_model=JobOut)
def get_job(job_id: int, conn=Depends(db_connection)):
    job = get_job_service(conn, job_id)
    if not job:
        raise HTTPException(404, '해당 데이터가 없습니다.')
    return job

@job_router.patch('/{job_id}', response_model=JobOut)
def update_job(job_id: int, data: JobPatch, conn=Depends(db_connection)):
    job = update_job_service(conn, job_id, data)
    if not job:
        raise HTTPException(404, '해당 데이터가 없습니다.')
    return job

@job_router.delete('/{job_id}')
def delete_job(job_id: int, conn=Depends(db_connection)):
    if not delete_job_service(conn, job_id):
        raise HTTPException(404, '해당 데이터가 없습니다.')
    return {'deleted': True, 'id': job_id}

### Perso Service

def perso_get(path,params=None):
    if not PERSO_API_KEY:
        raise HTTPException(503,'PERSO_API_KEY가 설정되지 않았습니다.')
    headers = {'XP-API-key': PERSO_API_KEY} # 요청 헤더에 API KEY 추가
    try:
        with httpx.Client(timeout=15.0) as client: # 동기 방식 클라이언트
            response = client.get( # GET요청 보내고 응답 획득
                PERSO_BASE + path, # 요청 URL (Endpoint)
                headers=headers, # 요청 헤더
                params=params # 요청 파라미터
            )
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        raise HTTPException(504,'응답 시간 초과')
    except httpx.HTTPStatusError as e:
        raise HTTPException(502,f'Perso API HTTP {e.response.status_code}')
    except (httpx.RequestError, ValueError):
        raise HTTPException(502,'Perso API 연결 또는 JSON 해석 실패')


### Perso Router

@perso_router.get('/languages')
def perso_languages():
    return perso_get('/video-translator/api/v1/language')

@perso_router.get('/spaces')
def perso_spaces():
    return perso_get('/portal/api/v1/spaces') # Space 목록

@app.get('/health')
def health():
    return {
        'status': 'ok',
        'db_configured' : bool(DATABASE_URL),
        'perso_configured' : bool(PERSO_API_KEY)
    }



app.include_router(job_router) # FastAPI 앱에 job_router  등록
app.include_router(perso_router) # FastAPI 앱에 perso_router 등록
























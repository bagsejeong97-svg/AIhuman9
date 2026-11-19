"""PostgreSQL 연결 — SQL을 실행한 뒤 연결을 확실히 닫습니다."""
from contextlib import asynccontextmanager
import psycopg
from psycopg.rows import dict_row
from backend.core.config import get_settings

@asynccontextmanager
async def db_connection():
    dsn = get_settings().database_url
    if not dsn:
        raise RuntimeError("DATABASE_URL 설정이 필요합니다")
    async with await psycopg.AsyncConnection.connect(dsn, row_factory=dict_row) as conn:
        yield conn

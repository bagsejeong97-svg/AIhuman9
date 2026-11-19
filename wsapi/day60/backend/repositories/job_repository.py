"""Repository Layer — SQL은 이 모듈 안에서만 실행합니다."""
from typing import Any
from psycopg.types.json import Jsonb
from backend.database.connection import db_connection

async def store_media(space_seq:int, media_seq:int, kind:str, filename:str, size:int):
    async with db_connection() as conn:
        await conn.execute("""INSERT INTO media_assets(space_seq,media_seq,kind,original_filename,file_size)
            VALUES (%s,%s,%s,%s,%s) ON CONFLICT (space_seq,media_seq) DO NOTHING""",
            (space_seq,media_seq,kind,filename,size))

async def media_for_space(space_seq:int, media_seq:int):
    async with db_connection() as conn:
        cur=await conn.execute("SELECT * FROM media_assets WHERE space_seq=%s AND media_seq=%s",(space_seq,media_seq))
        return await cur.fetchone()

async def save_jobs(space_seq:int, project_seqs:list[int], job_type:str, media_seq:int|None,
                    title:str, parent_project_seq:int|None=None):
    async with db_connection() as conn:
        for project_seq in project_seqs:
            await conn.execute("""INSERT INTO perso_jobs
              (space_seq,project_seq,media_seq,parent_project_seq,job_type,title)
              VALUES (%s,%s,%s,%s,%s,%s)
              ON CONFLICT (space_seq,project_seq) DO NOTHING""",
              (space_seq,project_seq,media_seq,parent_project_seq,job_type,title))

async def update_status(space_seq:int,project_seq:int,status:str,progress:float|None,raw:dict[str,Any]):
    async with db_connection() as conn:
        await conn.execute("""UPDATE perso_jobs SET status=%s, progress=%s, result_json=%s,
          updated_at=NOW() WHERE space_seq=%s AND project_seq=%s""",
          (status,progress,Jsonb(raw),space_seq,project_seq))

async def list_jobs(space_seq:int|None=None,limit:int=100):
    async with db_connection() as conn:
        if space_seq is None:
            cur=await conn.execute("""SELECT id,space_seq,project_seq,media_seq,parent_project_seq,
                 job_type,title,status,progress,last_error,created_at,updated_at
                 FROM perso_jobs ORDER BY created_at DESC LIMIT %s""",(limit,))
        else:
            cur=await conn.execute("""SELECT id,space_seq,project_seq,media_seq,parent_project_seq,
                 job_type,title,status,progress,last_error,created_at,updated_at
                 FROM perso_jobs WHERE space_seq=%s ORDER BY created_at DESC LIMIT %s""",(space_seq,limit))
        return await cur.fetchall()

async def get_job(space_seq:int,project_seq:int):
    async with db_connection() as conn:
        cur=await conn.execute("SELECT * FROM perso_jobs WHERE space_seq=%s AND project_seq=%s",(space_seq,project_seq))
        return await cur.fetchone()

async def mark_error(space_seq:int,project_seq:int,description:str):
    async with db_connection() as conn:
        await conn.execute("""UPDATE perso_jobs SET last_error=%s, updated_at=NOW()
            WHERE space_seq=%s AND project_seq=%s""",(description[:1000],space_seq,project_seq))

async def audit(event_type:str,description:str,space_seq:int|None=None,project_seq:int|None=None):
    async with db_connection() as conn:
        await conn.execute("""INSERT INTO operation_events(event_type,description,space_seq,project_seq)
          VALUES (%s,%s,%s,%s)""",(event_type,description[:1000],space_seq,project_seq))

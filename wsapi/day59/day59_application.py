
# day59_application.py
import os
from urllib.parse import quote, urlsplit, urlunsplit
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

load_dotenv()

BASE = 'https://api.perso.ai'
PREFIX = '/video-translator/api/v1'
KEY = os.getenv('PERSO_API_KEY', '').strip()

app = FastAPI(title='day59_application')


async def call(method: str, path: str, *, params=None, json=None):

    if not KEY:
        raise HTTPException(
            503,
            'PERSO_API_KEY 환경 변수가 없습니다.'
        )

    try:
        async with httpx.AsyncClient(
            timeout=60.0,
            follow_redirects=False
        ) as client:

            response = await client.request(
                method,
                BASE + path,
                params=params,
                json=json,
                headers={'XP-API-KEY': KEY}
            )
            print('요청 URL:', response.request.url)
            print('응답 코드:', response.status_code)
            print('응답 내용:', response.text)

    except httpx.TimeoutException as exc:
        raise HTTPException(504, 'Perso API 요청 시간 초과') from exc

    except httpx.RequestError as exc:
        raise HTTPException(502, 'Perso API 연결 오류') from exc

    try:
        data = response.json() if response.content else {}

    except ValueError:
        data = {'message': response.text[:120]}

    if response.status_code >= 400:
        raise HTTPException(
            response.status_code,
            detail=data
        )

    return data

class CreateStt(BaseModel):
    spaceSeq:int = Field(gt=0)
    mediaSeq:int = Field(gt=0)
    title:str = Field(min_length=1)


@app.post('/episodes/transcribe')
async def transcribe(
    body: CreateStt,
    confirm_cost: bool = Query(False)
):
    if not confirm_cost:
        raise HTTPException(400,'결제가 필요합니다.')

    result = await call(
        'POST',
        f'{PREFIX}/projects/spaces/{body.spaceSeq}/stt',
        json ={
            'title': body.title,
            'mediaSeq': body.mediaSeq,
            'isVideoProject': False
        }

    )
    ids = result.get('result', {}).get('startGenerateProjectIdList', [])
    if not isinstance(ids, list) or not ids:
        raise HTTPException(502,'perso 응답에 프로젝트 ID가 없다')
    return {
        'projectSeqList':ids,
        'message': '프로젝트별 진행률을 별도로 확인하시오'
    }

@app.get('/episodes/{project_seq}/spaces/{space_seq}/progress')
async def get_progress(
    space_seq: int,
    project_seq: int
):
    result = await call(
        'GET',
        f'{PREFIX}/projects/{project_seq}/space/{space_seq}/progress'
    )

    return result


@app.get('/episodes/{project_seq}/spaces/{space_seq}/script')
async def get_script(
    space_seq: int,
    project_seq: int,
):
    result = await call(
        'GET',
        f'{PREFIX}/projects/{project_seq}/spaces/{space_seq}/stt/script'
    )
    return result













































































# day58_basic.py
# [Basic] 지역 관광안내의 실제 지원 언어와 TTS 모델 조회

import os
import httpx

from util.print_util import pp

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

load_dotenv()

BASE = 'https://api.perso.ai'
PREFIX = '/video-translator/api/v1'
KEY = os.getenv('PERSO_API_KEY', '')

app = FastAPI(title='지역 관광안내 언어 조회')



async def call(method: str, path: str):
    if not KEY:
        raise HTTPException(503, 'API 키가 없습니다.')

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(
                method,
                BASE + path,
                headers={'XP-API-KEY': KEY}
            )

        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            exc.response.status_code,
            'Perso API 요청 실패'
        )

    except httpx.RequestError:
        raise HTTPException(502, 'Perso API 연결 실패')


@app.get('/perso/languages')
async def get_languages():
    languages = await call('GET', f'{PREFIX}/languages')
    return languages

@app.get('/guide/languages')
async def guide_get_languages(
    code: list[str] = Query(...),
    model : str = Query(...)
):
    if any (c.lower() == 'auto' for c in code):
        raise HTTPException(422,'auto가 포함됨')

    languages = await call('GET', f'{PREFIX}/languages')
    result = []
    all_languages = languages.get('languages', [])

    for c in code:
        matched = []

        for lang in all_languages:
            if lang['code'] == c:
                matched.append(lang)

                supported_models = lang.get('supportedTtsModels', [])

                if model == 'ELEVEN_V3':
                    model = 'LINNET_3'
                supported = model in supported_models #bool

                result.append({
                    'code': lang['code'],
                    'name': lang['name'],
                    'languageTag': lang['languageTag'],
                    # 'experiment': lang['experiment'],
                    # 'models':lang['supportedTtsModels'],
                    'LINNET_3 = ELEVEN_V3': supported
                })

        if not matched:
            raise HTTPException(404,'지원하는 언어코드가 없음')

    return {'languages': result,'request_model':model}



















































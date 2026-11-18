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
MEDIA = 'https://portal-media.perso.ai'  # 결과 파일 서버
app = FastAPI(title='day59_challenge')


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

def file_url(path: str) -> str:
    if not isinstance(path, str) or not path.startswith('/'):
        raise HTTPException(502, '미디어 경로가 올바르지 않습니다')
    if path.startswith('//') or '\\' in path or '\x00' in path:
        raise HTTPException(502, '허용되지 않은 미디어 경로')
    return MEDIA + quote(path, safe='/%')


class TargetLanguage(BaseModel):
    languageCode: str
    ttsModel: str | None = None


class DubbingRequest(BaseModel):
    mediaSeq: int
    sourceLanguageCode: str = 'auto'
    targetLanguages: list[TargetLanguage] = Field(min_length=1)
    numberOfSpeakers: int = Field(default=1, ge=1)
    withLipSync: bool = False
    preferredSpeedType: str = Field(
        default='GREEN',
        pattern='^(GREEN|RED)$'
    )

def job_ids(data: dict) -> dict:
    result = data.get('result') or {}
    ids = result.get('startGenerateProjectIdList', [])
    if not isinstance(ids, list) or not ids:
        raise HTTPException(502, 'Perso 응답에 프로젝트 ID가 없습니다')
    return {'projectSeqList': ids,
            'message': '프로젝트별 진행률을 별도로 확인하세요'}



async def create_job(space_seq: int, kind: str, body: dict,
                     confirm: bool) -> dict:
    if not confirm:
        raise HTTPException(400, '생성에는 confirm_cost=true가 필요합니다')
    result = await call('POST',
                        f'{PREFIX}/projects/spaces/{space_seq}/{kind}',
                        json=body)
    return job_ids(result)


@app.post('/perso/spaces/{space_seq}/dubbing')
async def perso_dubbing(
        space_seq: int,
        body: DubbingRequest,
        confirm_cost: bool = Query(False)
):
    if any(t.languageCode=='auto' for t in body.targetLanguages):
        raise HTTPException(422,'대상언어의 auto 사용 불가')
    return await create_job(
        space_seq,
        'translate',
        body.model_dump(exclude_none=True),
        confirm_cost
    )



@app.get('/perso/spaces/{space_seq}/projects/{project_seq}/progress')
async def perso_progress(
        space_seq: int,
        project_seq: int
):
    return await call(
        'GET',
        f'{PREFIX}/projects/{project_seq}/space/{space_seq}/progress',
    )


@app.get('/perso/spaces/{space_seq}/projects/{project_seq}/download')
async def download_info(
        space_seq:int,
        project_seq:int,
        target:str = 'all' # .tar 압축
):
    allowed = {
        'all', 'dubbingVideo', 'lipSyncVideo', 'voiceAudio',
        'originalVoiceAudio', 'backgroundAudio',
        'voicewithBackgroundAudio', 'translatedAudio',
        'originalVoiceSpeakers', 'speakerSegmentExcel',
        'speakerSegmentWithTranslationExcel', 'scriptTimestamps',
        'originalSubBackground', 'audioScript',
    }
    if target not in allowed:
        raise HTTPException(422,f'허용되지 않는 다운로드{target}')
    data = await call(
        'GET',
        f'{PREFIX}/projects/{project_seq}/spaces/{space_seq}/download',
        params={'target': target}
    )
    result = data.get('result') or {}

    urls = {}


    def collect(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, str) and value.startswith('/perso-storage/'):
                    urls[key] =file_url(value)
                elif isinstance(value, (dict, list)):
                    collect(value) # 재귀
        elif isinstance(node, list):
            for value in node:
                collect(value) # 재귀

    collect(result)
    return {
        'target':target,
        'urls':urls,
        'note': '자막 SRT/VTT는 target=all의 .tar 아카이브에 포함되어 있음'
    }




# # spec-seq : 612722      / LINNET_4
#
#  stt_clean_en.wav / mediaSeq : 65731 / projectSeqList": [ 447434 ]
#
#  separation_voice_music_en.wav/ mediaSeq": 65748 / projectSeqList": [ 447444 ]
#
# "dubbing_presentation_en.mp4 / "mediaSeq": 953942 /  "projectSeqList": [ 447461 ]
#
# "lip_sync_illustrated_face_en.mp4" / "mediaSeq": 953999 / "projectSeqList": [ 447492 ]
#
















































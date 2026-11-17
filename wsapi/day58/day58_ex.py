# day58_ex.py
# FastAPI + Perso API 연동 실습: 실제 서비스 호출 전용

'''
============================================================
FastAPI + Perso API — Swagger 실습 안내 (실제 라우터와 일치)
============================================================
[준비]
1. .env에 PERSO_API_KEY=pk_live_... 설정 (.env는 Git 제외)
2. python -m pip install fastapi uvicorn httpx python-dotenv python-multipart
3. uvicorn day58_ex:app --reload
4. http://127.0.0.1:8000/docs 접속 → Try it out → Execute

[공통 조회]
① GET /health               : 로컬 서버와 API 키 설정 여부만 확인
② GET /perso/spaces        : 실제 Space 목록에서 spaceSeq 확인
③ GET /perso/languages     : 지원 언어 및 supportedTtsModels 확인
④ GET /perso/status        : 남은 크레딧 확인 (space_seq 선택 가능)
⑤ GET /perso/queue         : 외부 PUT Queue API로 초기화/조회

[파일 업로드: 한 번의 Swagger 실행으로 3단계 진행]
⑥ POST /perso/upload
   - file: stt_clean_en.wav / kind: audio / space_seq: 실제 Space ID
   - 내부: request_sas() → put_blob() → register_media()
   - 1단계: GET /file/api/upload/sas-token → blobSasUrl
   - 2단계: PUT blobSasUrl (Azure Blob, XP-API-KEY 전송 금지) → 201
   - 3단계: PUT /file/api/upload/audio 또는 /video → seq
   - 최종 응답의 mediaSeq를 후속 생성 요청에 사용
   - 최대 업로드 25MB (실습 서버 자체 제한)

[STT: 실시간 크레딧 소모 가능]
⑦ POST /perso/spaces/{space_seq}/stt?confirm_cost=true
   본문: {"mediaSeq": 실제_ID, "isVideoProject": false,
          "title": "음성 인식 실습"}
   → projectSeqList를 기록
⑧ GET /perso/spaces/{space_seq}/projects/{project_seq}/progress
   → result.progressReason이 Completed인지 확인
   → 5초 이상 간격으로 재조회, Failed이면 failureReason 확인
⑨ GET /perso/spaces/{space_seq}/projects/{project_seq}/stt/script
   → kind=stt를 URL 경로로 지정, originalText 확인
   → cursor_id 첫 요청은 생략, hasNext면 nextCursorId로 재조회

[오디오 분리]
⑩ POST /perso/upload : separation_voice_music_en.wav, kind=audio
⑪ POST /perso/spaces/{space_seq}/separation?confirm_cost=true
   본문: {"mediaSeq": 실제_ID, "isVideoProject": false,
          "title": "음성과 배경음 분리"}
⑫ progress 조회 → Completed 후
   GET /perso/spaces/{space_seq}/projects/{project_seq}/audio-separation/script

[영상 더빙]
⑬ POST /perso/upload : dubbing_presentation_en.mp4, kind=video
⑭ POST /perso/spaces/{space_seq}/dubbing?confirm_cost=true
   본문 예시: {"mediaSeq": 실제_ID, "isVideoProject": true,
     "title": "다국어 더빙", "sourceLanguageCode": "en",
     "targetLanguages": [{"languageCode":"ko","ttsModel":"LINNET_4"}],
     "numberOfSpeakers": 1, "withLipSync": false,
     "preferredSpeedType": "GREEN"}
   → 지원 TTS 모델을 /perso/languages에서 먼저 확인
   → 언어별 projectSeq를 각각 progress 조회

[립싱크: 완료된 영상 더빙 프로젝트 대상]
⑮ POST /perso/spaces/{space_seq}/projects/{project_seq}/lip-sync
   ?confirm_cost=true
   본문: {"preferredSpeedType": "GREEN", "title": "립싱크 실습"}
   → 새 projectSeqList의 각 프로젝트 progress 조회

[결과 확인]
⑯ GET /perso/spaces/{space_seq}/projects/{project_seq}/files
   → 내려받을 수 있는 대상의 true/false 확인
⑰ GET /perso/spaces/{space_seq}/projects/{project_seq}/download
   → target=all / dubbingVideo / lipSyncVideo / voiceAudio 등
   → 상대 경로는 https://portal-media.perso.ai 에 합쳐 반환
   → 다운로드 URL 조회이며 파일 저장 기능은 아님
   → 자막 SRT/VTT는 일반적으로 target=all의 .tar에 포함

[주의]
- 이 파일의 /perso/queue는 FastAPI GET이지만 외부 Perso API는 PUT입니다.
- spaceSeq(공간), mediaSeq(미디어), projectSeq(작업)를 구분합니다.
- 예시 ID를 입력하지 말고 실제 응답값을 사용하세요.
- confirm_cost=true는 이 FastAPI의 안전장치이지 Perso 공식 필드가 아닙니다.
- API 키와 SAS URL을 외부에 공유하거나 로깅하지 마세요.
- 401 인증, 403 권한, 404 ID/경로, 429 과도한 호출을 우선 확인하세요.
============================================================
'''

import os
from urllib.parse import quote, urlsplit, urlunsplit
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from util.print_util import pp, up

load_dotenv()
BASE = 'https://api.perso.ai'  # Perso API 서버
MEDIA = 'https://portal-media.perso.ai'  # 결과 파일 서버
PREFIX = '/video-translator/api/v1'
KEY = os.getenv('PERSO_API_KEY', '').strip()
SPACE_SEQ = 524414  # 기본 작업 공간: 실제 조회한 Space로 변경 가능
MAX_UPLOAD = 25 * 1024 * 1024  # 교육용 업로드 제한: 25MB
app = FastAPI(title='Perso API 통합 실습', version='0.0.2')


# 외부 HTTP 비동기 클라이언트 생성
# follow_redirects=False: SAS 및 외부 API 요청을 다른 서버로 자동 전달하지 않음
def make_client(timeout: float = 60.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout, follow_redirects=False)


# 외부 Perso 응답의 JSON 본문과 HTTP 오류를 일관되게 처리
# 일부 오류가 JSON이 아닐 수 있으므로 문자열로도 안전하게 처리
def parse_response(response: httpx.Response) -> dict:
    try:
        data = response.json() if response.content else {}
    except ValueError:
        data = {'message': response.text[:120]}
    if response.status_code >= 400:
        err = data if isinstance(data, dict) else {'message': str(data)}
        raise HTTPException(
            status_code=response.status_code,
            detail={
                'code': err.get('code', ''),
                'detailCode': err.get('detailCode', ''),
                'message': err.get('message', err.get('detail',
                                                    '외부 API 오류')),
            },
        )
    if not isinstance(data, dict):
        raise HTTPException(502, '예상하지 못한 Perso 응답 형식')
    return data


# Perso 서버에 XP-API-KEY 헤더를 붙여 실제 HTTP 요청 전송
# method: GET/POST/PUT, path: BASE 뒤에 붙는 경로
# params: 쿼리 파라미터, json: JSON 요청 본문
async def call(method: str, path: str, *, params=None, json=None) -> dict:
    if not KEY:
        raise HTTPException(503, 'PERSO_API_KEY 환경 변수가 없습니다')
    try:
        async with make_client() as client:
            response = await client.request(
                method, BASE + path, params=params, json=json,
                headers={'XP-API-KEY': KEY},
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(504, 'Perso API 요청 시간 초과') from exc
    except httpx.RequestError as exc:
        raise HTTPException(502, 'Perso API 연결 오류') from exc
    return parse_response(response)


# Perso 응답에 있는 상대 미디어 경로를 다운로드 URL로 변환
# quote(): 공백·한글 등 특수문자 인코딩, 이미 인코딩된 % 유지
def file_url(path: str) -> str:
    if not isinstance(path, str) or not path.startswith('/'):
        raise HTTPException(502, '미디어 경로가 올바르지 않습니다')
    if path.startswith('//') or '\\' in path or '\x00' in path:
        raise HTTPException(502, '허용되지 않은 미디어 경로')
    return MEDIA + quote(path, safe='/%')


# 프로젝트 생성 결과에서 projectSeq 목록 추출
# 타깃 언어가 여러 개면 여러 projectSeq가 반환될 수 있음
def job_ids(data: dict) -> dict:
    result = data.get('result') or {}
    ids = result.get('startGenerateProjectIdList', [])
    if not isinstance(ids, list) or not ids:
        raise HTTPException(502, 'Perso 응답에 프로젝트 ID가 없습니다')
    return {'projectSeqList': ids,
            'message': '프로젝트별 진행률을 별도로 확인하세요'}


# 모든 생성 작업 공통 함수: 실제 비용 발생 요청은 confirm_cost가 true일 때만 수행
# kind: stt, audio-separation, translate
async def create_job(space_seq: int, kind: str, body: dict,
                     confirm: bool) -> dict:
    if not confirm:
        raise HTTPException(400, '생성에는 confirm_cost=true가 필요합니다')
    result = await call('POST',
                        f'{PREFIX}/projects/spaces/{space_seq}/{kind}',
                        json=body)
    return job_ids(result)


# Pydantic 요청 모델: 미디어의 길이·용량·해상도 등 메타데이터 검증
class MediaMeta(BaseModel):
    spaceSeq: int = Field(gt=0)
    durationMs: int = Field(gt=0)
    originalName: str = Field(min_length=1)
    mediaType: str = Field(pattern='^(audio|video)$')
    extension: str = Field(min_length=2)
    size: int = Field(ge=0)
    width: int | None = None
    height: int | None = None
    sttMode: bool = False


# STT/오디오 분리 생성에 사용할 공통 요청 모델
class CreateJob(BaseModel):
    mediaSeq: int = Field(gt=0)
    isVideoProject: bool = False
    title: str = 'Perso 실습'


# 번역 언어와 해당 언어의 TTS 모델 선택
class TargetLanguage(BaseModel):
    languageCode: str = Field(min_length=2)
    ttsModel: str | None = None


# Dubbing 요청 모델: 원본 언어, 목표 언어, 화자 수, 처리 옵션
class TranslateJob(CreateJob):
    sourceLanguageCode: str = 'auto'
    targetLanguages: list[TargetLanguage] = Field(min_length=1)
    numberOfSpeakers: int = Field(default=1, ge=1)
    withLipSync: bool = False
    preferredSpeedType: str = Field(default='GREEN',
                                    pattern='^(GREEN|RED)$')


# Lip Sync 요청 모델: 속도와 새 프로젝트 제목
class LipSyncJob(BaseModel):
    preferredSpeedType: str = Field(default='GREEN',
                                    pattern='^(GREEN|RED)$')
    title: str = '립싱크 생성'


# 업로드 파일명에서 경로 제거 및 빈 이름 거부
def clean_name(filename: str | None) -> str:
    name = (filename or '').replace('\\', '/').split('/')[-1]
    if not name or name in ('.', '..'):
        raise HTTPException(422, '올바른 파일명이 필요합니다')
    return name


# 최대 25MB까지만 메모리로 읽어 업로드 초과를 감지
async def read_upload(file: UploadFile) -> bytes:
    raw = await file.read(MAX_UPLOAD + 1)
    if not raw:
        raise HTTPException(422, '빈 파일은 업로드할 수 없습니다')
    if len(raw) > MAX_UPLOAD:
        raise HTTPException(413, '업로드 파일은 최대 25MB입니다')
    return raw


# Perso에서 발급한 SAS URL의 안전성을 검사하는 함수
def check_sas_url(sas_url: str) -> None:

    # SAS URL을 구성 요소별로 분리
    parsed = urlsplit(sas_url)

    # URL의 호스트 이름 추출
    host = (parsed.hostname or '').lower()

    # 실제 Perso API에서 확인된 호스트를 허용 목록에 추가
    allowed = (
        host == 'perso-studio-file.perso.ai'
        or host == 'perso-saas-file-frontdoor.perso.ai'
        or host.endswith('.blob.core.windows.net')
    )

    # HTTPS가 아니면 업로드 차단
    if parsed.scheme != 'https':
        raise HTTPException(502, 'SAS URL은 HTTPS여야 합니다')

    # 허용된 호스트가 아니면 업로드 차단
    if not allowed:
        raise HTTPException(
            502,
            f'허용되지 않은 SAS 호스트: {host}'
        )

    # SAS 서명 Query가 없으면 업로드 차단
    if not parsed.query:
        raise HTTPException(502, 'SAS 서명 Query가 없습니다')

    # URL에 사용자 이름, 암호, 별도 포트가 있으면 차단
    if parsed.username or parsed.password or parsed.port:
        raise HTTPException(502, 'SAS URL 호스트 정보가 잘못되었습니다')


# 업로드 1단계: Perso에서 30분 유효한 blobSasUrl 발급
# params를 이용하면 한글·공백 파일명은 httpx가 URL 인코딩
async def request_sas(file_name: str) -> str:
    data = await call('GET', '/file/api/upload/sas-token',
                      params={'fileName': file_name})
    sas_url = data.get('blobSasUrl')
    if not isinstance(sas_url, str):
        raise HTTPException(502, 'Perso 응답에 blobSasUrl이 없습니다')
    check_sas_url(sas_url)
    return sas_url


# 업로드 2단계: SAS가 가진 인증권한으로 Azure에 파일 바이너리 PUT
# XP-API-KEY는 전달하지 않으며 Azure가 반환한 오류 코드를 분석
async def put_blob(sas_url: str, raw: bytes) -> int:
    check_sas_url(sas_url)
    try:
        async with make_client(120.0) as client:
            response = await client.put(
                sas_url, content=raw,
                headers={'x-ms-blob-type': 'BlockBlob',
                         'Content-Type': 'application/octet-stream'},
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(504, 'Azure 업로드 시간 초과') from exc
    except httpx.RequestError as exc:
        raise HTTPException(502, 'Azure 업로드 연결 오류') from exc
    if response.status_code != 201:
        # x-ms-error-code는 서명/토큰을 포함하지 않는 Azure 오류 식별자
        error_code = response.headers.get('x-ms-error-code', 'unknown')
        raise HTTPException(
            502, detail={'message': 'Azure Blob 업로드 실패',
                         'upstreamStatus': response.status_code,
                         'azureErrorCode': error_code}
        )
    return response.status_code


# 업로드 3단계: 등록 요청으로 실제 mediaSeq 취득
# SAS URL 서명 파라미터는 등록 전에 제거하여 저장 경로 안정화
async def register_media(space_seq: int, kind: str, sas_url: str,
                         file_name: str) -> int:
    check_sas_url(sas_url)
    if kind not in ('audio', 'video'):
        raise HTTPException(422, 'kind는 audio 또는 video')
    parts = urlsplit(sas_url)
    stable_url = urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))
    data = await call('PUT', f'/file/api/upload/{kind}', json={
        'spaceSeq': space_seq, 'fileUrl': stable_url,
        'fileName': file_name,
    })
    media_seq = data.get('seq')
    if not isinstance(media_seq, int):
        raise HTTPException(502, 'Perso 응답에 mediaSeq가 없습니다')
    return media_seq


# 라우터: GET /health — 로컬 API 키 설정만 확인, Perso 서버는 호출하지 않음
@app.get('/health')
def health():
    return {'ok': True, 'provider': 'Perso',
            'apiKeyConfigured': bool(KEY)}


# 라우터: GET /perso/spaces — 사용자가 접근 가능한 Space 목록
@app.get('/perso/spaces')
async def get_spaces():
    spaces = await call('GET', '/portal/api/v1/spaces')
    for item in spaces.get('result', []):
        pp(item.get('spaceSeq'), item.get('memberRole'))
    return spaces


# 라우터: GET /perso/languages — 언어별 지원 TTS 모델 확인
@app.get('/perso/languages')
async def get_languages():
    languages = await call('GET', f'{PREFIX}/languages')
    for lang in languages.get('languages', []):
        pp(lang.get('code'), lang.get('supportedTtsModels'))
    return languages


# 라우터: GET /perso/status — 실제 계정의 잔여 크레딧 확인
# space_seq를 생략하면 SPACE_SEQ를 기본값으로 사용
@app.get('/perso/status')
async def get_status(space_seq: int = Query(SPACE_SEQ, gt=0)):
    return await call('GET',
                      f'{PREFIX}/projects/spaces/{space_seq}/plan/status')


# 라우터: GET /perso/queue — 외부 Perso의 PUT Queue API 호출
# 외부 PUT은 큐가 없으면 초기화, 있으면 상태 조회
@app.get('/perso/queue')
async def queue(space_seq: int = Query(SPACE_SEQ, gt=0)):
    return await call('PUT',
                      f'{PREFIX}/projects/spaces/{space_seq}/queue')

# 라우터: POST /perso/media/validate - 업로드 전 메타데이터만 검사
@app.post('/perso/media/validate')
async def validate_media(meta: MediaMeta):
    return await call(
        'POST',
        '/file/api/v1/media/validate',
        json=meta.model_dump(exclude_none=True) # None 배제
    )

# 단계별 오류를 일관되게 반환하는 함수
# SAS 주소나 API 키 등의 인증 정보를 외부 응답에 포함하지 않음
def stage_error(stage: str, exc: HTTPException) -> HTTPException:
    detail = exc.detail
    if isinstance(detail, dict):
        # 상위 API의 응답에서 진단에 필요한 필드만 사용
        upstream = detail.get('upstreamStatus')
        code = detail.get('azureErrorCode') or detail.get('code')
        message = detail.get('message', '외부 API 요청 실패')
    else:
        upstream = None
        code = None
        message = str(detail)
    return HTTPException(
        status_code=exc.status_code,
        detail={'stage': stage, 'message': message,
                'upstreamStatus': upstream, 'errorCode': code}
    )


# 라우터: POST /perso/upload — SAS 발급 → Azure 업로드 → Perso 등록
# 정상 수행 시 mediaSeq를 반환하며, 실패하면 stage를 함께 제공
@app.post('/perso/upload')
async def upload_all_in_one(
    file: UploadFile = File(...),
    kind: str = Query('audio', pattern='^(audio|video)$'),
    space_seq: int = Query(SPACE_SEQ, gt=0)
):
    file_name = clean_name(file.filename)
    raw = await read_upload(file)
    try:
        sas_url = await request_sas(file_name)
    except HTTPException as exc:
        raise stage_error('sas', exc) from exc
    try:
        azure_status = await put_blob(sas_url, raw)
    except HTTPException as exc:
        raise stage_error('azure_upload', exc) from exc
    try:
        media_seq = await register_media(
            space_seq, kind, sas_url, file_name
        )
    except HTTPException as exc:
        raise stage_error('perso_register', exc) from exc
    return {
        'mediaSeq': media_seq,
        'spaceSeq': space_seq,
        'kind': kind,
        'fileName': file_name,
        'size': len(raw),
        'azureHttpStatus': azure_status,
        'message': 'Perso 파일 등록 완료'
    }

"""FastAPI 라우터 — HTTP 요청 입출력만 처리합니다."""
from pathlib import Path
import re
from uuid import uuid4
from fastapi import APIRouter,UploadFile,File,Form,Query,HTTPException
from backend.core.config import get_settings
from backend.core.errors import PersoError,api_error
from backend.integrations.perso_client import PersoClient,public_media_url,result_data
from backend.services import job_service as svc
from backend.schemas.jobs import JobCreate,LipSyncCreate
from backend.repositories import job_repository as repo

router=APIRouter(prefix="/api",tags=["Perso Studio"])
ALLOWED={"audio":{".wav",".mp3"},"video":{".mp4",".mov",".webm"}}
TARGETS={"all","dubbingVideo","lipSyncVideo","voiceAudio","originalVoiceAudio",
    "backgroundAudio","voicewithBackgroundAudio","originalVoiceSpeakers",
    "speakerSegmentExcel","speakerSegmentWithTranslationExcel","scriptTimestamps",
    "originalSubBackground","audioScript"}

@router.get("/health")
async def health():
    return {"ok":True,"service":"Perso Integrated Studio"}

@router.get("/spaces")
async def spaces():
    try:return await PersoClient().spaces()
    except PersoError as exc:raise api_error(exc) from exc

@router.get("/languages")
async def languages():
    try:return await PersoClient().languages()
    except PersoError as exc:raise api_error(exc) from exc

@router.post("/media/upload")
async def upload(file:UploadFile=File(...),space_seq:int=Form(...),kind:str=Form(...)):
    if space_seq<=0:raise HTTPException(422,"space_seq는 양수여야 합니다")
    if kind not in ALLOWED:raise HTTPException(422,"kind는 audio 또는 video")
    name=Path(file.filename or "").name
    ext=Path(name).suffix.lower()
    if ext not in ALLOWED[kind]:raise HTTPException(422,f"지원하지 않는 확장자: {ext}")
    max_bytes=get_settings().max_upload_mb*1024*1024
    data=await file.read(max_bytes+1)
    if not data or len(data)>max_bytes:
        raise HTTPException(413,"업로드가 비어 있거나 설정된 용량을 초과했습니다")
    # 사용자 파일명을 외부에 그대로 전달하지 않고 ASCII 안전명으로 변환합니다.
    safe_name=f"studio_{uuid4().hex}{ext}"
    try:
        result=await svc.upload_and_save(space_seq,kind,safe_name,data)
        result["originalFilename"]=name
        return result
    except PersoError as exc:raise api_error(exc) from exc

@router.post("/jobs")
async def start_job(req:JobCreate):
    try:return await svc.create_job(req)
    except PersoError as exc:raise api_error(exc) from exc

@router.post("/jobs/lip-sync")
async def lip_sync(req:LipSyncCreate):
    try:return await svc.create_lip_sync(req)
    except PersoError as exc:raise api_error(exc) from exc

@router.get("/jobs")
async def jobs(space_seq:int|None=None,limit:int=Query(100,ge=1,le=200)):
    return await repo.list_jobs(space_seq,limit)

@router.get("/jobs/{space_seq}/{project_seq}")
async def job_detail(space_seq:int,project_seq:int):
    job=await repo.get_job(space_seq,project_seq)
    if job is None:raise HTTPException(404,"작업 기록이 없습니다")
    return job

@router.get("/jobs/{space_seq}/{project_seq}/progress")
async def progress(space_seq:int,project_seq:int):
    try:return await svc.refresh_progress(space_seq,project_seq)
    except PersoError as exc:raise api_error(exc) from exc

@router.get("/jobs/{space_seq}/{project_seq}/script")
async def script(space_seq:int,project_seq:int,cursor_id:int|None=None):
    job=await repo.get_job(space_seq,project_seq)
    if not job:raise HTTPException(404,"DB에서 작업을 찾을 수 없습니다")
    kind=job["job_type"]
    if kind not in ("stt","audio-separation","dubbing"):
        raise HTTPException(422,"해당 작업은 스크립트를 지원하지 않습니다")
    try:return await PersoClient().script(space_seq,project_seq,kind,cursor_id)
    except PersoError as exc:raise api_error(exc) from exc

@router.get("/jobs/{space_seq}/{project_seq}/files")
async def files(space_seq:int,project_seq:int):
    if not await repo.get_job(space_seq,project_seq):raise HTTPException(404,"작업이 없습니다")
    try:return await PersoClient().files(space_seq,project_seq)
    except PersoError as exc:raise api_error(exc) from exc

@router.get("/jobs/{space_seq}/{project_seq}/download")
async def download(space_seq:int,project_seq:int,target:str="all"):
    if target not in TARGETS:raise HTTPException(422,"지원하지 않는 다운로드 대상")
    if not await repo.get_job(space_seq,project_seq):raise HTTPException(404,"작업이 없습니다")
    try:data=await PersoClient().download(space_seq,project_seq,target)
    except PersoError as exc:raise api_error(exc) from exc
    urls={}
    # 파일 링크를 다운로드 API가 내려준 결과에서만 취합합니다.
    def collect(node):
        if isinstance(node,dict):
            for key,val in node.items():
                if isinstance(val,dict):collect(val)
                elif isinstance(val,str) and val.startswith("/") and not val.startswith("//"):
                    urls[key]=public_media_url(val)
    collect(result_data(data))
    return {"target":target,"urls":urls,
            "note":"SRT 등 자막은 target=all 아카이브 안에 포함될 수 있습니다"}

"""Service Layer — 업무 규칙과 처리 순서를 담당합니다."""
from fastapi import HTTPException
from backend.schemas.jobs import JobCreate,LipSyncCreate
from backend.integrations.perso_client import PersoClient,project_ids,result_data
from backend.repositories import job_repository as repo

async def upload_and_save(space_seq:int,kind:str,filename:str,data:bytes):
    # 외부 API에 실제 업로드한 후 그 결과 ID만 DB에 저장합니다.
    out=await PersoClient().upload(space_seq,kind,filename,data)
    await repo.store_media(space_seq,out["mediaSeq"],kind,filename,len(data))
    await repo.audit("UPLOAD","미디어 업로드 등록 완료",space_seq)
    return out

async def create_job(req:JobCreate):
    if not req.confirm_cost:
        raise HTTPException(400,"실제 생성 비용 확인이 필요합니다 (confirm_cost=true)")
    # 사용자가 임의의 mediaSeq로 다른 Space의 미디어를 참조하지 못하게 제한합니다.
    asset=await repo.media_for_space(req.space_seq,req.media_seq)
    if asset is None:
        raise HTTPException(404,"현재 데이터베이스에 업로드한 mediaSeq가 없습니다")
    if (asset["kind"]=="video")!=req.is_video_project:
        raise HTTPException(422,"업로드 미디어 유형과 is_video_project가 다릅니다")
    if req.kind=="dubbing" and req.target_language_code==req.source_language_code:
        raise HTTPException(422,"원본 언어와 대상 언어를 다르게 설정하세요")
    body={"mediaSeq":req.media_seq,"isVideoProject":req.is_video_project}
    if req.title:body["title"]=req.title
    if req.kind=="dubbing":
        body.update({"sourceLanguageCode":req.source_language_code or "auto",
          "targetLanguages":[{"languageCode":req.target_language_code,"ttsModel":req.tts_model}],
          "numberOfSpeakers":req.number_of_speakers,
          "preferredSpeedType":req.preferred_speed_type,"withLipSync":req.with_lip_sync})
    client=PersoClient()
    # Queue 초기화는 멱등성 확인이 가능하므로 생성 요청 전에 실행합니다.
    await client.init_queue(req.space_seq)
    response=await client.start(req.space_seq,req.kind,body)
    ids=project_ids(response)
    if not ids:
        raise HTTPException(502,"생성 응답에 projectSeq 목록이 없습니다. Perso 작업 내역을 확인하세요")
    await repo.save_jobs(req.space_seq,ids,req.kind,req.media_seq,req.title)
    await repo.audit("JOB_CREATED",f"{req.kind} 프로젝트 생성 완료: {ids}",req.space_seq)
    return {"projectSeqList":ids,"spaceSeq":req.space_seq,"jobType":req.kind}

async def create_lip_sync(req:LipSyncCreate):
    if not req.confirm_cost:
        raise HTTPException(400,"실제 립싱크 생성 비용 확인이 필요합니다")
    parent=await repo.get_job(req.space_seq,req.parent_project_seq)
    if parent is None or parent["job_type"]!="dubbing":
        raise HTTPException(404,"해당 Space에 저장된 더빙 프로젝트가 없습니다")
    if parent["status"].lower()!="completed":
        raise HTTPException(409,"더빙 작업이 Completed 상태여야 합니다. 먼저 진행 상태를 갱신하세요")
    body={"preferredSpeedType":req.preferred_speed_type}
    if req.title:body["title"]=req.title
    response=await PersoClient().start_lip_sync(req.space_seq,req.parent_project_seq,body)
    ids=project_ids(response)
    if not ids:
        raise HTTPException(502,"립싱크 응답에 projectSeq 목록이 없습니다")
    await repo.save_jobs(req.space_seq,ids,"lip-sync",None,req.title,req.parent_project_seq)
    await repo.audit("LIP_SYNC_CREATED",f"립싱크 생성: {ids}",req.space_seq,req.parent_project_seq)
    return {"projectSeqList":ids,"spaceSeq":req.space_seq,"jobType":"lip-sync"}

async def refresh_progress(space_seq:int,project_seq:int):
    job=await repo.get_job(space_seq,project_seq)
    if job is None:
        raise HTTPException(404,"해당 프로젝트가 DB에 없습니다")
    try:
        response=await PersoClient().progress(space_seq,project_seq)
    except Exception as exc:
        # 네트워크 장애로 기존 성공 상태를 덮어쓰지 않습니다.
        await repo.mark_error(space_seq,project_seq,str(exc))
        raise
    root=result_data(response)
    if not isinstance(root,dict):root={}
    status=str(root.get("progressReason") or root.get("status") or "Unknown")
    progress=root.get("progress")
    try:progress=float(progress) if progress is not None else None
    except (TypeError,ValueError):progress=None
    await repo.update_status(space_seq,project_seq,status,progress,response)
    return {"spaceSeq":space_seq,"projectSeq":project_seq,"status":status,
            "progress":progress,"persoResponse":response}

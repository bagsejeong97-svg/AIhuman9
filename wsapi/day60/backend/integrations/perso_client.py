"""Perso API Client — 이전 day58_ex.py의 HTTP 로직을 계층화한 구현입니다."""
from __future__ import annotations
from urllib.parse import urlparse, urlunparse, quote
import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import httpx
from backend.core.config import get_settings
from backend.core.errors import PersoError

BASE = "https://api.perso.ai"
MEDIA_BASE = "https://portal-media.perso.ai"
PREFIX = "/video-translator/api/v1"


def result_data(data):
    """result 래퍼가 있는 응답과 없는 응답 모두 처리합니다."""
    if isinstance(data,dict) and "result" in data:
        return data["result"]
    return data


def project_ids(data)->list[int]:
    """상태 생성 응답에서 실제 projectSeq 목록을 뽑습니다."""
    root=result_data(data)
    if not isinstance(root,dict):
        return []
    ids=root.get("startGenerateProjectIdList") or root.get("projectSeqList") or []
    return [int(x) for x in ids]


def public_media_url(value:str)->str:
    """Perso 상대 미디어 경로에 정해진 호스트를 붙입니다."""
    if not value.startswith("/") or value.startswith("//"):
        raise ValueError("외부 미디어 URL 형식이 올바르지 않습니다")
    return MEDIA_BASE + quote(value,safe="/%-_.~")


# 백오프 대상: 사용량 제한 및 일시적인 서버 장애만 선택합니다.
RETRYABLE_CODES = {429, 500, 502, 503, 504}
MAX_RETRY_ATTEMPTS = 5  # 최초 요청 포함, 최대 5회 시도
MAX_BACKOFF_SECONDS = 60.0


def retry_after_seconds(value: str | None) -> float | None:
    """Retry-After를 초 단위 또는 HTTP-date로 해석합니다."""
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            target = parsedate_to_datetime(value)
            if target.tzinfo is None:
                target = target.replace(tzinfo=timezone.utc)
            return max(0.0, (target - datetime.now(timezone.utc)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None


def backoff_seconds(attempt: int, retry_after: str | None = None) -> float:
    """5, 10, 20, 40초를 기본으로 하되, Retry-After가 있으면 우선합니다.

    Retry-After가 최대 60초보다 큰 경우에는 안전하게 실패시켜야 하므로
    호출부에서 별도 확인합니다. 이 함수는 대기 시간 계산에만 집중합니다.
    """
    header = retry_after_seconds(retry_after)
    if header is not None:
        return min(MAX_BACKOFF_SECONDS, header)
    return min(MAX_BACKOFF_SECONDS, 5.0 * (2 ** (attempt - 1)))


class PersoClient:
    def __init__(self, transport=None, sleep=None):
        self.key = get_settings().perso_api_key
        self.transport = transport
        # 테스트에서는 실제 대기 없이 호출 시간을 검증할 수 있도록 주입합니다.
        self.sleep = sleep or asyncio.sleep

    async def call(self, method: str, path: str, *, params=None, json=None):
        """읽기 전용 GET만 제한적으로 재시도합니다.

        POST/PUT 생성·업로드는 중복 생성 또는 중복 과금을 방지하기 위해
        네트워크 타임아웃이 발생해도 자동 재시도하지 않습니다.
        """
        if not self.key or self.key.endswith("REPLACE_ME"):
            raise PersoError(503, "PERSO_API_KEY를 먼저 설정하세요")
        if not path.startswith("/"):
            raise PersoError(500, "유효하지 않은 API 경로")

        safe_retry = method.upper() == "GET"
        attempts = MAX_RETRY_ATTEMPTS if safe_retry else 1
        async with httpx.AsyncClient(timeout=60, transport=self.transport, follow_redirects=False) as client:
            for attempt in range(1, attempts + 1):
                try:
                    res = await client.request(method, BASE + path,
                        headers={"XP-API-KEY": self.key}, params=params, json=json)
                except (httpx.TimeoutException, httpx.RequestError) as exc:
                    if safe_retry and attempt < attempts:
                        await self.sleep(backoff_seconds(attempt))
                        continue
                    code = 504 if isinstance(exc, httpx.TimeoutException) else 503
                    raise PersoError(code, "Perso API 조회 시간 초과" if code == 504
                                     else "Perso API 네트워크 연결 실패") from exc

                if res.status_code in RETRYABLE_CODES and safe_retry and attempt < attempts:
                    header = res.headers.get("Retry-After") if res.status_code == 429 else None
                    parsed = retry_after_seconds(header)
                    # 공급자가 60초보다 긴 대기를 명시하면 빠르게 실패하고
                    # 나중에 사용자가 다시 조회하도록 합니다.
                    if parsed is not None and parsed > MAX_BACKOFF_SECONDS:
                        raise PersoError(429, "Perso 서버의 Retry-After가 60초를 초과합니다. 나중에 조회하세요")
                    await self.sleep(backoff_seconds(attempt, header))
                    continue

                if res.status_code >= 400:
                    # 오류 본문은 길이를 제한하고 SAS/인증 정보를 노출하지 않습니다.
                    raise PersoError(res.status_code, f"Perso HTTP {res.status_code}: 요청에 실패했습니다")
                try:
                    return res.json() if res.content else {}
                except ValueError as exc:
                    raise PersoError(502, "Perso API의 JSON 형식이 올바르지 않습니다") from exc
        raise PersoError(503, "Perso API 재시도 횟수를 초과했습니다")

    async def upload(self,space_seq:int,kind:str,filename:str,contents:bytes):
        """1) SAS 발급 2) Azure Blob PUT 3) Perso 미디어 등록."""
        sas=await self.call("GET","/file/api/upload/sas-token",params={"fileName":filename})
        token=result_data(sas)
        sas_url=token.get("blobSasUrl") if isinstance(token,dict) else None
        if not sas_url:
            raise PersoError(502,"Perso SAS 응답에 blobSasUrl이 없습니다")
        parsed=urlparse(sas_url)
        host=(parsed.hostname or "").lower()
        # 업로드용 SAS URL은 반드시 Perso 또는 Azure Blob의 HTTPS 호스트여야 합니다.
        if parsed.scheme!="https" or not (host.endswith(".perso.ai") or host.endswith(".blob.core.windows.net")):
            raise PersoError(502,"안전하지 않은 SAS 업로드 호스트입니다")
        try:
            async with httpx.AsyncClient(timeout=180,transport=self.transport,follow_redirects=False) as client:
                res=await client.put(sas_url,content=contents,headers={"x-ms-blob-type":"BlockBlob"})
            if res.status_code not in (200,201,202):
                raise PersoError(502,f"Blob 업로드 실패 ({res.status_code})")
        except httpx.RequestError as exc:
            raise PersoError(503,"Blob 업로드 중 네트워크 오류") from exc
        # SAS 서명은 재사용/저장하지 않도록 쿼리 문자열을 제거합니다.
        file_url=urlunparse(parsed._replace(query="",fragment=""))
        reg=await self.call("PUT",f"/file/api/upload/{kind}",json={
            "spaceSeq":space_seq,"fileUrl":file_url,"fileName":filename,"sttMode":kind=="audio"})
        registered=result_data(reg)
        media_seq=registered.get("seq") if isinstance(registered,dict) else None
        if media_seq is None:
            raise PersoError(502,"업로드 등록 응답에 seq가 없습니다")
        return {"mediaSeq":int(media_seq),"kind":kind,"spaceSeq":space_seq,"fileName":filename}

    async def spaces(self):
        return await self.call("GET","/portal/api/v1/spaces")

    async def languages(self):
        return await self.call("GET",f"{PREFIX}/languages")

    async def init_queue(self,space_seq:int):
        return await self.call("PUT",f"{PREFIX}/projects/spaces/{space_seq}/queue")

    async def start(self,space_seq:int,job_type:str,body:dict):
        path={"stt":"stt","audio-separation":"audio-separation","dubbing":"translate"}[job_type]
        return await self.call("POST",f"{PREFIX}/projects/spaces/{space_seq}/{path}",json=body)

    async def start_lip_sync(self,space_seq:int,project_seq:int,body:dict):
        return await self.call("POST",f"{PREFIX}/projects/{project_seq}/spaces/{space_seq}/lip-sync",json=body)

    async def progress(self,space_seq:int,project_seq:int):
        return await self.call("GET",f"{PREFIX}/projects/{project_seq}/space/{space_seq}/progress")

    async def script(self,space_seq:int,project_seq:int,kind:str,cursor_id:int|None=None):
        sub={"stt":"stt/script","audio-separation":"audio-separation/script","dubbing":"script"}[kind]
        params={"size":100}
        if cursor_id is not None:params["cursorId"]=cursor_id
        return await self.call("GET",f"{PREFIX}/projects/{project_seq}/spaces/{space_seq}/{sub}",params=params)

    async def files(self,space_seq:int,project_seq:int):
        return await self.call("GET",f"{PREFIX}/projects/{project_seq}/spaces/{space_seq}/download-info")

    async def download(self,space_seq:int,project_seq:int,target:str):
        return await self.call("GET",f"{PREFIX}/projects/{project_seq}/spaces/{space_seq}/download",params={"target":target})

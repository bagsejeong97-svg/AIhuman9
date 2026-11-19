"""httpx MockTransport 사용: 외부 API 요청 경로/인증/파싱을 독립 테스트."""
import asyncio
import httpx
from backend.integrations.perso_client import PersoClient

def test_space_request_monkeypatch(monkeypatch):
    monkeypatch.setenv("PERSO_API_KEY","pk_live_TEST_KEY")
    calls=[]
    def handler(request):
        calls.append((request.url.path,request.headers.get("XP-API-KEY")))
        return httpx.Response(200,json={"result":[{"spaceSeq":524414}]})
    async def run():
        return await PersoClient(transport=httpx.MockTransport(handler)).spaces()
    data=asyncio.run(run())
    assert data["result"][0]["spaceSeq"]==524414
    assert calls==[("/portal/api/v1/spaces","pk_live_TEST_KEY")]

"""429·5xx·네트워크 장애 백오프, 비멱등 POST 비재시도 테스트."""
import asyncio
import httpx
import pytest
from backend.integrations.perso_client import PersoClient, backoff_seconds, retry_after_seconds
from backend.core.errors import PersoError


def test_backoff_schedule():
    assert [backoff_seconds(i) for i in range(1, 6)] == [5, 10, 20, 40, 60]
    assert backoff_seconds(2, "17") == 17
    assert retry_after_seconds("0") == 0


def test_rate_limit_uses_retry_after(monkeypatch):
    monkeypatch.setenv("PERSO_API_KEY", "pk_live_TEST_KEY")
    calls, waits = [], []
    def handler(req):
        calls.append(req.method)
        if len(calls) == 1:
            return httpx.Response(429, headers={"Retry-After": "7"})
        return httpx.Response(200, json={"result": {"progressReason": "Completed"}})
    async def fake_sleep(sec):
        waits.append(sec)
    async def run():
        return await PersoClient(httpx.MockTransport(handler), fake_sleep).progress(1, 2)
    assert asyncio.run(run())["result"]["progressReason"] == "Completed"
    assert calls == ["GET", "GET"]
    assert waits == [7]


def test_503_retries_exponentially(monkeypatch):
    monkeypatch.setenv("PERSO_API_KEY", "pk_live_TEST_KEY")
    waits, count = [], [0]
    def handler(req):
        count[0] += 1
        return httpx.Response(503) if count[0] < 4 else httpx.Response(200, json={"ok": True})
    async def fake_sleep(sec): waits.append(sec)
    async def run():
        return await PersoClient(httpx.MockTransport(handler), fake_sleep).spaces()
    assert asyncio.run(run()) == {"ok": True}
    assert waits == [5, 10, 20]


def test_post_not_retried(monkeypatch):
    monkeypatch.setenv("PERSO_API_KEY", "pk_live_TEST_KEY")
    calls = [0]
    def handler(req):
        calls[0] += 1
        return httpx.Response(503)
    async def run():
        return await PersoClient(httpx.MockTransport(handler)).start(1, "stt", {"mediaSeq": 2})
    with pytest.raises(PersoError): asyncio.run(run())
    assert calls == [1]


def test_retry_attempt_cap(monkeypatch):
    monkeypatch.setenv("PERSO_API_KEY", "pk_live_TEST_KEY")
    count, waits = [0], []
    def handler(req):
        count[0] += 1
        return httpx.Response(429)
    async def fake_sleep(sec): waits.append(sec)
    async def run():
        return await PersoClient(httpx.MockTransport(handler), fake_sleep).progress(1, 2)
    with pytest.raises(PersoError) as exc: asyncio.run(run())
    assert exc.value.status_code == 429
    assert count == [5] and waits == [5, 10, 20, 40]


def test_nonretryable_400(monkeypatch):
    monkeypatch.setenv("PERSO_API_KEY", "pk_live_TEST_KEY")
    count = [0]
    def handler(req):
        count[0] += 1
        return httpx.Response(400)
    async def run():
        return await PersoClient(httpx.MockTransport(handler)).progress(1, 2)
    with pytest.raises(PersoError): asyncio.run(run())
    assert count == [1]

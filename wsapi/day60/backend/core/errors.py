"""외부 API와 DB 오류를 HTTP 오류로 안전하게 번역합니다."""
from fastapi import HTTPException

class PersoError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

def api_error(exc: PersoError) -> HTTPException:
    # 외부 서버의 예기치 않은 5xx는 우리 서비스의 502로 표시합니다.
    status = exc.status_code if 400 <= exc.status_code < 500 else 502
    return HTTPException(status_code=status, detail=exc.detail)

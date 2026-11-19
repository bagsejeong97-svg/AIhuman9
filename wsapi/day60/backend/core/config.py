"""환경변수 로딩 — API 비밀키는 서버에서만 읽습니다."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    perso_api_key: str = ""
    database_url: str = ""
    perso_space_seq: int | None = None
    max_upload_mb: int = 50
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
# 테스트는 get_settings.cache_clear()로 환경변수 캐시를 초기화할 수 있습니다.
def get_settings() -> Settings:
    return Settings()

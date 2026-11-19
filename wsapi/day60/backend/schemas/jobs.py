"""Pydantic 데이터 검증 — 프런트엔드 입력값을 신뢰하지 않습니다."""
from typing import Literal
from pydantic import BaseModel, Field







class JobCreate(BaseModel):
    space_seq:int=Field(gt=0)
    media_seq:int=Field(gt=0)
    kind:Literal["stt","audio-separation","dubbing"]
    is_video_project:bool=False
    title:str=Field(default="",max_length=150)
    source_language_code:str="auto"
    target_language_code:str="ko"
    tts_model:str="LINNET_4"
    number_of_speakers:int=Field(default=1,ge=1,le=20)
    preferred_speed_type:Literal["GREEN","RED"]="GREEN"
    with_lip_sync:bool=False
    confirm_cost:bool=False

class LipSyncCreate(BaseModel):
    space_seq:int=Field(gt=0)
    parent_project_seq:int=Field(gt=0)
    title:str=Field(default="",max_length=150)
    preferred_speed_type:Literal["GREEN","RED"]="GREEN"
    confirm_cost:bool=False

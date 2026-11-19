"""외부 API 호출 없이 응답 파싱 로직을 검증합니다."""
from backend.integrations.perso_client import project_ids,result_data,public_media_url

def test_project_ids_result_wrapper():
    assert project_ids({"result":{"startGenerateProjectIdList":[101,102]}})==[101,102]

def test_project_ids_direct_wrapper():
    assert project_ids({"startGenerateProjectIdList":[11]})==[11]

def test_result_spaces():
    assert result_data({"result":[{"spaceSeq":524414}]})==[{"spaceSeq":524414}]

def test_safe_relative_media_url():
    assert public_media_url("/perso-storage/a.mp4")=="https://portal-media.perso.ai/perso-storage/a.mp4"

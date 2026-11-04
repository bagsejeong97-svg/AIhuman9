# day30_logic.py
# DB외 UI 사이의 데이터 검증, 가공, 업무 로직 담담

import pandas as pd

# DB 함수들 import
from day30_db import (
    create_table,
    has_database_url,
    save_voice_data,
    load_voice_data,
    update_voice_data,
    delete_voice_data
)

def has_database_url_logic():
    return has_database_url()

def create_table_logic():
    return create_table()

# 화면과 데이터 검증에서 공통으로 사용할 언어 목록
LANGUAGES = ['ko','en','ja','zh']

# 등록 데이터 검증 함수
def validate_insert_data(speaker, transcript):
    if not speaker.strip():
        return '화자명을 입력하세요.'
    if not transcript.strip():
        return '녹음 문장을 입력하세요.'
    return None

# 수정 데이터 검증 함수
def validate_update_data(transcript):
    if not transcript.strip():
        return '수정할 녹음 문장을 입력하세요.'
    return None

# 등록 함수
def register_voice_data(speaker, transcript, language, file_name):
    return save_voice_data(
        speaker.strip(),
        transcript.strip(),
        language.strip(),
        file_name.strip()
    )

# 검색 조회 함수
def search_voice_data(keyword = ''):
    rows = load_voice_data(keyword)
    # UI 쪽에서 DATAFRAME 보여주도록 데이터 프레임으로 변환해서 리턴
    return to_dataframe(rows)

# 수정 함수
def modify_voice_data(data_id, transcript, language):
    return update_voice_data(
        int(data_id),
        transcript.strip(),
        language,
    )

# 삭제 함수
def remove_voice_data(data_id):
    return delete_voice_data(int(data_id))

# DB 조회 결과를 데이터 프레임을 변환하는 함수
def to_dataframe(rows):
    if not rows: # 조회 결과행이 없다면
        return pd.DataFrame(
            columns=['ID','화자','언어','파일명','등록일']
        )
    df = pd.DataFrame(rows)
    return df.rename( # 컬럼명 변경 후 리턴
        columns={
            'id': 'ID',
            'speaker':'화자',
            'transcript':'문장',
            'language':'언어',
            'file_name':'파일명',
            'created_at':'등록일'
        }
    )


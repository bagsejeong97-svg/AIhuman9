# day30_ui.py
# Streamlit 화면 구성 및 사용자 입력/출력 담당
import psycopg
import streamlit as st
from day30_logic import (
    has_database_url_logic,
    create_table_logic,
    LANGUAGES,
    modify_voice_data,
    register_voice_data,
    remove_voice_data,
    search_voice_data,
    validate_insert_data,
    validate_update_data
)

# 입력폼 함수
def show_insert_form():
    st.subheader("음성 메타데이터 등록")
    with st.form('voice_form',clear_on_submit=True):
        speaker = st.text_input(
            '화자명',
            max_chars=50,
            placeholder='예: 민준'
        )
        transcript = st.text_area(
            '녹음 문장',
            placeholder='녹음된 문장을 입력하세요.'
        )
        language = st.selectbox(
            '언어',
            LANGUAGES,
        )
        file_name = st.text_input(
            '파일명',
            placeholder='예: voice_001.wav'
        )
        submitted = st.form_submit_button('저장')

    # 저장 버튼을 누르지 않으면
    if not submitted:
        return

    # 입력값 검증을 logic 계층에 위임(delegation)
    error_message = validate_insert_data(speaker,transcript)

    if error_message:
        st.warning(error_message)
        return

    try:
        # 등록 처리는 logic에서 하고 결과를 저장
        new_id = register_voice_data(speaker,transcript,language,file_name)
    except psycopg.Error:
        st.error('데이터베이스 저장중 문제가 발생했습니다.')

# 데이터 화면 출력 함수
def show_data_list():
    st.subheader('음성 메타데이터 조회')
    keyword = st.text_input(
        '화자 검색',
        placeholder='화자명의 일부를 입력하세요'
    )
    try:
        df = search_voice_data(keyword)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    except psycopg.Error:
        st.error('데이터 베이스 조회중 문제가 발생했습니다.')

# 수정 / 삭제 화면 출력 함수
def show_update_delete():
    st.subheader('수정 / 삭제')
    data_id = st.number_input(
        '대상 ID',
        min_value=1,
        step=1,
    )
    transcript = st.text_area(
        '수정할 문장',
        key='update_transcript'
    )
    language = st.selectbox(
        '수정할 언어',
        LANGUAGES,
        key='update_language'
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button('수정',use_container_width=True):
            error_message = validate_update_data(transcript)
            if error_message:
                st.warning(error_message)
            else:
                try:
                    count = modify_voice_data(data_id,transcript,language)
                    if count:
                        st.success('수정했습니다.')
                    else:
                        st.warning('해당 ID가 없습니다.')
                except psycopg.Error:
                    st.error('데이터베이스 수정 중  문제가 발생했습니다.')

    with col2:
        if st.button('삭제',type='secondary',use_container_width=True):
            try:
                count = remove_voice_data(data_id)
                if count:
                    st.success('삭제 했습니다.')
                else:
                    st.warning('해당 ID가 없습니다.')
            except psycopg.Error:
                st.error('데이터 베이스 삭제중 문제가 발생했습니다.')

def main():
    st.set_page_config(
        page_title='VOICE DB',
        page_icon='🎙️',
        layout='wide'
    )
    st.title('VOICE Metadata')
    st.caption('Streamlit + PostgreSQL 데이터 관리 웹앱')

    # DB 접속 환경 변수가 없다면 웹앱 실행 중단
    if not has_database_url_logic():
        st.error('DATABASE_URL 환경변수를 설정하세요.')
        st.stop() # UI 중단

    try:
        create_table_logic()
    except psycopg.Error:
        st.error('PostgreSQL 연결 또는 테이블 생성에 실패했습니다.')
        st.stop()


    tab1, tab2, tab3 = st.tabs(['등록','조회','수정/삭제'])

    with tab1:
        show_insert_form()

    with tab2:
        show_data_list()

    with tab3:
        show_update_delete()

if __name__ == '__main__':
    main()

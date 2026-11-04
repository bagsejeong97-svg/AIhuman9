# day30_basic_db.py
# 주제: PostgreSQL 연동을 통한 Streamlit 스터디 일정 관리 CRUD 웹앱 구현
# python -m streamlit .r/webservice/day30/day30_basic.db.py
import os
import streamlit as st
import pandas as pd
import psycopg

from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    if not DATABASE_URL:
        st.error('접속 정보 미설정')
        st.stop()
    return psycopg.connect(DATABASE_URL)


def create_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS STUDY_SCHEDULE (
        ID SERIAL PRIMARY KEY,
        SUBJECT VARCHAR(100) NOT NULL,
        STUDY_DATE TIMESTAMP NOT NULL,
        PLACE VARCHAR(100) NOT NULL DEFAULT '미정'
    );
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()


def insert_schedule(conn, subject, study_date, place):
    sql = """
    INSERT INTO STUDY_SCHEDULE (SUBJECT, STUDY_DATE, PLACE) 
    VALUES (%s, %s, %s)
    """
    with conn.cursor() as cur:
        cur.execute(sql, (subject, study_date, place))
        conn.commit()


def get_schedule(conn):
    sql = """
    SELECT ID, SUBJECT, STUDY_DATE, PLACE 
    FROM STUDY_SCHEDULE
    ORDER BY STUDY_DATE,ID
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    df = pd.DataFrame(rows, columns=['ID', '학습 주제', '학습 날짜', '장소'])
    return df


def main():
    st.title('스터디 일정 관리 웹앱')

    with get_connection() as conn:
        create_table(conn)

        st.subheader('일정 등록')

        with st.form('study_schedule', clear_on_submit=True):
            subject = st.text_input('학습 주제를 입력하시오.')
            study_date = st.date_input('학습 날짜를 입력하시오.')
            place = st.text_input('학습 장소를 입력하시오.')

            submitted = st.form_submit_button('일정 저장')

        if submitted:
            if not subject.strip():
                st.warning('학습 주제를 입력하시오.')
            elif not place.strip():
                st.warning('학습장소를 입력하시오.')
            else:
                # study_date는 date 객체이므로 .strip() 제거
                insert_schedule(conn, subject.strip(), study_date, place.strip())
                st.success('저장 완료')
                st.rerun()  # 저장 후 즉시 목록 갱신

        st.divider()

        st.subheader('등록된 일정 확인')

        df = get_schedule(conn)

        if df.empty:
            st.info('일정 미등록')
        else:
            st.dataframe(df, use_container_width=True)


if __name__ == '__main__':
    main()
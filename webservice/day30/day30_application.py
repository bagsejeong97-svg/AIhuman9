# day30_application.py
# 주제:
# day30_application.py
# 채용 공고 지원 관리 웹앱

import os
import pandas as pd
import psycopg
import streamlit as st
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """PostgreSQL 연결 객체를 생성합니다."""
    return psycopg.connect(DATABASE_URL)

def create_table():
    """채용 지원 정보를 저장할 테이블을 생성합니다."""
    sql = """
    CREATE TABLE IF NOT EXISTS job_applications (
        id SERIAL PRIMARY KEY,
        company VARCHAR(100) NOT NULL,
        position VARCHAR(100) NOT NULL,
        status VARCHAR(20) NOT NULL,
        memo TEXT
    )
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

def add_job(company, position, status, memo):
    """새 지원 정보를 저장합니다."""
    sql = """
    INSERT INTO job_applications
        (company, position, status, memo)
    VALUES (%s, %s, %s, %s)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (company, position, status, memo or None),
            )

def search_jobs(keyword):
    """회사명에 keyword가 포함된 지원 정보를 조회합니다."""
    sql = """
    SELECT id, company, position, status, memo
    FROM job_applications
    WHERE company ILIKE %s
    ORDER BY id DESC
    """
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, (f"%{keyword.strip()}%",))
            return cur.fetchall()

def update_status(job_id, status):
    """PK로 지원 건을 찾아 상태를 변경합니다."""
    sql = """
    UPDATE job_applications
    SET status = %s
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (status, job_id))
            return cur.rowcount

def main():
    """등록, 검색, 상태 수정 화면을 구성합니다."""
    st.title("채용 공고 지원 관리")
    if not DATABASE_URL:
        st.error("DATABASE_URL을 설정하세요.")
        st.stop()
    try:
        create_table()
        with st.form("job_form", clear_on_submit=True):
            company = st.text_input("회사명")
            position = st.text_input("지원 직무")
            status = st.selectbox(
                "상태",
                ["관심", "지원", "면접", "결과"],
            )
            memo = st.text_area("메모")
            submitted = st.form_submit_button("등록")
        if submitted:
            if not company.strip() or not position.strip():
                st.warning("회사명과 지원 직무를 입력하세요.")
            else:
                add_job(
                    company.strip(),
                    position.strip(),
                    status,
                    memo.strip(),
                )
                st.success("등록했습니다.")
        keyword = st.text_input("회사명 검색")
        rows = search_jobs(keyword)
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )
        st.subheader("지원 상태 수정")
        job_id = st.number_input("지원 ID", min_value=1, step=1)
        new_status = st.selectbox(
            "새 상태",
            ["관심", "지원", "면접", "결과"],
            key="new_status",
        )
        if st.button("상태 수정"):
            count = update_status(int(job_id), new_status)
            if count:
                st.success("상태를 수정했습니다.")
            else:
                st.warning("해당 ID가 없습니다.")
    except psycopg.Error:
        st.error("데이터베이스 처리 중 문제가 발생했습니다.")

if __name__ == "__main__":
    main()

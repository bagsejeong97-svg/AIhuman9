# day30_challenge.py
# 주제:
# day30_challenge.py
# CAI 모델 실험 기록 관리 웹앱

import os
import pandas as pd
import psycopg
import streamlit as st
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """환경변수 기반 PostgreSQL Connection을 반환합니다."""
    return psycopg.connect(DATABASE_URL)

def create_table():
    """AI 모델 실험 기록 테이블을 생성합니다."""
    sql = """
    CREATE TABLE IF NOT EXISTS model_experiments (
        id SERIAL PRIMARY KEY,
        model_name VARCHAR(100) NOT NULL,
        dataset_name VARCHAR(100) NOT NULL,
        accuracy DOUBLE PRECISION NOT NULL
            CHECK (accuracy >= 0 AND accuracy <= 1),
        memo TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

def add_experiment(model_name, dataset_name, accuracy, memo):
    """새 모델 실험 결과를 저장합니다."""
    sql = """
    INSERT INTO model_experiments
        (model_name, dataset_name, accuracy, memo)
    VALUES (%s, %s, %s, %s)
    """
    params = (model_name, dataset_name, accuracy, memo or None)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)

def load_experiments(min_accuracy):
    """최소 정확도 이상인 실험을 성능 내림차순으로 조회합니다."""
    sql = """
    SELECT id, model_name, dataset_name, accuracy, memo, created_at
    FROM model_experiments
    WHERE accuracy >= %s
    ORDER BY accuracy DESC, created_at DESC
    """
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, (min_accuracy,))
            return cur.fetchall()

def delete_experiment(exp_id):
    """PK에 해당하는 실험 기록을 삭제합니다."""
    sql = "DELETE FROM model_experiments WHERE id = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (exp_id,))
            return cur.rowcount

def main():
    """실험 등록, 조건 조회, 확인 후 삭제 기능을 구성합니다."""
    st.set_page_config(page_title="AI Experiment DB", layout="wide")
    st.title("AI 모델 실험 기록 관리")
    if not DATABASE_URL:
        st.error("DATABASE_URL을 설정하세요.")
        st.stop()
    try:
        create_table()
        with st.form("experiment_form", clear_on_submit=True):
            model_name = st.text_input("모델명")
            dataset_name = st.text_input("데이터셋명")
            accuracy = st.number_input(
                "정확도",
                min_value=0.0,
                max_value=1.0,
                value=0.8,
                step=0.01,
            )
            memo = st.text_area("메모")
            submitted = st.form_submit_button("실험 결과 저장")
        if submitted:
            if not model_name.strip() or not dataset_name.strip():
                st.warning("모델명과 데이터셋명을 입력하세요.")
            elif not 0.0 <= accuracy <= 1.0:
                st.warning("정확도는 0.0~1.0이어야 합니다.")
            else:
                add_experiment(
                    model_name.strip(),
                    dataset_name.strip(),
                    float(accuracy),
                    memo.strip(),
                )
                st.success("실험 결과를 저장했습니다.")
        st.subheader("성능 조건 조회")
        min_accuracy = st.slider(
            "최소 정확도",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            step=0.01,
        )
        rows = load_experiments(min_accuracy)
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )
        st.subheader("실험 기록 삭제")
        exp_id = st.number_input("삭제 ID", min_value=1, step=1)
        confirmed = st.checkbox("삭제할 데이터를 확인했습니다.")
        if st.button("삭제", disabled=not confirmed):
            count = delete_experiment(int(exp_id))
            if count:
                st.success("삭제했습니다.")
            else:
                st.warning("해당 ID가 없습니다.")
    except psycopg.Error:
        st.error("데이터베이스 처리 중 문제가 발생했습니다.")

if __name__ == "__main__":
    main()

# day32_application.py
# 주제:
# day32_application.py

import os
import uuid
import psycopg
from psycopg.rows import dict_row
import streamlit as st
from util.print_util import pp, up
from dotenv import load_dotenv

load_dotenv()

def db(sql, params=()):
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise ValueError("DATABASE_URL 환경변수를 설정하세요.")
    with psycopg.connect(
        url, connect_timeout=15, row_factory=dict_row,
        prepare_threshold=None,
    ) as conn:
        return conn.execute(sql, params).fetchall()  # 값 바인딩, 결과 목록

def main():
    st.title("월간 예산 계획")
    if "budget_preview" not in st.session_state:
        st.session_state["budget_preview"] = None
    try:
        with st.form("budget"):
            title = st.text_input("계획 제목", max_chars=80)
            income = st.number_input("수입(원)", 0, 100000000, step=1000)
            expense = st.number_input("지출(원)", 0, 100000000, step=1000)
            ok = st.form_submit_button("계산 미리보기")
        if ok:
            if not title.strip():
                st.warning("계획 제목을 입력하세요.")
            else:
                st.session_state["budget_preview"] = {
                    "title": title.strip(), "income": int(income),
                    "expense": int(expense), "balance": int(income - expense),
                    "key": str(uuid.uuid4()),
                }  # 새 계산 결과마다 새로운 요청 키
        p = st.session_state["budget_preview"]
        if p:
            st.write(p["title"])
            st.metric("예상 잔액", f"{p['balance']:,}원")
            if st.button("계획 저장"):
                rows = db(
                    "INSERT INTO budget_plans "
                    "(title, income, expense, balance, request_key) "
                    "VALUES (%s, %s, %s, %s, %s) "
                    "ON CONFLICT (request_key) DO NOTHING RETURNING id",
                    (p["title"], p["income"], p["expense"],
                     p["balance"], p["key"]),
                )
                st.success("저장 완료" if rows else "이미 저장한 계획입니다.")
        stats = db(
            "SELECT count(*) AS total, "
            "COALESCE(sum(balance), 0) AS balance_sum FROM budget_plans"
        )[0]
        st.write("전체 계획:", stats["total"], "잔액 합계:", stats["balance_sum"])
        keyword = st.text_input("제목 검색", max_chars=80)
        rows = db(
            "SELECT id, title, balance FROM budget_plans "
            "WHERE title ILIKE %s ORDER BY id DESC LIMIT 100",
            (f"%{keyword.strip()}%",),
        )
        st.dataframe(rows, hide_index=True, use_container_width=True)
        if rows:
            rid = st.selectbox("상세 ID", [x["id"] for x in rows])
            detail = db("SELECT * FROM budget_plans WHERE id = %s", (rid,))
            if detail:
                st.write({k: detail[0][k] for k in
                          ("title", "income", "expense", "balance")})
            else:
                st.info("기록이 사라졌습니다.")
    except ValueError as exc:
        st.warning(str(exc))
    except psycopg.Error as exc:
        pp("DB 오류 유형:", type(exc).__name__)
        st.error("연결·권한·budget_plans 테이블을 확인하세요.")

if __name__ == "__main__":
    main()

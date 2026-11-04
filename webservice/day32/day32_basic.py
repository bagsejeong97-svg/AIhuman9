# day32_basic.py

import os
import psycopg
from psycopg.rows import dict_row
import streamlit as st
from util.print_util import pp, up
from dotenv import load_dotenv

load_dotenv()

# DB 연결하고 쿼리 실행하는 함수
def db(sql, params=()):
    url = os.getenv("DATABASE_URL", '').strip()
    if not url:
        raise ValueError("DATABASE_URL 환경변수를 설정하세요.")
    with psycopg.connect(
        url,
        connect_timeout=15,
        row_factory=dict_row
    ) as conn:
        return conn.execute(sql, params).fetchall()

# 중량에 따라 배송비 리턴하는 함수
def shipping_fee(weight):
    return 3000 if weight <= 1000 else 3000 + ((weight-1) // 1000) * 1000

def main():
    st.title('배송비 견적 기록')
    try:

        with st.form('quote'):
            label = st.text_input('견적 제목', max_chars=80)
            weight = st.number_input('무게(g)', 1, 20000, 1000, step=1)
            ok = st.form_submit_button('계산하고 저장')
        if ok:
            if not label.strip():
                st.warning('제목을 입력하세요.')
            else:
                fee = shipping_fee(int(weight)) # 배송비 계산
                # 데이터 입력
                rows = db(
                    ' INSERT INTO SHIPPING_QUOTES '
                    ' (LABEL, WEIGHT, FEE, RULE_VERSION) '
                    ' VALUES (%s, %s, %s, %s) RETURNING ID ',
                    (label.strip(), int(weight), fee, 'shipping-v1')
                )
                st.success(f"{fee:,}원, 기록 {rows[0]['id']} 저장")

            # 목록 조회 후 데이터프레임에 표시
            rows = db(' SELECT * FROM SHIPPING_QUOTES ORDER BY ID DESC LIMIT 100 ')
            st.dataframe(rows, hide_index=True, use_container_width=True)

    except ValueError as ve:
        st.warning(str(ve))
    except psycopg.Error as pe:
        pp('DB오류 - 유형: ', type(pe).__name__)
        st.error('연결/권한/테이블을 확인하세요.')

if __name__ == '__main__':
    main()






































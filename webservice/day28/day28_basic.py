# day28_basic.py

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title = '영화 평점 CSV 요약기',
    layout = 'wide'
)

st.title('영화 평점 CSV 요약기')

uploaded = st.file_uploader(
    '영화 평점 CSV 파일',
    type = ['csv']
)

if uploaded is None:
    st.info('CSV 파일을 선택하세요.')
else:
    try:

        df = pd.read_csv(
            uploaded,
            encoding = 'utf-8-sig',
        )

        required = {'영화명', '장르', '평점'}

        if not required.issubset(df.columns):
            st.error('영화명, 장르, 평점 컬럼이 필요합니다.')
        else:
            df['평점'] = pd.to_numeric(df['평점'], errors='coerce')

            c1, c2, c3 = st.columns(3)
            c1.metric('영화 수', len(df))
            c2.metric('평균 평점', f'{df["평점"].mean():.2f}')
            c3.metric('최고 평점', f'{df["평점"].max():.1f}')

            st.dataframe(
                df,
                use_container_width = True,
                hide_index = True
            )

    except Exception as error:
        st.error(f'파일 처리 오류: {error}')

































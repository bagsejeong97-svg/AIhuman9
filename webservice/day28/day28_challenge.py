# day28_challenge.py
# 주제:

import streamlit as st
import matplotlib.pyplot as plt
from include.graph_config import set_graph
import numpy as np
import pandas as pd
set_graph(10, 8, 13)

data = {
    '날짜': [
        '2026-10-01', '2026-10-01', '2026-10-02', '2026-10-02',
        '2026-10-03', '2026-10-03', '2026-10-04', '2026-10-04'
    ],
    '운동종류': [
        '러닝', '수영', '웨이트', '러닝',
        '수영', '웨이트', '러닝', '수영'
    ],
    '운동시간': [30, 45, 60, 40, 50, 55, 35, 40],       # 단위: 분
    '소모칼로리': [300, 400, 350, 420, 450, 320, 350, 380] # 단위: kcal
}
# DataFrame 변환
df = pd.DataFrame(data)
st.set_page_config(
    page_title='나의 운동기록과 음성 메모',
    layout='centered'
)

data_tab, audio_tab = st.tabs(['운동기록', '음성메모'])
with data_tab:

    st.header('운동 기록')

    st.subheader('운동 종류 선택')

    total = ['전체']+ list(df['운동종류'].unique())

    category = st.selectbox('운동종류',total)
    filter_df = df.copy()
    if category != '전체':
        filter_df = df[df['운동종류']==category]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        '기록건수',f'{filter_df['운동시간'].count()}건'
    )
    c2.metric(
        '총 운동시간',f'{filter_df['운동시간'].sum()}시간'
    )
    c3.metric(
        '총 소모 칼로리',f'{filter_df['소모칼로리'].sum():,}kcal'
    )
    st.dataframe(filter_df,use_container_width=True,hide_index=True)

    fig,ax=plt.subplots()

    total_minus = df.groupby('날짜')['소모칼로리'].sum().sort_values(ascending=False)

    ax.plot(total_minus.index,total_minus.values)
    ax.set_title('날짜별 소모칼로리')
    ax.set_xlabel('날짜별')
    ax.set_ylabel('소모칼로리')
    fig.autofmt_xdate()
    ax.grid(alpha=0.2)
    st.pyplot(fig)


with audio_tab:
    st.header('WAV 음성파일')
    audio_file = st.file_uploader(
        'WAV 파일 선택',
        type=['WAV'],
        key='wav_file'
    )
    if audio_file is None:
        st.info('재생할 WAV 파일을 선택하세요.')
    else:
        file_size = len(audio_file.getvalue())
        c1, c2 = st.columns(2)
        c1.metric('파일 크기', f'{file_size / 1024:.1f} KB')
        c2.metric('파일명',audio_file.name)
        st.audio(audio_file, format='audio/wav')

        st.success('음성메모 연결 완료')






















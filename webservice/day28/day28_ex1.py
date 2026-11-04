# day28_ex1.py
# Streamlit 데이터/음성 대시보드

import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from include.graph_config import set_graph

set_graph(10, 8, 13)

st.set_page_config(
    page_title = '데이터/음성 대시보드',
    page_icon = '📊',
    layout = 'wide'
)

# 샘플데이터 생성 함수
# @st.cache_data : 데이터를 캐싱하기 위해 사용하는 데코레이터
#                  rerun시마다 데이터를 생성할 수는 없으므로 생성된 데이터를 캐싱(임시 저장)
@st.cache_data
def make_sample_data():
    rng = np.random.default_rng(42) # 랜덤 제네레이터
    dates = pd.date_range( # 날짜 범위
        '2026-09-01', # 시작날짜
        periods=30, # 기간
        freq='D' # 주기 (Day)
    )
    rows = []
    for date in dates:
        for region in ['강남', '종로', '마포']:
            visitors = int(rng.integers(80, 301))
            stay = round(float(rng.uniform(10, 45)), 1)
            score = round(float(rng.uniform(3.0, 5.0)), 1)
            rows.append({
                '날짜': date,
                '지역': region,
                '방문자수': visitors,
                '평균체류시간': stay,
                '만족도': score
            })
    return pd.DataFrame(rows)

# print(make_sample_data())

# 업로드한 CSV 파일을 읽어서 데이터프레임 반환하는 함수
def read_csv_file(uploaded):
    raw = uploaded.getvalue()
    encodings = ['utf-8-sig', 'utf-8', 'cp949'] # 인코딩 후보
    last_error = None # 최종 발생한 에러 저장 변수
    for encoding in encodings: # 인코딩 별로 읽기 시도
        try:
            return pd.read_csv(
                io.BytesIO(raw), # 원본데이터를 byte로 읽음
                encoding=encoding
            )
        except UnicodeDecodeError as error:
            last_error = error
    raise last_error # 에러 발생

st.title('데이터/음성 대시보드')
st.caption('CSV 데이터 분석과 WAV 음성 재생을 하나의 웹앱에 구성함')

data_tab, audio_tab = st.tabs(['데이터 분석', '음성 파일'])

with data_tab:
    st.header('데이터 분석 대시보드')
    uploaded = st.file_uploader(
        'CSV 파일 선택',
        type=['csv'], # 업로드 허용 파일 확장자
        key='csv_file' # 식별자
    )
    try:
        if uploaded is None: # 업로드된 파일이 없다면
            df = make_sample_data() # 샘플데이터 생성
            st.info('CSV 파일이 업로드 되지 않아 샘플 데이터를 사용함')
        else:
            df = read_csv_file(uploaded)
            st.success('CSV 파일을 읽어서 데이터프레임 생성함')
    except Exception as error:
        st.error(f'CSV 파일을 읽을 수 없음: {error}')
        st.stop() # 종료

    # 컬럼 중에 날짜 컬럼이 있다면 문자타입을 날짜타입으로 변환
    if '날짜' in df.columns:
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')

    with st.sidebar:
        st.header('데이터 필터')
        if '지역' in df.columns:
            regions = df['지역'].dropna().astype(str).unique().tolist()
            regions = ['전체'] + sorted(regions)
            region = st.selectbox('지역 선택', regions)
        else:
            region = '전체'
            st.caption('지역 컬럼이 없어서 지역 필터를 생략함')

    filtered = df.copy()

    # 필터링하는 지역이 있다면
    if region != '전체' and '지역' in filtered.columns:
        # 필터링된 지역으로 데이터프레임 구성
        filtered = filtered[filtered['지역'].astype(str) == region]

    if filtered.empty: # 필터링된 데이터가 없다면
        st.warning('조건에 맞는 데이터가 없음')
    else:
        numeric = filtered.select_dtypes(include='number') # 숫자타입만 추출
        total_missing = int(filtered.isna().sum().sum()) # 결측치 합계

        c1, c2, c3 = st.columns(3)
        c1.metric('데이터 건수', f'{len(filtered):,}')
        c2.metric('수치형 컬럼', len(numeric.columns))
        c3.metric('결측치', f'{total_missing:,}')

        st.subheader('데이터 미리보기')

        st.dataframe(
            filtered, # 필터링된 데이터프레임
            use_container_width=True, # 넓이를 컨테이너 넓이 전체에 맞춤
            hide_index=True # 인덱스 숨김
        )

        if not numeric.empty: # 숫자 컬럼이 있다면
            st.subheader('기초 통계')
            st.dataframe( # 기초통계 데이터프레임
                numeric.describe().round(2),
                use_container_width=True
            )

        # 필터링된 데이터프레임에 날짜와 방문자수 컬럼이 있다면
        if {'날짜', '방문자수'}.issubset(filtered.columns):
            st.subheader('날짜별 방문자 변화')
            daily = (
                filtered.groupby('날짜')['방문자수'].sum().sort_index()
            )
            st.line_chart(daily)

        if {'지역', '방문자수'}.issubset(filtered.columns):
            st.subheader('지역별 평균 방문자수')
            region_mean = (
                df.groupby('지역')['방문자수'].mean().sort_values(ascending=False)
            )
            fig, ax = plt.subplots()
            ax.bar(region_mean.index, region_mean.values)
            ax.set_title('지역별 평균 방문자수')
            ax.set_xlabel('지역')
            ax.set_ylabel('평균 방문자 수')
            st.pyplot(fig)
            plt.close(fig) # Streamlit으로 그리므로

with audio_tab:
    st.header('WAV 음성 파일')
    audio_file = st.file_uploader(
        'WAV 파일 선택',
        type = ['WAV'],
        key = 'wav_file'
    )
    if audio_file is None:
        st.info('재생할 WAV 파일을 선택하세요.')
    else:
        file_size = len(audio_file.getvalue())
        c1, c2 = st.columns(2)
        c1.metric('파일 크기', f'{file_size/1024:.1f} KB')

        st.audio(audio_file, format='audio/wav')

        st.success('향후 이 영역에 STT/TTS 또는 음성 모델을 연결함!')





































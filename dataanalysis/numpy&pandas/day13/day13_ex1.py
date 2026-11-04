# day13_ex1.py
# 주제: 문자열 처리 , 날짜 데이터 처리, 범주형 데이터 처리, 구간화
from util.print_util import pp

pp()

import pandas as pd

#채용데이터
df = pd.DataFrame({
    "지원자": [" 김민수 ", "이서연", " 박준호", "최유진 ", "정하늘", "윤지호", "한소민", "오지훈"],
    "직무": [" Data Analyst ", "DATA ANALYST", "data  analyst", "AI Engineer", "ai engineer ", "Backend", "BACKEND ", "backend"],
    "지원일": ["2026-08-01", "2026/08/03", "2026-08-05", "2026-08-08", "invalid", "2026-08-15", "2026/08/17", "2026-08-20"],
    "전형": ["서류", "면접", "서류", "과제", "면접", "서류", "과제", "면접"],
    "평가점수": [78, 84, 82, 91, 88, 76, 80, 190]
})
df.info()

# 문자열 공백 처리, 표기 정리
df['지원자'] = df['지원자'].str.strip() # 이름 앞뒤 공백 문자 제거
df['직무'] = (
    df['직무']
    .str.strip()   # 공백 문자 제거
    .str.lower()   # 소문자로 변경
    .str.replace(r'\s+', ' ',regex=True)   # 공백문자가 1개이상 연속되면 1개로, 정규표현식 사용
)
pp(df[['지원자','직무']])

#문자열 검색, 부분 추출


# 컬럼의 문자열이 data라는 문자열을 포함하면 True,
#포함하지 않거나 결측치일 경우 False
df['데이터직무'] = df['직무'].str.contains('data', na=False)
pp(df['데이터직무'])


# 직무 컬럼의 문자열에서 영문소문자가 1개이상 반복되는 문자열로 시작하는
# 문자열을 추출
# expand=False : 별도 컬럼으로 확장하지 않음
df['직무첫단어'] = df['직무'].str.extract(r'^([a-z]+)', expand=False)
pp(df['직무첫단어'])
df['직무첫단어'] = df['직무'].str.extract(r'^([a-z]+)', expand=True)
pp(df['직무첫단어'])

# 날짜 문자열 > datetime
pp(type(df['지원일'].dtypes))

df['지원일'] = pd.to_datetime(  # 날짜 타입으로 변환
    df['지원일'],
    errors='coerce',   # 변환 불가시에는 NaT
    format = 'mixed')  # 포멧 = 형식

pp(df['지원일'])
pp(type(df['지원일'].dtypes))
pp(df['지원일'].isna().sum())  # 1, NaT 1개

# 날짜 파생 변수 생성
df['지원연도'] = df['지원일'].dt.year
df['지원월'] = df['지원일'].dt.month
df['지원요일'] = df['지원일'].dt.day_name()
df['지원요일번호'] = df['지원일'].dt.dayofweek
df['지원연월'] = df['지원일'].dt.strftime('%Y-%m-%d')
pp([[df['지원연도'],df['지원일'],df['지원요일'],df['지원요일번호'],df['지원연월']]])

# 기준일과 날짜 차이 계산
reference_date = pd.Timestamp('2026-08-31')
df['기준일까지경과일'] = (reference_date - df['지원일']).dt.days # 경과일
pp(df[['지원일','기준일까지경과일']])

# 범주형 자료형 변환
df['전형'] = df['전형'].astype('category')
pp(df['전형'].cat.categories)
pp(df['전형'].cat.categories.to_list())

# 순서형 범주 만들기
process_order = ['서류','과제','면접'] # 범주로 사용할 리스트
process_type = pd.CategoricalDtype(
    categories=process_order, # 범주리스트
    ordered=True) # 순서가 있음

# 범주로 정렬하기 위해 순서형 범주 타입으로 변환
df['전형']=df['전형'].astype(process_type) # 전형을 순서형 범주 타입으로 변환
pp(df.sort_values('전형')[['지원자','전형']]) # 전형 오름차순 정렬 후 지원자, 전형 출력

# 점수를 고정 구간 범주로 변환
df['평가등급'] = pd.cut(
    df['평가점수'],  # 범주 기준 데이터
    #구간설정 ,float('inf') = 무한대
    bins = [0,70,80,90,100,float('inf')],
    labels = ['D','C','B','A','범위초과'], # 구간 명칭
    include_lowest = True # 최소값을 구간에 포함 (bins의 최소값)
)
pp(df[['평가점수','평가등급']])

# IQR 기준 계산
q1 = df['평가점수'].quantile(0.25)  # 1사 분위수 , 1/4
q2 = df['평가점수'].quantile(0.5)  # 2사분위수 , 2/4 중앙값(median)
q3 = df['평가점수'].quantile(0.75)  # 3사 분위수 , 3/4
iqr = q3 - q1  # 중앙값에 위치한 50% 범위
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr  # 하한, 상한 값
pp(f'Q1 = {q1:.2f}, Q2 = {q2:.2f}, Q3 = {q3:.2f}, IQR = {iqr:.2f}')
pp(f'하한 ={lower:.2f}, 상한={upper:.2f}')

# 이상치 후보 탐지
# 평가점수가 하한 ~ 상한 사이인지 여부에 대한 불리언 시리즈
# between(a, b) : a와 b를 포함한 사이
outlier_mask = ~df['평가점수'].between(lower, upper)
df['이상치여부'] = outlier_mask
pp(outlier_mask)

# 원본을 유지하면서 경계값으로 보정
df['평가점수_보정'] = df['평가점수'].clip(lower=lower,upper=upper)
pp(df[['평가점수','평가점수_보정']]) # 190을 102.625(상한값) 으로 보정

# 전처리 결과 검증
pp('날짜 NaT 수 :', df['지원일'].isna().sum()) # 날짜 없는 값
pp('직무 교유값:', sorted(df['직무'].unique()))
pp('전형 범주:', list(df['전형'].cat.categories))
pp('이상치 후보 수:', int(df['이상치여부'].sum()))

pp(df) # 전체 데이터  프레임 출력































# day13_challenge.py
# 주제:
from util.print_util import pp

pp()

import pandas as pd

df = pd.DataFrame({
    "설비ID": [" mx-01 ", "MX-01", "mx-02", " MX-02 ", "MX-03", "mx-03", "MX-04", "mx-04"],
    "점검시각": ["2026-09-01 08:30", "2026/09/01 12:30", "2026-09-02 09:00", "invalid", "2026-09-03 10:10", "2026/09/03 16:20", "2026-09-04 07:50", "2026-09-04 18:10"],
    "상태": [" normal ", "NORMAL", "Warning", " warning", "normal", "ALERT", "alert ", "Normal"],
    "온도": [62.1, 63.0, 64.2, 63.8, 65.1, 64.7, 66.0, 142.0],
    "진동": [1.2, 1.3, 1.4, 1.5, 1.2, 1.6, 1.4, 8.9]
})

# 문자열 정제 함수
def clean_text(series):
     return (pd.Series(series)
             .astype('string')
             .str.strip()
             .str.lower()
             .str.replace(r'\s+', ' ',regex=True))

# IQR 하한, 상한 구하는 함수
def iqr_bounds(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower,upper = q1-1.5*iqr,q3+1.5*iqr
    return lower,upper

# 설비id 공백 제거후 대문자
# pp(clean_text(df['설비ID']).str.upper())
df['설비ID'] = df['설비ID'].str.strip().str.upper()
df['상태'] = clean_text(df['상태'])

# 점검 시각 변환, 파생 변수 생성
df['점검시각'] = pd.to_datetime(df['점검시각'], errors='coerce',format = 'mixed')
df['점검일'] = df['점검시각'].dt.date
df['점검시간'] = df['점검시각'].dt.strftime('%H:%M') # 시 : 분 문자열
df['점검일'] = df['점검시각'].dt.day_name()

# 상태를 순서형 category로 변환
status_order = ['normal','warning','alert'] # 카테고리로 사용할 리스트
status_type = pd.CategoricalDtype(  # 순서가 있는 카테고리 타입 생성
    categories= status_order,
    ordered= True
)

df['상태'] = df['상태'].astype(status_type)

# 온도와 진동의 IQR 경계 계산
temp_lower , temp_upper = iqr_bounds(df['온도'])
vib_lower , vib_upper = iqr_bounds(df['진동'])

#센서별 이상치 후보 표시
df['온도이상'] = ~df['온도'].between(temp_lower , temp_upper)
df['진동이상'] = ~df['진동'].between(vib_lower , vib_upper)
df['센서이상'] = df['온도이상'] | df['진동이상']

#원본을 유지하고 보정 센서값 생성
df['온도_보정'] = df['온도'].clip(lower=temp_lower, upper=temp_upper)
df['진동_보정'] = df['온도'].clip(lower=vib_lower, upper=vib_upper)

# 데이터 품질 보고서
quality_report = {
    '전체 행 수' : len(df),
    '날짜 변환 실패 수' : int(df['점검시각'].isna().sum()),
    '상태 범주 목록' : list(df['상태'].cat.categories),
    '온도 이상치 수' : int(df['온도이상'].sum()),
    '진동 이상치 수' : int(df['진동이상'].sum()),
    '하나 이상의 센서 이상 행수' : int(df['센서이상'].sum())
}
pp('[데이터 품질 보고서')
for key,value in quality_report.items():
    print(f'{key}: {value}')

# IQR 경계 출력
pp(f'온도 하한={temp_lower:.2f}, 상한={temp_upper:.2f}')
pp(f'진동 하한={vib_lower:.2f}, 상한={vib_upper:.2f}')

# 최종 정제 결과 출력
result_cols = [
    '설비ID','점검시각','상태','온도','온도_보정','온도이상','진동','진동_보정','진동이상','센서이상'
]
pp(['최종 정제 데이터'])
pp(df[result_cols])

















































# day13_application.py
# 주제:



from util.print_util import pp

pp()

import pandas as pd

df = pd.DataFrame({
    "학습자ID": [" S001 ", "S002", " s003", "S004 ", "S005", "s006", "S007", "S008"],
    "강의명": [" Python Data ", "PYTHON DATA", "python  data", "LLM Basic", "llm basic ", "Prompt", "PROMPT ", "prompt"],
    "접속일": ["2026-08-01", "2026/08/02", "2026-08-03", "2026-08-04", "error", "2026/08/06", "2026-08-07", "2026-08-08"],
    "접속기기": ["PC", "mobile", "Mobile", "pc", "TABLET", "tablet", "PC", "mobile"],
    "시청분": [42, 58, 35, 70, 63, 51, 47, 720],
    "진도율": [35, 48, 62, 77, 85, 91, 100, 56]
})
# 학습자 id 공백제거, 대문자 통일
df['학습자ID'] = df['학습자ID'].str.strip().str.upper()
pp(df['학습자ID'])

# 강의명은 소문자, 공백은 한칸
df['강의명'] = df['강의명'].str.strip().str.lower().str.replace(r'\s+',' ', regex=True)
pp(df['강의명'])

df['접속기기'] = df['접속기기'].str.lower()

# 접속기기는 pc,mobile,tablet 범주로 표기
df['접속기기'] = df['접속기기'].astype('category')

process_order = ['pc','mobile','tablet']
process_type = pd.CategoricalDtype(process_order, ordered=True)
pp(process_type)

df['접속기기'] = df['접속기기'].astype(process_type)
pp(df['접속기기'])


# 접속일 dt변환
df['접속일'] = pd.to_datetime(
    df['접속일'],
    errors='coerce',
    format = 'mixed'
)
df['접속월'] = df['접속일'].dt.month
df['접속요일'] = df['접속일'].dt.day_name()
df['접속연월'] = df['접속일'].dt.strftime('%Y-%m')

# 접속기기를 카테고리로
df['접속기기'] = df['접속기기'].astype(process_type)
pp(df['접속기기'])


# 진도 단계
df['진도단계'] = pd.cut(
    df['진도율'],
    bins = [0,49,74,99,100],
    labels = ['시작','진행','마무리','완료'],
    include_lowest = True,
    ordered=True #순서가 있다
)
pp(df['진도단계'])

#iqr

q1 = df['시청분'].quantile(0.25)
q3 = df['시청분'].quantile(0.75)
iqr = q3 - q1
lower,upper = q1 - 1.5*iqr,q3 + 1.5*iqr
pp(lower,upper)
# 이상치 여부
outlier_mask = ~df['시청분'].between(lower,upper)
df['이상치여부'] = outlier_mask
pp(df['이상치여부'])

#시청분_보정 컬럼
df["시청분_보정"] = df['시청분'].clip(lower=lower,upper=upper)
pp(df[['시청분_보정','시청분']])


# 날짜 변환 실패 건수 = a
a = df['접속일'].isna().sum()
#강의명 고유값 = b
b = sorted(df['강의명'].unique())
#접속 기기 범주 = c
c= list(df['접속기기'].cat.categories)
# 진도 단계별 건수 = d
d = df['진도단계'].value_counts(sort=False)
# 이상치 후보수 = f
f = int(df['이상치여부'].sum())
# 시청자 원본과 보정값 비교 = g
g = df[['학습자ID','시청분_보정','시청분']]

pp(f'날짜 변환 실패건수: {a}')
pp(f'강의명 고유값수 : {b}')
pp(f'접속 기기 범주: {c}')
pp(f'진도 단계별 건수: {d}')
pp(f'이상치 후보수: {f}')
pp(f'시청자 원본과 보정값 비교: {g}')












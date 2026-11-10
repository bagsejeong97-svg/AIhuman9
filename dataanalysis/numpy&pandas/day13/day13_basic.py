# day13_basic.py
# 주제:




import pandas as pd
from util.print_util import pp

pp()

df = pd.DataFrame({
    "예약자": [" 김지우 ", "박하준", " 이나연", "최도윤 ", "서윤아", "정민재"],
    "공간": [" Meeting Room ", "MEETING ROOM", "focus room", " Focus  Room ", "Lounge", "LOUNGE "],
    "예약일": ["2026-09-01", "2026/09/02", "2026-09-03", "bad-date", "2026-09-05", "2026/09/06"],
    "회원등급": ["Basic", "Pro", "Basic", "Enterprise", "Pro", "Basic"],
    "사용시간": [2, 3, 1, 2, 4, 18]
})

# 예약자 앞뒤 공백 제거
df['예약자'] = df['예약자'].str.strip()

# 공간 통일

df['공간'] = df['공간'].str.strip().str.lower().str.replace(r'\s+',' ',regex=True)

pp(df[['예약자','공간']])

df['예약일'] = pd.to_datetime(
    df['예약일'],
    errors='coerce',  # 변환 불가시 NaT 처리
    format = 'mixed'  # 여러 형태의 날짜처리 방식들을 모두 허용
)
pp(df['예약일'])

#  예약월 예약요일 컬럼 추가
df['예약월'] = df['예약일'].dt.month
df['예약요일'] = df['예약일'].dt.day_name()
pp([df['예약월'],df['예약요일']])

# 회원등급
df['회원등급'] = df['회원등급'].astype('category')
pp(df['회원등급'])
pp(df['회원등급'].cat.categories)  # 인덱스로 표현

# 사용시간 iqr 방식

q1 = df['사용시간'].quantile(0.25)
q3 = df['사용시간'].quantile(0.75)
iqr = q3 - q1
lower,upper = q1 - 1.5*iqr,q3 + 1.5*iqr
pp(lower,upper)
# 이상치 여부
# 사용시간이 lower~upper이 아닌 것은 True
outlier_mask = ~df['사용시간'].between(lower,upper)
df['이상치여부'] = outlier_mask
pp(df['이상치여부'])

# 전처리 결과 검증
#날짜 변환 실패건수 = a
a = df['예약일'].isna().sum()
# 공간 고유값 = b
b = sorted(df['공간'].unique())
# 이상치 후보 = c
c = df.loc[df['이상치여부'],['예약자','사용시간','예약일']]

pp(f'날짜 변환 실패건수: {a}')
pp(f'공간 고유값: {b}')
pp(f'이상치 후보: {c}')













# day10_challenge.py
# 주제:
from email.mime import application

import pandas as pd
from pathlib import Path

DATA_FILE = Path('applicants.csv')
REPORT_FILE = Path('applicants_data_dictionary.csv')
application_df = {
    '지원ID' : ['A001','A002','A003','A004','A005','A006','A007','A008','A009','A0010'],
    '지원직무' : ['백엔드','데이터분석','프론트엔드','AI엔지니어','백엔드','데이터분석','AI엔지니어','프론트엔드','백엔드','데이터분석'],
    '전공' : ['컴퓨터공학','통계학','디자인','전자공학','경영학','수학','컴퓨터공학','컴퓨터공학','전자공학','경영학'],
    '경력년수' : [1,0,2,1,3,1,2,0,1,2],
    '코딩테스트' : [82,91,78,94,75,89,96,84,87,81],
    '영어점수' : [845,910,800,880,920,870,935,825,860,905]
}


# 1.
df = pd.DataFrame(application_df)
# df = pd.read_csv(DATA_FILE)
df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
df = pd.read_csv(DATA_FILE)
# 2.
print(df.head())
print(df.tail())
print(df.shape)
print(df.columns)
print(df.dtypes)
df.info()

# 3.
score_df = df[['코딩테스트','영어점수']]
print(score_df)

# 4.
a = df.describe()
print(a)

# 5.
b = df['지원직무'].value_counts()
print(b)

#6.
c = df['전공'].unique()
print(c)
print(len(c))

#7.
print(f'컬럼명: {df.columns}')
print(f'dytpe: {df.dtypes}')
print(f'전체행수: {df.shape[0]}')
print(f'Non-Null개수: {df.info()}')
print(f'고유갑수: {df.nunique()}')
print(f'첫번째예시값: {df.head(1)}')

data_dictionary_rows = []
for column in df.columns:
    e_value = df[column].iloc[0]
    data_dictionary_rows.append({
        '컬럼명': df.columns,
    'dytpe': df.dtypes,
    '전체행수': df.shape[0],
    'Non-Null개수': df.info(),
    '고유갑수': df.nunique(),
    '첫번째예시값': df.head(1)

    })

data_dictionary = pd.DataFrame(data_dictionary_rows)
print(data_dictionary)

data_dictionary.to_csv(REPORT_FILE, index=False, encoding='utf-8-sig')

















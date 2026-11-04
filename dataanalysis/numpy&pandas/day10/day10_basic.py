# day10_basic.py
# 주제:
import pandas as pd
from pathlib import Path

DATA_FILE = Path('employee_training.csv')

sample_df = {
    '사번' : ['E101','E102','E103','E104','E105','E106'],
    '이름' : ['김지훈','이수빈','박현우','정예린','최민석','한서진'],
    '부서' : ['개발','기획','영업','개발','기획','영업'],
    '교육점수': [88,92,76,95,84,81],
    '교육시간': [8,10,6,12,8,7]
}

sample_df = pd.DataFrame(sample_df)

sample_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

employee_df = pd.read_csv(DATA_FILE)
print(employee_df)        # 3.

# 4.
print(employee_df.head(3))   # 처음 3개행
print(employee_df.tail(2))   # 마지막 2개행

#5. 행 과 열 출력
print(employee_df.shape)
a = employee_df.shape[0]
b = employee_df.shape[1]
print(f'행 : {a} , 열 : {b}')

#6. 컬럼이름 리스트 형태로 출력
print('컬럼 이름 : ',list(employee_df.columns))
#7. 각 컬럼의 dtypes
print(employee_df.dtypes)
#8.info()
employee_df.info()
#9. 교육점수의 평균 최솟값, 최대값
df = employee_df['교육점수']

print(f'평균 : {df.mean()}')
print(f'최소값 : {df.min()}')
print(f'최대값 : {df.max()}')

#부서별 직원수
print('부서별 직원수 : ',employee_df['부서'].value_counts())






















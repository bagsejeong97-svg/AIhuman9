# ex2
# merge(), concat()
# merge()
# - 특정 컬럼(키)의 값을 기준으로 두 데이터 프레임을 병합
# - SQL의 JOIN과 유사
# 대표옵션 : on, how, left_on, right_on, indicator
#
#concat()
# - 데이터 프레임을 행 방향 또는 열 방행으로 병합 (축 기준)
# - 대표 옵션 : axis, ignore_index, join
import pandas as pd

from util.print_util import pp

pp()

# merge()

student = pd.DataFrame({
    '학번' : [101,102,103,104],
    '이름' :['홍길동','김철수','이영희','강감찬']
})
pp(student)

score = pd.DataFrame({
    '학번' : [101,102,103,105],
    '점수': [90,80,85,70]
})
pp(score)
# how옵션 생략되면 기본값은 inner
result = pd.merge(student, score, on='학번')
pp(result)

# merge()의 how 옵션

# inner : 양쪽 데이터프레임에 모두 존재하는 학번만 결합
inner_result = pd.merge(
    student,
    score,
    on = '학번',
    how = 'inner'
)
pp(inner_result)


# left : 왼쪽 데이터프레임에 모든 행을 유지
left_result = pd.merge(
    student,
    score,
    on = '학번',
    how = 'left'
)
pp(left_result)

# right : 오른쪽 데이터프레임의 모든 행을 유지
right_result = pd.merge(
    student,
    score,
    on = '학번',
    how = 'right'
)
pp(right_result)

# outer : 양쪽 데이터프레임의 모든 행을 유지
outer_result = pd.merge(
    student,
    score,
    on = '학번',
    how = 'outer'
)
pp(outer_result)

# indicator = True 옵션, _merge 컬럼
# indicator=True를 설정하면 각 행이 어느 데이터프레임에서 왔는지
# 자동으로 생성되는 _merge 컬럼으로 확인 가능

indicator_result = pd.merge(
    student,
    score,
    on = '학번',
    how = 'outer',
    indicator=True
)
pp(indicator_result)

# _merge 값
# both : 양쪽 모두 존재
# left_only : 왼쪽에만 존재
# right_only : 오른쪽에만 존재
pp(indicator_result)

# concat() - 세로 결합
jan = pd.DataFrame({
    '상품' : ['A','B'],
    '매출' : [100,200]
})
pp(jan)
feb = pd.DataFrame({
    '상품': ['C','D'],
    '매출' : [300,400]
})
pp(feb)

concat_row = pd.concat(
    [jan,feb],
    axis = 0 #열 , 세로결합, 기본 값
).reset_index(drop = True) # 새로운 인덱스
pp(concat_row)

# innore_index=True 옵션
# : 기존 index를 버리고 0 부터 새로운 index생성
concat_row_reset = pd.concat(
    [jan,feb],
    axis = 0,
    ignore_index = True
)
pp(concat_row_reset)

# concat() - 가로결합
name_df = pd.DataFrame({
    '이름' : ['홍길동','김철수']
})
pp(name_df)  # type ; dataframe
score_df = pd.DataFrame({
    '점수':[90,80]
})
pp(score_df) # type ; dataframe

concat_col = pd.concat(
    [name_df,score_df],
    axis = 1    # 가로 결합
)
pp(concat_col)

# merge()와 concat(axis=1) 차이
df1 = pd.DataFrame({
    '학번':[101,102,103],
    '이름':['홍길동','김철수','이영희']
})
pp(df1)

df2 = pd.DataFrame({
    '학번':[103,102,101],
    '점수':[70,90,80]
})
pp(df2)

# merge() : 학번 값을 비교해서 학생과 점수를 연결
merge_result = pd.merge(
    df1,
    df2,
    on = '학번'
)
pp(merge_result)

# concat(axis=1)
concat_result = pd.concat(
    [df1,df2],
    axis=1
)
pp(concat_result)




















































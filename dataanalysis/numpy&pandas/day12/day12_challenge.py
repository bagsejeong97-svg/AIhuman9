# day12_challenge.py
# 주제:

from util.print_util import pp

pp()
import pandas as pd
activity_data = {
    "activity_id": ["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "E11", "E12"],
    "month": ["2026-01", "2026-01", "2026-01", "2026-02", "2026-02", "2026-02", "2026-03", "2026-03", "2026-03", "2026-03", "2026-02", "2026-01"],
    "course": ["Python", "AI", "Cloud", "Python", "AI", "Cloud", "Python", "AI", "Cloud", "Python", "AI", "Cloud"],
    "learner": ["민준", "서연", "지우", "민준", "하윤", "지우", "도윤", "서연", "시우", "하윤", "민준", "도윤"],
    "study_minutes": [120, 95, 80, 150, 110, 90, 130, 125, 100, 75, 140, 105],
    "completed": [1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1]
}



course_data = {
    "course": ["Python", "AI", "Cloud"],
    "category": ["Programming", "AI", "Infrastructure"],
    "instructor": ["김강사", "이강사", "박강사"]
}

activity_dt = pd.DataFrame(activity_data)
course_dt = pd.DataFrame(course_data)

# 코스로 데이터 결합
merged = pd.merge(activity_dt, course_dt, on="course", # 키컬럼
                  how = 'left', # 결합 방식
                  validate = 'm:1') #
print(merged)

course_summary = merged.groupby('course').agg(
    total_study_minutes=('study_minutes', 'sum'), # 전체 학습 분수
    avg_study_minutes=('study_minutes', 'mean'), # 평균 학습 분
    act_count=('activity_id', 'count'), # 활동 수
    total_completed=('completed', 'sum') # 완료 수
).reset_index()

course_summary['course_data'] = (course_summary['total_completed'] / course_summary['act_count'] * 100).round(1)
print(course_summary)

result = course_summary.sort_values(
    'course_data',
        ascending=False,
        ignore_index = True)
print(result)




study_pivot = merged.pivot_table(
    values = 'study_minutes', # 값 컬럼
    index = 'month', # 행
    columns = 'course', #열
    aggfunc = sum, # 집계함수
    fill_value = 0, # 결측값
    margins = True, # 추가
    margins_name = 'Total' # 추가할 항목에 이름
)
print(study_pivot)


completed_pivot = merged.pivot_table(
    values = 'completed',
    index = 'month',
    columns = 'category',
    aggfunc = 'mean',
    fill_value = 0)


completed_pivot = (completed_pivot*100).round(1)
print(completed_pivot)

# 전체 학습시간 검증

raw_total = merged['study_minutes'].sum() # 원복 학습분 합계
pivot_total = study_pivot.loc['Total','Total'] # 피벗 후 학습분 합계
pp(f'일치여부 :{raw_total == pivot_total}')























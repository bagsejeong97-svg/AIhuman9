# day12_application.py
# 주제:

import pandas as pd


# 지원 데이터
apply_data = {
    "applicant_id": ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08"],
    "job_code": ["J01", "J02", "J01", "J03", "J02", "J04", "J03", "J01"],
    "result": ["합격", "불합격", "합격", "서류검토", "합격", "합격", "불합격", "불합격"],
    "score": [88, 72, 91, 81, 86, 90, 69, 77]
}

# 직무 정보 데이터
job_data = {
    "job_code": ["J01", "J02", "J03"],
    "job_name": ["백엔드", "데이터분석", "AI서비스"],
    "team": ["플랫폼", "데이터", "AI"]
}

apply_df = pd.DataFrame(apply_data)
job_df = pd.DataFrame(job_data)
#info() 찍어 보기

# 지원 데이터 왼쪽기준으로 결합

merged = apply_df.merge(
    job_df,
    on = 'job_code',
    how = 'left',
    indicator = True,
    validate = 'many_to_one' # = 'm:1'
)
print(merged)

# 결합되지 않은 직무 코드
unmatched_codes = merged.loc[
    merged['_merge'] == 'left_only', # 왼쪽에만 존재하는 값
    'job_code'].unique() # 유일값
print(unmatched_codes)

# 미등록 직무명 보완
merged['job_name'] = merged['job_name'].fillna('미등록 직무')

# 직무별 지원 통계 계산
job_summary = (
    merged.groupby('job_name')
.agg(
        applicant_count = ('applicant_id', 'count'),
        avg_score = ('score', 'max')
    )
    .reset_index()
)

job_summary['avg_score'] = job_summary['avg_score'].round(1)

job_summary = job_summary.sort_values(
    by='avg_score',
    ascending=False,
    ignore_index=True
)
print(job_summary)

# 보완된 결합 결과 확인
print(merged[['applicant_id','job_code','score', '_merge']])









































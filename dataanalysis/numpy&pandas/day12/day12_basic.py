# day12_basic.py
# 주제: 도서관 대출 데이터 그룹 집계와 정렬


import pandas as pd
from unicodedata import category

loan_data = {
    "loan_id": ["L001", "L002", "L003", "L004", "L005", "L006", "L007", "L008", "L009", "L010"],
    "branch": ["강남", "강남", "마포", "종로", "마포", "강남", "종로", "마포", "강남", "종로"],
    "category": ["IT", "경제", "IT", "문학", "경제", "IT", "IT", "문학", "문학", "경제"],
    "loan_days": [7, 14, 10, 21, 8, 12, 9, 18, 6, 15]
}

df = pd.DataFrame(loan_data)
print(df)

# 지점별 대출 건수
loan_count = df.groupby('branch')['loan_id'].count()
print(loan_count)

# 평균 대출일수
avg_loan_days = df.groupby('branch')['loan_days'].mean().round(1)
print(avg_loan_days)


report = (
    df.groupby('branch').agg(
        loan_count = ('loan_id', 'count'),
        avg_loan_days = ('loan_days', 'mean')

    ). reset_index()
)
report['avg_loan_days'] = report['avg_loan_days'].round(1)

print(report)

# 대출 건수가 많은 지점부터 내림차순 정렬
ranked = report.sort_values(
    'loan_count',
    ascending=False,
    ignore_index = True
)

ranked.index = ranked.index + 1
print('dd',ranked)



category_count = df.groupby('category').agg(
    c1 = ('loan_id', 'count')
).reset_index()
print(category_count)

result = category_count.sort_values('c1',ascending=False, ignore_index = True)

print(result)






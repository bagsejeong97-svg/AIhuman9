#day13_ex3
from util.print_util import pp

# 문자열 처리, 범주형 ,구간화 보충

pp()

import pandas as pd

# str.contains() 와 na=False
s = pd.Series(['AI 개발','Python',None,'생성형 AI'])
pp(s)
pp(s.str.contains('AI'))
pp(s.str.contains('AI', na=False)) # 결측치를 False로 처리
pp(type(s.str.contains('AI'))) #<class 'pandas.Series'>
# 'AI' 문자열을 포함하면 True , 아니면 False의 값을 갖는 불리언 시리즈

#str.split() 과  expand = True
dates = pd.Series(['2026-09-08','2025-12-25','2024-01-01'])
pp(dates)
pp(dates.str.split('-'))
pp(type(dates.str.split('-')))
pp(dates.str.split('-',expand=True)) # 열 확장
pp(type(dates.str.split('-',expand=True))) #<class 'pandas.DataFrame'>

#str.extract() 와 캡춰그룹()
s = pd.Series(['상품123','제품45','item789'])
pp(s)
# 패턴을 따른 문자열을 추출(extract)하려면  추출 전에 캡춰를 해야함
pp(s.str.extract(r'(\d+)')) # 숫자가 하나이상 나오는 문자열을 캡춰(저장)


# 여러 문자열 동시 캡춰
date_text = pd.Series(['2026-09-08','2025-12-25','2024-01-01'])
result = date_text.str.extract(r'(\d{4})-(\d{2})-(\d{2})')
print(result)

# category 타입과 cat 접근자
s = pd.Series( # 카테고리 들의 시리즈
    pd.Categorical(
        ['중','상','하','중'], # 데이터
        categories=['하','중','상','최상'] # 카테고리
    )
)
pp(s)

# 카테고리 목록, Index(['하', '중', '상', '최상'], dtype='str')
pp(s.cat.categories)
pp(s.cat.categories.to_list())

# Decoraton =  인덱스 안에 dtype과 리스트를 감싸고 있다

# cat.remove_unused_categories() : 사용되지 않는 범주 제거
pp(s.cat.categories)

#  '최상' 카테고리는 데이터가 없으므로 제거
s = s.cat.remove_unused_categories()
pp(s.cat.categories)

# cat.reorder_categories()
order = ['하','중','상'] # 새로운 카테고리로 사용할 리스트
# 범주의 순서를 다시 지정할때는 기존 범주를 반드시 모두 포함해야 함
s = s.cat.reorder_categories(order,ordered=True) # 순서 있는 카테고리로 재구성
pp(s.cat.categories)
pp(s.cat.ordered)  # True, 순서가 있다
pp(s.sort_values()) # 순서가 있어야 정렬이 가능
pp(s.cat.codes) # 하가 0 상이 2 (순서에 대한 번호가 내부정으로 설정)


data = pd.Series([1,2,3,4,5,6,7,8,51,100])
# pd.cut() :
# 값의 범위를 기준으로 구간을 나눔,
# 각 구간에 포함되는 데이터 개수는 다를 수 있음
cut_result = pd.cut(
    data,
    bins = 2,
    labels = ['낮은 구간','높은 구간']
)
# 낮은 구간 9개, 높은 구간 1개
pp(pd.DataFrame({'값': data, 'cut결과:' : cut_result}))
pp(cut_result.value_counts(sort=False))

#pd.qcut()
# - 데이터 개수 또는 분위수 (quantile)를 기준으로 구간을 나눔
# 각 구간에 들어가는 데이터 수는 가능한 비슷
qcut_result = pd.qcut(
    data,
    q = 2,
    labels = ['하위50%', '상위50%']
)
# 하위 5개, 상위 5개
pp(pd.DataFrame({'값': data, 'qcut결과:' : qcut_result}))
pp(qcut_result.value_counts(sort=False))


















































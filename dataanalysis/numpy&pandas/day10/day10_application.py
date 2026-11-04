# day10_application.py
# 주제:
import pandas as pd
from pathlib import Path

DATA_FILE = Path('online_orders.csv')

online_df = {
    '주문번호' : ['0001','0002','0003','0004','0005','0006','0007','0008',],
    '채널' : ['모바일','웹','모바일','웹','모바일','앱','앱','웹',],
    '상품분류': ['전자기기','생활용품','패션','전자기기','생활용품','패션','전자기기','패션',],
    '수량' : [1,3,2,1,5,1,2,3],
    '주문금액' : [120000,45000,78000,210000,65000,52000,330000,99000]
}
# 데이터 프레임 생성
online_df = pd.DataFrame(online_df)

#CSV 파일 생성
online_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# CSV > 데이터 프레임
df = pd.read_csv(DATA_FILE)
print(df)  # 전체 데이터
print(type(df)) # 타입,<class 'pandas.DataFrame'>

print('shape',df.shape)
print('ndim',df.ndim)    # 3
print('size',df.size)

print('columns',list(df.columns))   # 4
print('dtypes',df.dtypes)

order_data = df[['주문번호','상품분류','주문금액']]   #5. 데이터 프레임 출력
print(order_data)

order_price = df['주문금액']
print(type(order_price)) #6. <class 'pandas.Series'>

#7. 합계,평균,중앙값,최솟값,최댓값
print('합계',order_price.sum())
print('평균',order_price.mean())
print('중앙값',order_price.median())
print('최소값',order_price.min())
print('최대값',order_price.max())

#8.  기초통계
print(df.describe())

# 9. 채널별 주문건수
print(df['채널'].value_counts())

# 10. 상품분류 고유값 목록, 고유값 개수
a = df['상품분류'].unique()
print(f'고유값 목록 : {list(a)}')
print(f'고유값 개수 : {len(a)}')

# 11. 채널과 주문금액만 다시 읽은 DataFrame
select_df = pd.read_csv(DATA_FILE, encoding='utf-8-sig', usecols = ['채널','주문금액'])
print(select_df)

row = df.shape[0]    # 행
colum = df.shape[1]   # 열

avg = order_price.mean()   # 주문금액 평균

a = df['채널'].value_counts().idxmax() # 가장 많이 사용한 채널

print(f'데이터 크기 행:{row}, 열:{colum}')
print(f'주문금액 평균 : {avg:,.0f}원')
print(f'가장 많이 사용한 채널 : {a}')

































# day11_ex.py
# 주제:
import os

import pandas as pd

assets_dir = ('./assets'
              'os.makedirs(assets_dir,exist_ok=True)')

raw_path = os.path.join(assets_dir,'day11_orders_raw.csv')
clean_path = os.path.join(assets_dir,'day11_clean.csv')

order_data = {
    "주문ID": ["O2001", "O2002", "O2003", "O2004", "O2005", "O2002", "O2006", "O2007", "O2008"],
    "상품분류": ["노트북", "마우스", "키보드", "모니터", "헤드셋", "마우스", "웹캠", "노트북", "마우스"],
    "수량": ["1", "2", "unknown", "1", "2", "2", None, "1", "3"],
    "결제금액": ["1200000", "44000", "65000", "350000", "오류", "44000", "98000", "1350000", "66000"],
    "채널": ["웹", "앱", "앱", None, "웹", "앱", "앱", "웹", "앱"],
    "고객등급": ["Gold", "Silver", "Silver", "Gold", None, "Silver", "Bronze", "Gold", "Silver"],
}

source_df = pd.DataFrame(order_data)
source_df.to_csv(raw_path,index=False, encoding = 'utf-8-sig')

df = pd.read_csv(raw_path, encoding = 'utf-8-sig')

before_df = df.copy()

rows_before = before_df.shape[0]
missing_before = before_df.isna().sum().sum()

duplicate_order_before = before_df.duplicated(subset = ['주문ID']).sum()

pp(before_df.dtypes)
pp(before_df.isna().sum())
pp(duplicate_order_before)

app_orders = df.loc[
    df['채널'] == '앱',
    ['주문ID','수량',' 결제금액']
]

print(app_orders)

first_block = df.iloc[0:5, 0:4]
print(first_block)

df['수량'] = pd.to_numeric(df['수량'], errors='coerce')
df['결제금액'] = pd.to_numeric(df['결제금액'], errors='coerce')

pp(df['수량'].isna().sum()) # 수량 결측치 합계

quantity_median = df['수량'].median()

df['수량'] = df['수량'].fillna(quantity_median)

payment_median = df['결제금액'].median()

df['결제금액'] = df['결제금액'].fillna(payment_median)

df['채널'] = df['채널'].fillna('미확인')

grade_mode = df['고객등급'].mode()[0]

df['고객등급'] = df['고객등급'].fillna(grade_mode)

df = df.drop_duplicates(subset = ['주문ID'], keep = 'first')

df = df.reset_index(drop=True)

df['수량'] = df['수량'].astype('int64')
df['결제금액'] = df['결제금액'].astype('int64')

high_value_orders = df.loc[
    df['결제금액'] >= 50000,
    ['주문ID', '상품분류',' 수량','결제금액','채널']
]
pp(high_value_orders)


cleaning_log_rows = [
    {
        '항목' : '수량',
        '발견문제' : '문자열 unknown과 결측값 포함',
        '처리방법' : '숫자 변환 후 중앙값 대체',
        '처리근거' : '수량을 집계 가능한 숫자형으로 만들고 오류값의 영향을 제한'
    },
{
        '항목' : '결제금액',
        '발견문제' : '문자열 오류값 포함',
        '처리방법' : '숫자 변환 후 중앙값 대체',
        '처리근거' : '금액 계산이 가능하도록 숫자형을 통일하고 큰 금액의 영향이 적은 중앙값 사용'
    },
{
        '항목' : '채널',
        '발견문제' : '일부 채널 값 누락',
        '처리방법' : '미확인 으로 대체',
        '처리근거' : '실제 채널을 임의 추정하지 않고 누락 상태를 별도 범주로 유지'
    },
{
        '항목' : '주문ID 중복',
        '발견문제' : '02002',
        '처리방법' : '주문ID 기준 첫번째 행 유지',
        '처리근거' : '동일 주문ID가 동일 내용으로 반복되어 중복 저장으로 판단'
    }
]

# 전처리 근거 리스트 > 데이터프레임
cleaning_log_df = df.DataFrame(cleaning_log_rows)
pp(cleaning_log_df)

rows_after = df.shape[0]
missing_after = df.isna().sum().sum()
duplicate_order_after = df.duplicated(subset = ['주문ID']).sum()

# 전처리 전후 비교표

comparison_df = pd.DataFrame({
    '점검항목' : ['행 수','전체 결측치', '중복 주문ID'],
    '전처리전' : [rows_before, missing_before, duplicate_order_before],
    '전처리후' : [rows_after, missing_after, duplicate_order_before],
})
pp(comparison_df)

payment_count = df['결제금액'].count()
payment_mean = df['결제금액'].mean()
payment_min = df['결제금액'].min()
payment_max = df['결제금액'].max()

pp(f'count : {payment_count}')
pp(f'mean : {payment_mean}')
pp(f'min : {payment_min}')
pp(f'max : {payment_max}')

#최종 정제 데이터프레임 > CSV 파일
df.to_csv(clean_path, index=False, encoding = 'utf-8-sig')

















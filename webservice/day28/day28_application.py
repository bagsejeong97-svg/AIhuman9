# day28_application.py
# 주제:

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from include.graph_config import set_graph


set_graph()

data = {
'주문일': ['2026-09-01','2026-09-02','2026-09-03','2026-09-04','2026-09-05','2026-09-06','2026-09-07','2026-09-08','2026-09-09','2026-09-10',
             '2026-09-11','2026-09-12','2026-09-13','2026-09-14','2026-09-15','2026-09-16','2026-09-17','2026-09-18','2026-09-19','2026-09-20',
             '2026-09-21','2026-09-22','2026-09-23','2026-09-24','2026-09-25','2026-09-26','2026-09-27','2026-09-28','2026-09-29','2026-09-30'],

    '카테고리': ['식품','전자기기','의류','생활용품','식품','전자기기','의류','생활용품','식품','전자기기',
              '의류','생활용품','식품','전자기기','의류','생활용품','식품','전자기기','의류','생활용품',
              '식품','전자기기','의류','생활용품','식품','전자기기','의류','생활용품','식품','전자기기'],

    '주문금액': [15000,120000,45000,18000,23000,89000,52000,31000,27000,145000,
              38000,22000,19000,98000,61000,34000,26000,132000,47000,29000,
              21000,76000,55000,33000,24000,118000,42000,36000,28000,101000],

    '주문수량': [2,1,3,2,4,1,2,5,3,1,
              2,4,3,1,2,5,4,1,3,2,
              5,1,2,4,3,1,2,5,4,1]
}


df = pd.DataFrame(data)

st.title('온라인 쇼핑 주문 대시보드')


st.sidebar.header('카테고리 선택')
category = ['전체']+ list(df['카테고리'].unique())
mini_category = st.sidebar.selectbox(
    '선택',
    options=category
)


if mini_category == '전체':
    filtered_df = df
else:
    filtered_df = df[df['카테고리']==mini_category]


c1, c2, c3 = st.columns(3)
c1.metric(
    '주문건수',f'{len(filtered_df)}건')
c2.metric(
    '총 주문 금액',f'{filtered_df['주문금액'].sum():,}원'
)
c3.metric(
    '총 주문 수량',f'{filtered_df['주문수량'].sum()}개'
)

st.subheader('주문 목록')
st.dataframe(filtered_df,use_container_width=True,hide_index=True)

total_price = filtered_df.groupby('카테고리')['주문금액'].sum().sort_values(ascending=False)
fig, ax = plt.subplots()

if mini_category == '전체':
    # 전체 선택 시: 카테고리별 비교 막대그래프
    ax.bar(total_price.index, total_price.values)
    ax.set_title('카테고리별 총 주문 금액')
    ax.set_xlabel('카테고리')
    ax.set_ylabel('총 주문 금액')
else:
    # 특정 카테고리 선택 시: 날짜별 주문 금액 추이
    ax.bar(filtered_df['주문일'], filtered_df['주문금액'], color='skyblue')
    ax.set_title(f'[{mini_category}] 날짜별 주문 금액')
    ax.set_xlabel('주문일')
    ax.set_ylabel('주문 금액')
    plt.xticks(rotation=45)  # 날짜 라벨 겹침 방지

st.pyplot(fig)
plt.close(fig)

































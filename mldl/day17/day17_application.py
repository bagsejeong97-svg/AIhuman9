# day17_application.py
# 주제:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from include.graph_config import set_graph
from mldl.day16.day16_ex import RANDOM_STATE
from util.print_util import pp, pt, up

set_graph(10,8,13)
RANDOM_SEED = 42
df = pd.DataFrame({
'광고비(만원)': [80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380],
'매출(만원)': [1050, 1120, 1220, 1280, 1380, 1490, 1580, 1660, 1770, 1850, 1960, 2070, 2160, 2260, 2370, 2460]
})

X = df[['광고비(만원)']]

y = df['매출(만원)']

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.25,random_state=RANDOM_SEED)
model = LinearRegression()

model.fit(X_train,y_train)
prediction = model.predict(X_test)

# 절대 오차 MAE

mae = mean_absolute_error(y_test, prediction)

result = pd.DataFrame({
    '실제매출': y_test,
    '예측매출': prediction,
    '절대오차': mae
})
pp(result)
pp(f'MAE : {mae:.2f}')

# r2
r2 = r2_score(y_test, prediction)
pp(f'R2 : {r2}')

new_X = pd.DataFrame({
    '광고비(만원)':[400]
})
pred = model.predict(new_X)
pp(pred) # 광고비 400일때 예상 매출

line_x = pd.DataFrame({
    '광고비(만원)':sorted(df['광고비(만원)'])
})

line_y = model.predict(line_x)

plt.scatter(df['광고비(만원)'],df['매출(만원)'])
plt.plot(line_x['광고비(만원)'],line_y)
plt.xlabel('광고비')
plt.ylabel('매출')
plt.title('매출 예측값')
plt.show()

pp('MAE는 실제값에서 예측값이 얼마나 떨어져 있는 지나타낸다')
























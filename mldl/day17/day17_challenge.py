# day17_challenge.py
# 주제:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pylab as pl
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from include.graph_config import set_graph
from mldl.day16.day16_ex import RANDOM_STATE, FEATURES
from util.print_util import pp, pt, up

set_graph(10,8,13)

# df

df = pd.DataFrame({
'면적': [45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140],
'역거리': [18, 15, 14, 16, 12, 13, 10, 11, 9, 8, 10, 7, 6, 8, 5, 6, 4, 5, 3, 4],
'준공연수': [24, 20, 18, 22, 15, 17, 14, 12, 13, 10, 11, 9, 8, 10, 7, 6, 5, 7, 4, 3],
'가격': [33300, 37000, 41200, 40300, 46650, 46950, 52100, 53100, 56450, 60000, 59650, 64550, 66800, 68200, 71250, 73900, 76450, 78250, 81300, 83550],
})

# 랜덤 42 고정
RANDOM_SEED = 42

# 단순회귀
X = df[['면적']]
y = df['가격']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=RANDOM_SEED)
model = LinearRegression()
model.fit(X_train, y_train)
pred1 = model.predict(X_test)
# pp(pred1)


# 다중 선형회기
FEATURES = ['면적','역거리','준공연수']

X_m = df[FEATURES]
y_m = df['가격']
X_m_train,X_m_test,y_m_train,y_m_test = train_test_split(X_m, y_m, test_size=0.25, random_state=RANDOM_SEED)
model_m = LinearRegression()
model_m.fit(X_m_train, y_m_train)
pred2 = model_m.predict(X_m_test)
# pp(pred2)

# mae와 R2 비교
# 단순
mae = mean_absolute_error(y_test, pred1)
r2 = r2_score(y_test, pred1)

# 다중
mae_m = mean_absolute_error(y_m_test, pred2)
r2_m = r2_score(y_m_test, pred2)

result = pd.DataFrame({
    'MAE' : [mae, mae_m],
    'R2': [r2, r2_m]
},index = ['단순회귀','다중회귀'])
pp(result)
# 다중회기 모델 특성 회귀계수 df

coef_df = pd.DataFrame({
    '특성' : FEATURES,
    '회기계수': model_m.coef_,
})

#다중회귀모델 예측
new_X = pd.DataFrame({
    '면적':[100],
    '역거리':[5],
    '준공연수':[6]
})
a = model_m.predict(new_X)
pp(a)
#단순회귀 면적 가격 산점도와 회귀선

line_x = pd.DataFrame({
    '면적': sorted(df['면적'])
})
line_y = model.predict(line_x)

plt.scatter(df['면적'],df['가격'])
plt.plot(line_x['면적'],line_y)
plt.xlabel('면적')
plt.ylabel('가격')
plt.title('면적별 가격')
plt.show()



pp(f'mae는 0에 가까울수로 좋고,r2는 1에 가까울 수록좋기 때문에 \n{result}\n중에 조건에 더부합한것은 다중회기 모델이다')



















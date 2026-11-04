# day17_ex.py
# 주제: 선형회귀 모델링
from statistics import linear_regression

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

RANDOM_SEED = 42 #같은 train/test 분할 결과를 재현하기 위한 난수 시드값

data = {
    "경력년수": [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "프로젝트수": [1, 1, 2, 2, 3, 3, 4, 5, 5, 6, 7, 7, 8, 9, 10, 11],
    "교육시간": [20, 30, 35, 45, 55, 60, 70, 80, 95, 110, 125, 140, 150, 170, 185, 200],
    "연봉": [3000, 3200, 3400, 3650, 3900, 4150, 4450, 4700, 5100, 5500, 6000, 6400, 6850, 7300, 7700, 8200]
}

# 데이터 확인
df = pd.DataFrame(data)
pp(df.head())
pp(df.shape)
pp(df.describe()) # 기초통계

# 단순현형회귀용 X,y
X = df[['경력년수']]
y = df['연봉']

# train, test 분리
X_train,X_test,y_train, y_test = train_test_split(
    X, #feature
         y, #target
    test_size=0.2,
    # train_size = 0.8#train 80%, test 20%
    random_state=RANDOM_SEED, #랜덤 시드 고정
    shuffle=True # 분할전에 데이터를 무작위로 섞음(기본값)
)

# 선형회귀모델
model = LinearRegression()

#학습 데이터를 통해 회기계수와 절편을 계산
model.fit(X_train, y_train) # 80%데이터로 학습

pred = model.predict(X_test) # 20% feature 데이터로 예측
pp(pred) # 총16건의 25% y 예측값 = 4개

# y = ax + b
pp('coef_',model.coef_) #  회귀계수 a
pp('intercept_',model.intercept_) # 절편 b

#fit할때 사용한 feature 수
pp('n_features_in_',model.n_features_in_)

# R^2
pp('R^2:', model.score(X_test, y_test))

# 실제값과 예측값 비교 출력
result = pd.DataFrame({
    '실제연봉' : y_test,
    '예측연봉' : pred
})
pp(result)

# Residual(자차) = 실제값 - 예측값
result['오차'] = result['실제연봉'] - result['예측연봉']
pp(result)

# MAE
simple_mae = mean_absolute_error(y_test,pred)
pp(f'단순회귀: {simple_mae:.2f}')

simple_r2 = r2_score(y_test,pred)
pp(f'R^2: {simple_r2:.3f}')

# 새로운 feature로 연봉 예측
new_person = pd.DataFrame({
    '경력년수':[4,5]
})
new_salary = model.predict(new_person)
pp(f'예상연봉:{new_salary[0]:.0f}만원')


# 회기선 산점도 그래프
line_x = pd.DataFrame({
    '경력년수':sorted(df['경력년수'])
})
line_y = model.predict(line_x)

plt.scatter(df['경력년수'],df['연봉'])
plt.plot(line_x['경력년수'],line_y)
plt.xlabel('경력년수')
plt.ylabel('연봉')
plt.title('단순 선형회귀')
# plt.show()

# 다중 선형회귀
features = ['경력년수','프로젝트수','교육시간']

X_multi = df[features]

X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(
    X_multi, y, test_size=0.25, random_state=RANDOM_SEED,
)

multi_model = LinearRegression()
multi_model.fit(X_train_m, y_train_m)

multi_pred = multi_model.predict(X_test_m)

# 다중 선형회귀에서는 회귀계수가 여러개
coef_df = pd.DataFrame({
    '특성' :  features,
    '회기계수': multi_model.coef_,
})

pp(coef_df)
pp(multi_model.intercept_)

multi_mae = mean_absolute_error(y_test_m,multi_pred)
pp(multi_mae)

multi_r2 = r2_score(y_test_m,multi_pred)
pp(multi_r2)

# 모델별 평가 지표를 비교하기 위한 DataFrame 생성
comparison = pd.DataFrame({
    '모델' : ['단순선형회귀','다중선형호귀'],
    'MAE' : [simple_mae,multi_mae],
    'R2' : [simple_r2,multi_r2]
})
pp(comparison)

# 잔차
residuals = y_test_m.to_numpy() - multi_pred

# 잔차 그래프
plt.scatter(multi_pred, residuals)
plt.axhline(0, linestyle='--') # 잔차 0 기준선을 표시
plt.xlabel('예측값')
plt.ylabel('잔차')
plt.title('다중선형회귀 잔차')
plt.show()































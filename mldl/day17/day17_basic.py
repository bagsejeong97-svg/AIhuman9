# day17_basic.py
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

df = pd.DataFrame({
'공부시간': [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5],
'평가점수': [48, 52, 55, 60, 63, 68, 72, 75, 80, 83, 87, 91]
})

X = df[['공부시간']]
y = df['평가점수']


X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.25,random_state=42)

model = LinearRegression()

model.fit(X_train,y_train)
prediction = model.predict(X_test)
pp(prediction)

result = pd.DataFrame({
    '실제점수' : y_test,
    '예측점수' : prediction
})

pp(result)


new_X = pd.DataFrame({
    '공부시간' : [7]
})

pp(model.predict(new_X))

line_x = pd.DataFrame({
    '공부시간':sorted(df['공부시간'])
})
line_y = model.predict(line_x)

plt.scatter(df['공부시간'],df['평가점수'])
plt.plot(line_x['공부시간'],line_y)
plt.xlabel('공부시간')
plt.ylabel('평가점수')
plt.title('공부시간에 따른 평가점수')
plt.show()


































# day16_basic.py
# 주제:
from sklearn.metrics import classification_report

from mldl.day16.day16_ex import FEATURES, TARGET
from util.print_util import pp, pt, up
import pandas as pd
import sklearn
from sklearn.datasets import load_iris
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.utils.multiclass import type_of_target
from sklearn.utils.validation import check_X_y

df = pd.DataFrame({
'distance_km'      : [2.5, 4.1, 6.8, 3.2, 10.5, 8.7, 5.4, 12.1],
'package_count'    : [1, 3, 2, 1, 5, 4, 2, 6],
'traffic_index'   : [3, 6, 8, 4, 9, 7, 5, 10],
'rain_mm'          : [0, 0, 4, 12, 0, 7, 1, 15],
'delivery_minutes' : [18.5, 29.2, 46.8, 35.1, 61.4, 58.7, 34.6, 79.3]
})

FEATURES = ['distance_km','package_count','traffic_index','rain_mm']

TARGET = 'delivery_minutes'

X = df[FEATURES]
y = df[TARGET]

# x,y shape 출력
pp(X.shape)
pp(y.shape)

# x,y 컬럼명과 이름
pp(list(X.columns))
pp(y.name)

# continuous
pp(type_of_target(y))

pp('이 문제는 회귀 유형으로 숫자로 계산되어져 결과를 예측할수 있기 떄문에')























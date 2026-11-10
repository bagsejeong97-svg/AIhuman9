# day18_ex.py
# 분류모델 : logisticregression, knn
from include.graph_config import set_graph

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from mldl.day16.day16_ex import RANDOM_STATE
from util.print_util import pp, up

set_graph(10,8,13)

RANDOM_STATE = 42

# 임계값(threshold:클래스를 구분하기위한 기준값)을 기준으로 확률을 0/1 클래스로 반환
probability = np.array([0.12,0.47,0.50,0.81]) # 1차원 넘파이 배열
pred_class = (probability >= 0.5).astype(int)
# 0.5이상이면 True = > 1로 변환 / 0.5이하면 False >0으로 변환
pp(pred_class)


X_raw, y = make_classification(
    n_samples=500,  #전체데이터 수
    n_features=4,   # 전체 특성수
    n_informative=3, # 실제분류에 유용한 특성수
    n_redundant=0, # 다른 특성의 조합으로 만들어지는 중복 성격 특성 수
    class_sep=1.0, # 클래스 사이 분리정도
    flip_y=0.05, # 일부 label을 임의로 뒤집는 비율 5%
    random_state=RANDOM_STATE
)

columns = ['방문빈도지수','콘텐츠반응지수','헤택민감도지수','최근활동지수']

X = pd.DataFrame(X_raw, columns=columns)
y = pd.Series(y, name ='이탈여부')

pp(X.shape)
pp('[클래스분포]')
pp(y.value_counts())

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=RANDOM_STATE,
    shuffle=True,
    stratify=y
)
pp(X_train)
pp(X_test)
pp(y_train)
pp(y_test)

# LogisticRegression : 선형결함을 확률로 변환하는 대표적인 분류
logistic = LogisticRegression(
    max_iter=1000, # 최적화 알고리즘 최대 반복 횟수
    C=1.0, # 규제 강도의 역수, 작을수록 규제가 강해짐
    solver='lbfgs', # 계수 최적화 하는 알고리즘
    random_state=RANDOM_STATE # 최적화 알고리즘에서 난수 재현성 확보를 위한 랜덤 시드값
)
# 학습
logistic.fit(X_train, y_train)

# 예측 클래스
logistic_pred = logistic.predict(X_test)
pp(logistic_pred[:10]) # 클래스, 1차원 배열

#  예측 : 확률
logistic_proba = logistic.predict_proba(X_test)
pp(logistic_proba[:10]) # 클래스일 확률, 2차원배열

# classes_ : 학습 후 각 열이 어떤 클래스인지를 저장
pp(logistic.classes_) #[0:1] : 클래스 2개

# coef_ : 학습 후 각 패쳐의 학습된 계수
pp(logistic.coef_)

# 정확도(Accuracy) : 분류 모델에서는 score가 정확도
pp(logistic.score(X_test, y_test))

# 전체 예측 중 정답과 일치한 비율
logistic_acc = accuracy_score(y_test, logistic_pred)
pp(logistic_acc)

#오분류 데이터 확인
result = X_test.copy()
result['정답'] = y_test
result['예측'] = logistic_pred
wrong = result['정답'] != result['예측'] # 불리언 시리즈
pp(wrong)

# KneighborsClassifier: 가까운 K개의 이웃 투표로 클래스를 결정

knn = KNeighborsClassifier(
    n_neighbors=5, #참고할 가장 가까운 이웃의 수(K)
    weights='uniform', # 각 이웃의 가중치 동일하게 적용
    metric = 'minkowski', # 거리 계산 알고리즘
    p=2 #Euclidean Distance: 두 점사이의 거리(직선거리)
    # p=1 # Manhattan Distance : 사용된 축들의 거리의 합(기본값)
)
#학습
knn.fit(X_train, y_train)

# 예측 : 확률
pp(knn.predict_proba(X_test.iloc[:10]))

#예측 : 분류
knn_pred = knn.predict(X_test)

#정확도
pp(accuracy_score(y_test, knn_pred))

# 정확도 : KNN에서도 score()가 정확도를 가리킴
pp(knn.score(X_test, y_test))

# KNN이 학습한 클래스 목록
pp(knn.classes_) #[0 1]

# Kneighbors() : 지정 데이터에서 가까운 이웃의 거리와 학습 데이터 인덱스 반환
distances, indices = knn.kneighbors(X_test.iloc[:1])
pp('가까운 이웃의 거리', distances,'\n 먼이웃의 거리:', indices)

# K값을 달리해서 정확도 비교
for k in [1,3,5,7,9]:
    model =  KNeighborsClassifier(n_neighbors=k )
    model.fit(X_train, y_train)
    pp('k:',k,'accuracy:',model.score(X_test, y_test))

# 신규데이터에 대한 클래스와 확률 예측
new_customers = pd.DataFrame([
    [0.8,-0.2,0.5,-1.1],
    [-1.0,0.7,-0.4,0.9]
])

new_result = new_customers.copy()
new_result['이탈예측'] = logistic.predict(new_customers)
new_result['이탈확률'] = logistic.predict_proba(new_customers)[:,1] # 클래스 1확률만
pp(new_result)

# 분류 결과의 일부 패쳐를 2차원 산점도로 시각화
df = X.copy()
df['이탈여부'] = y
plt.scatter(
    df['방문빈도지수'],
    df['콘텐츠반응지수'],
    c=df['이탈여부'],
    alpha=0.6
)
plt.title('방문빈도지수/콘텐츠반응지수 산점도(고객이탈 클래스 분포)')
plt.xlabel('방문빈도지수')
plt.ylabel('콘텐츠반응지수')
plt.legend('ㄴㄴ')
plt.tight_layout()
plt.show()


























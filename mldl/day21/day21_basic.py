# day21_basic.py
# 주제:
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

from util.print_util import pp

X_array, y = make_classification(
    n_samples=600,       # 전체 설비 측정 건수
    n_features=5,        # 센서 특성 개수
    n_informative=4,     # 분류에 실제 정보를 주는 특성 수
    n_redundant=0,       # 다른 특성의 조합으로 만들어지는 중복 특성 수
    class_sep=1.2,       # 두 클래스 사이의 분리 정도
    random_state=20
)
X = pd.DataFrame(X_array, columns=["진동", "온도", "압력", "전류", "소음"])
X["진동"] = 1000      # 큰 단위의 센서를 가정해 스케일 차이를 만듦
X["소음"]= 0.01      # 매우 작은 단위의 센서를 가정
pp("특성별 표준편차", X.std().round(3))



X_train, X_test, y_train, y_test = train_test_split(
    X,y,
    test_size=0.25,
    stratify=y,
    random_state=20,
)

# 스캐일링 전
knn_raw = KNeighborsClassifier(
    n_neighbors=7,
)

knn_raw.fit(X_train, y_train)
knn_pred = knn_raw.predict(X_test)
acc_raw = accuracy_score(y_test, knn_pred)

# 스케일링 후

scaler = StandardScaler(
    copy=True,
    with_mean=True,
    with_std=True,
)
X_train_scaled = scaler.fit_transform(X_train)

X_test_scaled = scaler.transform(X_test)

knn_scaled = KNeighborsClassifier(
    n_neighbors=7,
)

knn_scaled.fit(X_train_scaled, y_train)
knn_pred = knn_scaled.predict(X_test_scaled)
acc_scaled = accuracy_score(y_test, knn_pred)

pp(f'스케일링전 정확도: {acc_raw:.4f}')
pp(f'스케일링후 정확도: {acc_scaled:.4f}')

# scaler.mean과 scaler.scale

# fit 에서 계산한 특성별 평균
s_mean = scaler.mean_[:5]

# 표준화시 각 특성을 나누는 값
s_scaler = scaler.scale_[:5]

pp(s_mean, s_scaler)










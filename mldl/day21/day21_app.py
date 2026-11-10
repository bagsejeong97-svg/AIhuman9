# day21_application.py

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from util.print_util import pp, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

# 고객 이탈 가상 데이터 생성
X_array, y = make_classification(
    n_samples=1000,       # 고객 수
    n_features=8,         # 고객 행동/거래 특성 수
    n_informative=6,      # 실제 분류에 정보를 주는 특성 수
    n_redundant=1,        # 다른 특성 조합으로 표현되는 중복 특성 수
    weights=[0.7, 0.3],   # 유지 70%, 이탈 30%의 불균형을 가정
    class_sep=1.0,
    random_state=20
)
pp(X_array)
pp(y)

columns = ["이용기간", "월사용량", "문의횟수", "평균결제액", "할인율", "접속일수", "콘텐츠수", "만족도"]

X = pd.DataFrame(X_array, columns=columns)

X["평균결제액"] = X["평균결제액"] * 50000 + 80000  # 원 단위 결제액처럼 큰 스케일을 구성
X["할인율"] = X["할인율"] * 0.05 + 0.1            # 비율 데이터처럼 작은 스케일을 구성
pp(X.shape)

pp("이탈 비율")
pp(pd.Series(y).value_counts(normalize=True).sort_index().round(3))

# 전처리와 분류 모델을 Pipeline으로 연결
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(max_iter=3000))
])
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=20
)

# Accuracy, f1
accuracy_scores = cross_val_score(
    pipe,
    X,
    y,
    cv=cv,
    scoring='accuracy'
)
f1_scores = cross_val_score(
    pipe,
    X,
    y,
    cv=cv,
    scoring='f1'
)

pp('Fold별 Accuracy: ', accuracy_scores.round(4))
pp('Accuracy 평균 / 표준편차: ', \
   round(accuracy_scores.mean(), 4), \
   round(accuracy_scores.std(), 4)
)

# train / validation 정확도 차이
cv_result = cross_validate(
    pipe,
    X,
    y,
    cv=cv,
    scoring='accuracy',
    return_train_score=True
)
train_mean = cv_result['train_score'].mean()
valid_mean = cv_result['test_score'].mean()
pp('Train Accuracy 평균: ', round(train_mean, 4))
pp('Validation Accuracy 평균: ', round(valid_mean, 4))
pp ('평균 GAP: ', round(train_mean - valid_mean, 4))

# Hold-out 방식 평가
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=20,
    stratify=y
)
pipe.fit(X_train, y_train)
pred = pipe.predict(X_test)
holdout_accuracy = accuracy_score(y_test, pred)
holdout_f1 = f1_score(y_test, pred)
pp('Hold-out Accuracy: ', round(holdout_accuracy, 4))
pp('Hold-out F1: ', round(holdout_f1, 4))
pp('Accuracy 차이: Hold-out vs CV: ', \
   round(holdout_accuracy - accuracy_scores.mean(), 4)
)
pp('F1 차이: Hold-out vs CV: ', \
    round(holdout_f1 - f1_scores.mean(), 4)
)

pp('[해석]')
pp('Hold-out은 한 번의 분할 결과이므로 어떤 고객이 Test에 포함되는지에 따라 점수가 달라질 수 있음')
pp('CV는 서로 다른 검증 Fold의 결과를 평균내므로 한 번의 분할보다 안정적인 일반화 성능 추정에 유리함')

# Fold별 F1 점수 시각화
plt.plot(range(1, 6), f1_scores, marker='o')
plt.axhline(f1_scores.mean(), linestyle='--', label=f'mean={f1_scores.mean():.3f}')
plt.xticks(range(1, 6))
plt.xlabel('Fold')
plt.ylabel('F1 Score')
plt.title('Customer Churn 5-Fold F1')
plt.legend()
plt.tight_layout()
plt.show()

up(5)






























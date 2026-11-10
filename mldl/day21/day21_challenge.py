# day21_challenge.py
# 대출 연체 위험 예측을 위한 KNN Pipeline과 GridSearchCV 튜닝

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from util.print_util import pp
from include.graph_config import set_graph

set_graph(8, 6, 13)

# 연체 위험 가상 데이터 생성
X_array, y = make_classification(
    n_samples=1500,
    n_features=10,
    n_informative=7,
    n_redundant=1,
    weights=[0.82, 0.18],  # 정상 82%, 연체 18%의 불균형을 가정
    class_sep=0.9,
    flip_y=0.02,          # 실제 데이터의 라벨 오류/잡음을 일부 반영
    random_state=20
)
columns = ["연소득", "부채비율", "신용기간", "최근연체수", "카드사용률", "대출건수", "월상환액", "거래기간", "계좌잔액", "신용조회수"]
X = pd.DataFrame(X_array, columns=columns)
X["연소득"] = X["연소득"] * 20_000_000 + 50_000_000
X["월상환액"] = X["월상환액"] * 500_000 + 1_500_000
X["계좌잔액"] = X["계좌잔액"] * 10_000_000 + 20_000_000
pp("데이터 크기", X.shape)
pp("클래스 비율", pd.Series(y).value_counts(normalize=True).sort_index().round(3))
pp("특성별 표준편차", X.std().round(2))

# train / test
X_train, X_test, y_train, y_test = train_test_split(
    X,y,
    test_size=0.2,
    random_state=20,
    stratify=y
)

# 비교 기준이 될 기본 KNN Pipeline
baseline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', KNeighborsClassifier(n_neighbors=5)),
])

baseline.fit(X_train, y_train)
baseline_pred = baseline.predict(X_test)
baseline_f1 = f1_score(y_test, baseline_pred)
pp('기본 모델 Test F1:', round(baseline_f1, 4))

# GridSearch 대상 Pipeline과 교차검증 설정
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', KNeighborsClassifier()),
])
cv = StratifiedKFold(n_splits=5, random_state=20, shuffle=True)

# 5 * 2 * 2 = 20가지 조합
param_grid = {
    'model__n_neighbors': [3,5,7,9,13],
    # uniform: 동일 가중치, distance:거리 기반 가중치
    'model__weights': ['uniform', 'distance'],
    'model__p':[1,2] # 1:manhattan(기본값) , 2:euclidean
}

grid = GridSearchCV(
    estimator=pipe,
    param_grid=param_grid,
    # 소수 클래스인 연체 탐지의 precision/recall 균형을 반영하기 위해 f1 사용
    scoring='f1_macro',
    cv=cv,
    n_jobs=-1,
    return_train_score=True
)
grid.fit(X_train, y_train)

pp('최적 파라미터 :', grid.best_params_)
pp('최적 CV F1:',round(grid.best_score_,4))

# 탐지 결과 상위 조합 확인
result_df = pd.DataFrame(grid.cv_results_)
summary = result_df[[
    'param_model__n_neighbors',
    'param_model__weights',
    'param_model__p',
    'mean_train_score',
    'mean_test_score',
    'std_train_score',
    'std_test_score',
    'rank_test_score',
]].sort_values(by=['rank_test_score','param_model__n_neighbors'])

pp('상위 10개 조합:',summary.head(10).round(4))

# 최종 모델의 최종 Test 성능
best_model = grid.best_estimator_
best_pred = best_model.predict(X_test)
accuracy = accuracy_score(y_test, best_pred)
precision = precision_score(y_test, best_pred)
recall = recall_score(y_test, best_pred)
f1_score = f1_score(y_test, best_pred)

pp('최적 모델 TEST ACCURACY:', round(accuracy,4))
pp('최적 모델 TEST precision:', round(precision,4))
pp('최적 모델 TEST Recall:', round(recall,4))
pp('최적 모델 TEST F1:', round(f1_score,4))
pp('F1 개선량:', round(f1_score-baseline_f1,4))
pp('Confusion Matrix:')
pp(confusion_matrix(y_test, best_pred))

# p=2인 결과만 사용해 n_neighbors와 weighs에 따른 CV F1 비교
plot_df = result_df[result_df['param_model__p'].astype(int)==2].copy()
plot_df['n_neighbors'] = plot_df['param_model__n_neighbors'].astype(int)

for weights, group in plot_df.groupby('param_model__weights'):
    group = group.sort_values(by='n_neighbors')
    plt.plot(
        group['n_neighbors'],
        group['mean_test_score'],
        marker='o',
        label=str(weights)
    )
plt.xlabel('n_neighbors')
plt.ylabel('Mean CV F1')
plt.title('Loan Default KNN GridSearchCV')
plt.legend(title='weights')
plt.tight_layout()
plt.show()

# 업무 관점 추가 검토
pp('Recall 개선 검토 항목',[
    'GridSearchCV의 scoring 을 recall 또는 f=beta로 바꾸어 탐색 목적을 조정',
    '연체 클래스의 불균형 정도와 표본 수를 확인 하고 재표본화 전략 검토',
    '예측 활률 또는 거리 기반 점수의 의사결정 임곅밧을 업무 비용에 맞게 조절',
    '연체 위험을 설명하는 추가 특성을 확보하고 데이터 품질을 점검',
    'KNN와 LogisticRegression, Tree Ensemble 등 다른 모델과 성능 비교'
])












































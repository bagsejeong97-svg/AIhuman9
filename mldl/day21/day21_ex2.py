# day21_ex2.py
# StandardScaler, 교차검증, Pipeline, GridSearchCV

from util.print_util import pp, up
from include.graph_config import set_graph
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer # 유방암 이진분류 예제 데이터셋 로드
from sklearn.preprocessing import StandardScaler # 특성별 평균 0·표준편차 1 수준으로 표준화
from sklearn.linear_model import LogisticRegression # 클래스 확률을 학습하는 로지스틱 회귀 분류 모델 사용
from sklearn.pipeline import Pipeline, make_pipeline # 전처리와 모델 학습 단계를 하나의 흐름으로 연결
# 데이터 분할·교차검증·하이퍼파라미터 탐색 기능 사용
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV

set_graph(10, 8, 13)

# 데이터 준비
data = load_breast_cancer(as_frame=True)

# X, y
X = data.data
y = data.target
pp(X.shape)
pp(X.head(5))
pp(y.head(5))

# train / test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# StandarScaler 생성
scaler = StandardScaler(
    copy=True, # 원본 배열을 보존하고 변환 결과를 새로 생성
    with_mean=True, # 각 특성의 평균을 0에 가깝게 이동
    with_std=True # 각 특성의 값을 표준편차로 나눠서 스케일 조정
)
pp(scaler.get_params()) # 하이퍼파라미터 딕셔너리 출력

# 학습 데이터에서 평균과 표준편차를 계산하고 표준화
X_train_scaled = scaler.fit_transform(X_train)

# 학습 데이터에서 구한 스케일 기준을 테스트 데이터에 적용
X_test_scaled = scaler.transform(X_test)

pp('변환 전 평균 일부: ', np.round(X_train.mean().to_numpy()[:5], 3))
pp('변환 후 평균 일부: ', np.round(X_train_scaled.mean(axis=0)[:5], 3))
pp('변환 후 표준편차 일부: ', np.round(X_train_scaled.std(axis=0)[:5], 3))

# StandardScaler 학습 후 속성

# fit에서 계산한 특성별 평균
pp('mean_ 일부: ', np.round(scaler.mean_[:5], 3))

# fit에서 계산한 특성별 분산
pp('var_ 일부: ', np.round(scaler.var_[:5], 3))

# 표준화할 때 각 특성을 나누는 스케일 값
pp('scale_ 일부: ', np.round(scaler.scale_[:5], 3))

# fit에 전달된 입력특성의 개수
pp('n_features_in_: ', scaler.n_features_in_)

# DataFrame으로 학습할 때 기억한 입력 특성명
pp('feature_names_in_ 일부: ', scaler.feature_names_in_[:5])

# 표준화된 데이터를 원래 단위로 역변환
restored = scaler.inverse_transform(X_train_scaled[:2])
pp('복원값 일부: ', np.round(restored[:, :5], 3))

# 스케일링 전후 LogisticRegression 성능
raw_model = LogisticRegression(max_iter=5000, solver='liblinear')
raw_model.fit(X_train, y_train)
scaled_model = LogisticRegression(max_iter=5000, solver='liblinear')
scaled_model.fit(X_train_scaled, y_train)
pp('스케일링 전 정확도: ', round(raw_model.score(X_test, y_test), 4))
pp('스케일링 후 정확도: ', round(scaled_model.score(X_test_scaled, y_test), 4))

# Pipeline 직접 생성
pipe = Pipeline(steps=[
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(max_iter=5000, solver='liblinear'))
])
pp('Pipeline steps: ', pipe.steps) # 리스트내 튜플
pp('Pipeline named_steps: ', pipe.named_steps) # 딕셔너리
pp('Pipeline 파라미터 일부: ', {
    'model__C': pipe.get_params()['model__C'],
    'model__max_iter': pipe.get_params()['model__max_iter'],
    'scaler__with_mean': pipe.get_params()['scaler__with_mean']
})

# Pipeline내부에서 표준화 후 분류 모델까지 순서대로 학습
pipe.fit(X_train, y_train)

pp('Pipeline 테스트 정확도: ', round(pipe.score(X_test, y_test), 4))
pp('Pipeline 예측: ', pipe.predict(X_test.iloc[:5]))
pp('Pipeline 예측 확률: ', np.round(pipe.predict_proba(X_test.iloc[:3]), 4))

# make_pipeline 단계 이름 자동 생성
auto_pipe = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=5000, solver='liblinear')
)
pp('make_pipeline steps: ', auto_pipe.steps)

auto_pipe.fit(X_train, y_train)

pp('make_pipeline 정확도: ', round(auto_pipe.score(X_test, y_test), 4))

# cross_val_score
scores = cross_val_score(
    auto_pipe,
    X,
    y,
    cv=5, # 폴드 5개
    scoring='accuracy', # 지표 : 정확도
    n_jobs=-1
)
pp('5-Fold 점수: ', np.round(scores,4))
pp('평균 정확도: ', round(scores.mean(), 4))
pp('표준편차: ', round(scores.std(), 4))

# StratifiedKFold
cv = StratifiedKFold(
    n_splits=5, # 폴드 5개
    shuffle=True, # 분할 전에 샘플을 무작위로 섞음
    random_state=42
)
cv_scores = cross_val_score(
    auto_pipe,
    X,
    y,
    cv=cv,
    scoring='accuracy',
    n_jobs=-1
)
pp('StratifiedKFold 점수: ', np.round(cv_scores, 4))

# set_params()
tuned_pipe = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=5000, solver='liblinear')
)
# 이미 생성된 파이프라인의 파라미터들을 생성 후에 설정
tuned_pipe.set_params(
    logisticregression__C = 0.1,
    standardscaler__with_mean = True
)

pp('set_params 적용 C: ', tuned_pipe.get_params()['logisticregression__C'])

# GridSearchCV로 하이퍼파라미터 탐색
param_grid = { # 총 8개 조합
    'logisticregression__C': [0.01, 0.1, 1, 10], # 4개
    'logisticregression__penalty': ['l1', 'l2'] # 2개
}
grid = GridSearchCV(
    estimator=tuned_pipe, # 모델 또는 파이프라인
    param_grid=param_grid, # 하이퍼파라미터 조합을 가진 딕셔너리
    scoring='accuracy', # 지표 : 정확도
    cv=cv,
    n_jobs=-1,
    refit=True, # 최적 조합을 찾은 뒤 전체 학습 데이터로 다시 학습
    return_train_score=True # 각 조합의 학습 점수도 cv_results_에 저장
)
pp('GridSearchCV 파라미터: ', {
    'scoring': grid.scoring,
    'cv': grid.cv,
    'refit': grid.refit
})

# 모든 파라미터 조합을 교차검증하여 최적 조합 탐색
grid.fit(X_train, y_train)

# GridSearchCV 학습 후 속성

# 교차검증 결과 가장 좋은 성능을 낸 파라미터 조합
pp('best_params_: ', grid.best_params_)

# 최적 파라미터 조합의 평균 교차검증 점수
pp('best_score_: ', round(grid.best_score_, 4))

# 최적 파라미터로 다시 학습된 최종 estimator
pp('best_estimator_: ', grid.best_estimator_)

# cv_results_에서 최적 조합이 위치한 행 인덱스
pp('best_index_: ', grid.best_index_)

# estimator가 정의한 기본 평가 지표를 계산
pp('테스트 score(): ', round(grid.score(X_test, y_test), 4))

# 학습된 모델로 새로운 입력의 예측값 또는 클래스를 계산
pp('best estimator 예측: ', grid.predict(X_test.iloc[:5]))

# cv_results_에서 주요 결과 추출
cv_result = pd.DataFrame(grid.cv_results_)
cols = [
    'params',
    'mean_train_score',
    'mean_test_score',
    'std_test_score',
    'rank_test_score'
]
pp(cv_result[cols].sort_values('rank_test_score').head().round(4))





























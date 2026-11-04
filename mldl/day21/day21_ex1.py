# day21_ex1.py
# 스케일링, 교차검증, pipeline, 과적합, 하이퍼파라미터 튜닝

'''
# 1. 전체 흐름

1) 데이터 준비
2) 학습/테스트 데이터 분리
3) 스케일링(Scaling)
4) 모델 학습
5) 교차검증(Cross Validation)
6) Pipeline 구성
7) 과적합(Overfitting) 확인
8) 하이퍼파라미터(Hyper Parameter) 조정
9) GridSearch CV 로 최적 하이퍼파라미터 조합/ 모델 탐색


#  2. 스케일링

- 스케일링은 서로 다른 범위를 가진 특성의 값 범위를 비슷한 수준으로 맞추는 전처리 과정
- 예) 키 : 150~190, 연봉:30,000,000~1,000,000,000
- 연봉 값이 수치적으로 매우크기 떄문에 거리 기반 알고리즘에서는 연봉의 영향력이
- 지나치게 커질수 있음
- 스케일링 중요한 알고리즘
- : KNN, K-means, SVM, Logistic Regression, Neural Network, PCA
- 영향이 상대적으로 적은 알고리즘
- : Decision Tree, Random Forest, Gradient Boosting 계열


# 3. standardScaler

- StandardScaler는 데이터를 평균0, 표준편차 1인 형태로 변환
- 공식 : z = (x - 평균)/ 표준편차
- 예) 평균이 70,표준편차기 10, 원래 점수는 80
        z = (80 - 70)/10 = 1  (즉, 평균보다 표준편차 1만큼 높은값을 의미)
- 주요 메소드
- fit(X): X데이터에서 평균과 표준편차를 계산(train데이터 셋에만 해야함!!!)
- transform(X) : fit(X)에서 계산한 평균과 표준편차를 이용해 데이터를 변환
- fit_transform(X) : fit(X) 수행 후 transform(X) 수행
- inverse_transform(X) :  스케일링 된 데이터를 원래 값으로 복원


# 4. fit과 transform 을 구분해야 하는 이유
- 학습 데이터에서는 fit_transform을 사용하고 테스트 데이터에는 transform()만 사용해여함
- 테스트 데이터에서도 평균과 표준편차를 다시 계산하면 테스트 데이터의 정보를 모델 평가에 사용하므로 과적합 문제 발생

# 5. 데이터 누수 (Data Leakage)
- 모델 학습 과정에서 원래 알 수 없어애 하는 테스트 데이터의 정보가 학습 과정에 들어가는 문제
- 전체 데이터에 먼저 StandardScaler를 적용한 후 train/test 분리하면 테스트 데이터의 평균과 표준편차 정보가 학습데이터에 반영될수 있음 >> 과적합 문제 발생 가능

# 6. 교차검증 (Cross Validation)
- 데이터를 여러 부분으로 나누고 학습용과 검증용 역할을 번갈아 수행하면서 모델을 여러번 평가하는 방법
    동일 데이터 > 여러번 분리 > 여러번 평가

- 목적 : 한번의 train/test 분리 결과에 의존하지 않도록 해서 모델의 일반화 성능을 더 안정적으로 평가하기 위해 사용함

# 7. k-fold CV
- K-Fold는 데이터를 K개로 나눈 후 각 Fold를 한번씩 검증 데이터로 사용
- 예) 5개의 폴드 > 1개는 검증, 나머지는 학습.... 번갈아서
- 총5개의 평가 점수가 생성되고 일반적으로 평균값을 최종 성능 지표로 사용

# 8. cross_val_score()
- 교차검증을 간단히 수행하는 함수
- 주요 파라미터
    estimator : 평가할 머신러닝 모델, X:입력데이터, y: 정답데이터, cv: 교차검증 회숫
    scoring: 평가 기준
            분류 :(accuracy,precision,recall,f1,roc_auc)
            회기 : r2,neg_mean_absolute_error,neg_mean_squared_error,

# 9 . StratifiedKFold
- 분류 문제에서 각 Fold가 원래 데이터의 클래스 비율로 최대한 유지하도록 나누는 방식
- 예를 들어 전체 데이터가 정상 80%, 불량 20% 라면 각 Fold도 가능하면
정상 80% , 불량 20% 비율을 유지하도록 나눔
- 클래스 비율이 불균형한 데이터에서 일반 K-Fold 를 사용하면 특정 Fold에 특정클래스가 너무 많거나 너무 적어지는 문제가 발생
- 주요 파라미터
 n_splits:Fold 개수, shuffle: 데이터를 섞을지 여부,
 random_state: 재현성 확보를 위한 난수시드값

#10. Pipeline
- 여러 전처리 단계와 머신러닝 모델을 하나의 작업 흐름으로 연결하는 기능
- 파이프라인을 사용하는 이유
    1) 코드가 간결해 짐
    2) 전처리와 모델을 하나의 객체처럼 묶어서 사용할 수 있음
    3) 교차검증 과정에서 데이터 누수를 방지 할 수 있음
    4) GridSearchCV와 결힙하기 쉬움
    5) 실무 배포 시 동일한 전처리 과정을 보장하기 쉬움
- make_pipeline() : 각 단계에서 이름을 자동으로 생성하면서 파이프라인을 생성
- Pipeline() : 각 단계의 이름을 지정하면서 파이프라인을 생성

# 11. 일반화 (Generalization)
- 학습에 사용하지 않은 새로운 데이터에서도 좋은 성능을 유지하는 능력 => 머신러능의 최종 목표!!!
- 머신러닝의 궁극의 목표는 학습 데이터의 저수를 높이는 것이 아니라 일반화 성능을 높이는 것

# 12. Bias와 Variance
- Bias(편향) : 모델이 지나치게 단순해서 발생하는 오차, Bias 높음 => 과소적합
- Variance(분산) : 학습 데이터 변화에 모델이 지나치게 민감한 정도, Variance 높음 => 과적합

# 13. 하이퍼 파라미터 (Hyper Parameter)
- 모델이 학습하기 전에 사람이 설정해야 하는 값, 즉 모델의 설정 입력값
- LogisticRegression : C, max_iter, solver
- DecisionTreeClassifier : max_depth, min_samples_split, min_samples_leaf ...
- KNeighborsClassifier : n_neighbors, leaf_size, weights ...

# 14. 파라미터 (Parameter)
- 모델이 학습 과정에서 자동으로 학습하는 값
- LinearRegression : coef_, intercept_ ...

# 15. 튜닝(Tunning)
- 하이퍼파라미터의 값을 변경하면서 가장 좋은 성능을 내는 조합을 찾는 과정
- 모든 하이퍼파라미터의 값의 범위를 다 사용하지 말고 적절한 범위를 사용해서 조합을 찾는게 중요

# 16. GridSearchCV
- GridSearch + Cross Validation
- GridSearch : 하이퍼파라미터들의 조합 생성해서 결합
- Cross Validation : 교차 검증

# 17. Pipeline 의 하이퍼파라미터 이름
- '단계이름__파라미터이름' 의 형식으로 사용
- 일반적으로 딕셔너리를 생성해서 키를'단계이름__파라미터이름' 으로 값을 하이퍼파라미터의 개별값들의 리스트로 지정

# 18. GridSEarchCV 주요 속성
- best_params_ : 가장 좋은 하이퍼파라미터 조합
- best_score_ : 가장 좋은 교차검증 평가 점수
- best_estimator_ : 가장 좋은 하이퍼파라미터가 적용된 최종 모델
- cv_results_ : 모든 조합의 평가 결과

# 19. GridSearchCV
- estimator : 튜닝할 모델 또는 Pipeline
- param_grid : 탐색할 하이퍼파라미터 후보
- cv : 교차검증 회수 = 폴드수
- scoring : 평가기준, 여러개면 리스트
- n_jobs : 병렬 처리에 사용할 CPU 코어 수
- verbose : 진행 상황 출력 수준

# 20. Regularization (정규화)
- 모델이 지나치게 복잡해지는 것을 방지하기 위해 가중치 크기 등에 패널티를 부여하는 방법
- 대표 방식
    1) L1 Regularization
        일부 가중치를 0으로 만듬 = 특정 Feature를 사용하지 않음
    2) L2 Regularization
        큰 가중치를 줄이는 방향으로 학습
        LogisticRegression의 기본 규제 방식

# 21. solver
- LogisticRegression에서 최적의 가중치를 찾는 알고리즘
- 대표적인 solver
    1) lbfgs: 일반적으로 많이 사용, L2 규제 지원
    2) liblinear : 작은 데이터셋에 적합, L1/L2 규제 지원
    3) saga : 대용량 데이터셋에 적합, L1/L2 규제 지원



'''

















































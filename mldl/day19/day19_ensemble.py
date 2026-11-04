#day19_ensemble
# 앙상블 간단 비교 : Voting,Bagging, Boosting

# 앙상블(ensemble) : 여러 개의 모델을 결합하여 하나의 최종 예측 결과를 만드는 방법 또는 기법
# 1) Voting : 여러 모델의 예측 결과를 가져와서 투표로 결정
# 2) Bagging : 여러 모델을 서로 다른 데이터(bootstrap)로 독립적으로 학습시킨 후 결과를 집계(결합)
# 3) Boosting : 이전 모델이 틀린 부분을 다음 모델이 보완하면서 순차적으로 학습

from sklearn.datasets import load_wine
from sklearn.ensemble import VotingClassifier, BaggingClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from util.print_util import pp, pt, up

# wine 분류 데이터셋
wine = load_wine(as_frame=True)
X = wine.data
y = wine.target

# train, test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42,stratify=y)

# Voting
tree = DecisionTreeClassifier(
    max_depth=3,
    random_state=42
)
logistic = LogisticRegression(
    max_iter= 5000)

voting = VotingClassifier(
    estimators=[ # 투표 참여 모델
        ('tree', tree),
        ('logistic', logistic),
    ], voting='hard' # 투표에 참여한 모델의 예측 클래스를 다수결로 결정
)

voting.fit(X_train, y_train) #학습
y_pred = voting.predict(X_test) # 예측

pp('[Voting]')
pp('정확도: ',round(accuracy_score(y_test,y_pred),3))

#Bagging
bagging = BaggingClassifier(
    estimator=DecisionTreeClassifier(max_depth=3),
    n_estimators=30, # decision tree 30개 생성
    bootstrap=True, # 원본 데이터를 복원 추출해서 서로 다른 학습데이터 생성
    random_state=42
)

bagging.fit(X_train, y_train)
bagging_pred = bagging.predict(X_test)

pp('[Bagging]')
pp('정확도:',round(accuracy_score(y_test,bagging_pred),3))

# Boosting
boosting = AdaBoostClassifier(
    estimator=DecisionTreeClassifier(max_depth=1),
    n_estimators=30, # 약한 Decision tree 최대 30개 사용
    learning_rate=0.1, # 각 모델의 학습 영향 정도
    random_state=42
)
boosting.fit(X_train, y_train)
boosting_pred = boosting.predict(X_test)
pp('[AdaBoost]')
pp('정확도 :',round(accuracy_score(y_test,boosting_pred),3))





















